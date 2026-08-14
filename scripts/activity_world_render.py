from __future__ import annotations

import math
from collections import defaultdict

from activity_world_model import BASE_Y, Cell, build_frames, camera_values, classify_steps, fmt, group_weeks, position
from activity_world_titan import render_titan

LEVEL_TOP={0:'#193149',1:'#145b58',2:'#137f85',3:'#2d67d6',4:'#8548cc'}
LEVEL_FRONT={0:'#07131f',1:'#0a3434',2:'#0c4b52',3:'#193b82',4:'#432469'}
LEVEL_SIDE={0:'#040b13',1:'#072323',2:'#08333a',3:'#10285b',4:'#2d194c'}
DAY_COLORS={0:'#1f2f40',1:'#1f7a6d',2:'#26a899',3:'#5c8cff',4:'#d08cff'}
TOWER_WIDTH=46.0
TOWER_DEPTH=24.0


def _spring_response(dt:float, amplitude:float, kind:str):
    """Underdamped spring response for contribution towers.

    `feet` is the heavy jump-landing profile, `foot` is a quick sprint footfall,
    and `hands` is a softer ledge tug. All profiles settle exactly to identity.
    """
    if dt < 0 or dt > 1.65:
        return 0.0,1.0,1.0,0.0

    if kind == 'feet':
        omega,damping,compression_decay,depth_cap,depth_gain = 15.8,2.65,5.6,.36,.038
        wave_gain,micro_gain,down_gain,tilt_gain = .92,.22,1.05,.22
    elif kind == 'foot':
        omega,damping,compression_decay,depth_cap,depth_gain = 20.5,4.9,8.2,.16,.026
        wave_gain,micro_gain,down_gain,tilt_gain = .54,.10,.58,.12
    elif kind == 'hands':
        omega,damping,compression_decay,depth_cap,depth_gain = 12.4,3.25,6.4,.24,.032
        wave_gain,micro_gain,down_gain,tilt_gain = .68,.15,.72,.17
    else:
        omega,damping,compression_decay,depth_cap,depth_gain = 14.2,3.7,7.0,.20,.028
        wave_gain,micro_gain,down_gain,tilt_gain = .62,.12,.64,.14

    spring = math.exp(-damping*dt)*math.sin(omega*dt)
    micro = math.exp(-(damping+1.5)*dt)*math.sin(omega*1.92*dt + .25)
    compression = math.exp(-compression_decay*dt)*max(0.0, math.cos(omega*.45*dt))

    depth = min(depth_cap, amplitude*depth_gain)
    sy = 1.0 - depth*compression + min(.14,depth*.48)*spring + .018*micro
    # Volume-ish preservation: the tower bulges outward when it squashes.
    sx = 1.0 + (1.0-sy)*1.16 + min(.07,amplitude*.006)*spring + .012*micro
    dy = amplitude*(down_gain*compression + wave_gain*spring + micro_gain*micro)
    tilt = amplitude*tilt_gain*math.exp(-(damping+.8)*dt)*math.sin(omega*.78*dt)
    return dy,sx,sy,tilt


def _lateral_shake(dt:float, amplitude:float, kind:str)->float:
    if dt < 0 or dt > 1.45:
        return 0.0
    gain = .34 if kind == 'feet' else .14 if kind == 'foot' else .22 if kind == 'hands' else .18
    damping = 3.1 if kind == 'feet' else 5.2 if kind == 'foot' else 3.8
    return amplitude*gain*math.exp(-damping*dt)*math.sin(24.0*dt + .4)


def _physics_frames(events,total):
    moments={0.0,total}
    for when,_,_ in events:
        for d in (-.05,0,.035,.07,.11,.16,.23,.32,.44,.58,.75,.95,1.18,1.42,1.64):
            moments.add(max(0,min(total,when+d)))
    vals=[]
    for t in sorted(moments):
        dx=dy=tilt=0.0
        sx=sy=1.0
        for when,amp,kind in events:
            dt=t-when
            ddy,ssx,ssy,tt=_spring_response(dt,amp,kind)
            dx += _lateral_shake(dt,amp,kind)
            dy += ddy
            sx += ssx-1
            sy += ssy-1
            tilt += tt
        vals.append((
            t,
            max(-11,min(11,dx)),
            max(-24,min(32,dy)),
            max(.78,min(1.42,sx)),
            max(.56,min(1.22,sy)),
            max(-6.0,min(6.0,tilt)),
        ))
    keys=';'.join(fmt(t/total) for t,*_ in vals)
    trans=';'.join(f'{fmt(dx)} {fmt(dy)}' for _,dx,dy,_,_,_ in vals)
    scales=';'.join(f'{fmt(sx)} {fmt(sy)}' for _,_,_,sx,sy,_ in vals)
    tilts=';'.join(f'{fmt(r)} 0 0' for *_,r in vals)
    return keys,trans,scales,tilts


def _ripples(index,x,top_abs,events,total):
    if not events:
        return ''
    moments={0.0,total}
    for when,_,_ in events:
        for d in (0,.06,.13,.22,.34,.48,.66):
            moments.add(max(0,min(total,when+d)))
    ordered=sorted(moments)
    keys=';'.join(fmt(t/total) for t in ordered)
    op=[]; sc=[]
    for t in ordered:
        o=0.0; s=1.0
        for when,amp,kind in events:
            dt=t-when
            if 0<=dt<=.66:
                strength=min(.72,.22+amp*.052) if kind=='feet' else min(.52,.15+amp*.038)
                o=max(o,max(0,1-dt/.66)*strength)
                s=max(s,1+dt*(6.2 if kind=='feet' else 4.8))
        op.append(fmt(o)); sc.append(f'{fmt(s)} {fmt(s)}')
    return f'''<g id="impact-ripple-{index}" transform="translate({fmt(x)} {fmt(top_abs-2)})">
      <animate attributeName="opacity" values="{";".join(op)}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>
      <animateTransform attributeName="transform" type="scale" additive="sum" values="{";".join(sc)}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>
      <ellipse rx="22" ry="7" fill="none" stroke="#c9ffff" stroke-width="1.5" opacity=".78"/>
      <ellipse rx="14" ry="4.5" fill="none" stroke="#77fff1" stroke-width="1" opacity=".5"/>
    </g>'''


def _tower(index,week,count,events,total):
    x,top_abs=position(index,week,count)
    top=top_abs-BASE_Y
    level=week.terrain_level
    half=TOWER_WIDTH/2
    depth=TOWER_DEPTH
    keys,trans,scales,tilts=_physics_frames(events,total)
    shadow=f'M{-half+depth*.2} 6 L{half+depth*1.35} 6 L{half+depth*2.2} {-depth*.76} L{-half+depth*.7} {-depth*.76} Z'
    front=f'{-half},{top} {half},{top} {half},0 {-half},0'
    side=f'{half},{top} {half+depth},{top-depth} {half+depth},{-depth} {half},0'
    topface=f'{-half},{top} {half},{top} {half+depth},{top-depth} {-half+depth},{top-depth}'
    studs=[]
    levels=week.levels or (0,)
    for day,day_level in enumerate(levels[:7]):
        px=-half+4+day*(max(1,TOWER_WIDTH-8)/max(1,min(6,len(levels)-1)))
        py=top-depth*.43-(day%2)*.55
        studs.append(f'<ellipse cx="{fmt(px+depth*.38)}" cy="{fmt(py)}" rx="2.7" ry="1.5" fill="{DAY_COLORS.get(day_level,DAY_COLORS[0])}" stroke="#e6ffff" stroke-opacity=".28"/>')
    return f'''<g id="tower-{index}" transform="translate({fmt(x)} {fmt(BASE_Y)})"><g>
      <animateTransform attributeName="transform" type="translate" values="{trans}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>
      <g><animateTransform attributeName="transform" type="rotate" values="{tilts}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>
        <g id="tower-jello-{index}"><animateTransform attributeName="transform" type="scale" values="{scales}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>
          <path d="{shadow}" fill="#000" opacity=".30" filter="url(#blur4)"/>
          <!-- TOWER_FRONT_FACE --><polygon points="{front}" fill="{LEVEL_FRONT[level]}" stroke="#4d6f8d" stroke-opacity=".36"/>
          <!-- TOWER_SIDE_FACE --><polygon points="{side}" fill="{LEVEL_SIDE[level]}" stroke="#34506d" stroke-opacity=".34"/>
          <!-- TOWER_TOP_FACE --><polygon points="{topface}" fill="{LEVEL_TOP[level]}" stroke="#d7ffff" stroke-opacity=".58" stroke-width="1.2"/>
          <path d="M{-half+3},{top+3} L{half-3},{top+3}" stroke="#9cfff5" stroke-opacity=".16" stroke-width="2"/>
          {"".join(studs)}
        </g>
      </g>
    </g></g>{_ripples(index,x,top_abs,events,total)}'''


def _defs():
    return '''<defs>
      <linearGradient id="worldBg"><stop stop-color="#01040a"/><stop offset="1" stop-color="#06101c"/></linearGradient>
      <radialGradient id="greenNear" cx="34%" cy="22%"><stop stop-color="#e2ffe4"/><stop offset=".28" stop-color="#64dd70"/><stop offset=".67" stop-color="#24923d"/><stop offset="1" stop-color="#052a13"/></radialGradient>
      <radialGradient id="greenFar" cx="36%" cy="24%"><stop stop-color="#a5f6ac"/><stop offset=".55" stop-color="#2e9c43"/><stop offset="1" stop-color="#082d17"/></radialGradient>
      <radialGradient id="torsoGreen" cx="40%" cy="22%"><stop stop-color="#caffcd"/><stop offset=".30" stop-color="#63d96d"/><stop offset=".66" stop-color="#238c3b"/><stop offset="1" stop-color="#052712"/></radialGradient>
      <radialGradient id="trapGreen" cx="45%" cy="24%"><stop stop-color="#baffc0"/><stop offset=".58" stop-color="#3fb653"/><stop offset="1" stop-color="#083419"/></radialGradient>
      <radialGradient id="pecGreen" cx="38%" cy="28%"><stop stop-color="#adffb4"/><stop offset=".52" stop-color="#45bd58"/><stop offset="1" stop-color="#0d4821"/></radialGradient>
      <radialGradient id="faceGreen" cx="38%" cy="28%"><stop stop-color="#b9ffbe"/><stop offset=".45" stop-color="#53c861"/><stop offset="1" stop-color="#0a3a1b"/></radialGradient>
      <linearGradient id="neckGreen"><stop stop-color="#65d96e"/><stop offset="1" stop-color="#124a23"/></linearGradient>
      <radialGradient id="fistGreen" cx="32%" cy="25%"><stop stop-color="#d2ffd5"/><stop offset=".36" stop-color="#68d971"/><stop offset=".76" stop-color="#238d3b"/><stop offset="1" stop-color="#073018"/></radialGradient>
      <linearGradient id="shortsPurple"><stop stop-color="#80509a"/><stop offset=".42" stop-color="#512b63"/><stop offset="1" stop-color="#24122b"/></linearGradient>
      <filter id="titanShadow"><feDropShadow dx="0" dy="5" stdDeviation="4" flood-color="#000" flood-opacity=".52"/></filter>
      <filter id="blur4"><feGaussianBlur stdDeviation="4"/></filter>
      <pattern id="deck" width="72" height="28" patternUnits="userSpaceOnUse"><path d="M0 28L36 0L72 28M36 0V56" fill="none" stroke="#72a7ff" stroke-opacity=".045"/></pattern>
    </defs>'''


def render_activity_world(cells:list[Cell])->str:
    weeks=group_weeks(cells)
    if len(weeks)<2:
        raise ValueError('activity world requires at least two week columns')
    frames,arrivals=build_frames(weeks)
    total=frames[-1].t
    keys=';'.join(fmt(f.t/total) for f in frames)
    camera=camera_values(frames,len(weeks))
    reactive=defaultdict(list)
    for index,events in arrivals.items():
        reactive[index].extend(events)
        for dist,factor,delay in ((1,.52,.06),(2,.26,.12),(3,.11,.18)):
            for neighbor in (index-dist,index+dist):
                if 0<=neighbor<len(weeks):
                    reactive[neighbor].extend((moment+delay,amp*factor,kind) for moment,amp,kind in events)
    towers=''.join(_tower(i,w,len(weeks),reactive.get(i,[]),total) for i,w in enumerate(weeks))
    states=classify_steps([w.height for w in weeks])+classify_steps([w.height for w in reversed(weeks)])
    counts={s:states.count(s) for s in ('jump','climb','sprint')}
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 820" role="img" aria-label="Cinematic 3D contribution activity world with a massive green comic powerhouse traversing real GitHub activity terrain">{_defs()}
      <rect width="1600" height="820" rx="26" fill="url(#worldBg)"/>
      <rect y="392" width="1600" height="428" fill="url(#deck)"/>
      <text x="62" y="62" fill="#e2fcff" font-size="20" font-weight="700">ACTIVITY WORLD // TITAN RUN</text>
      <text x="62" y="90" fill="#70869b" font-size="11">FOOT-PLANE CONTACT → ARTICULATED POWERHOUSE RIG → DEEP SPRING-MASS JELLO TERRAIN</text>
      <text x="1538" y="90" text-anchor="end" fill="#6ee7b7" font-size="10">JUMP {counts['jump']:02d} // CLIMB {counts['climb']:02d} // SPRINT {counts['sprint']:02d}</text>
      <g id="camera-follow"><animateTransform attributeName="transform" type="translate" values="{camera}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>
        <g id="terrain"><!-- COLUMN_SETTLE --><!-- JELLO_SPRING_PHYSICS -->{towers}</g>
        {render_titan(frames,total)}
      </g>
      <rect x="57" y="731" width="1486" height="52" rx="13" fill="#07111f" fill-opacity=".72"/>
      <text x="80" y="762" fill="#d1edf2" font-size="11">run → true stride  //  jump → crouch + flight + heavy brace  //  climb → grab + pull + plant  //  impact → deep squash + lateral shake + rebound + neighbor wave</text>
    </svg>'''
