from __future__ import annotations

import math
from collections import defaultdict
from activity_world_model import BASE_Y, Cell, build_frames, camera_values, classify_steps, fmt, group_weeks, position
from activity_world_titan import render_titan

LEVEL_TOP={0:'#193149',1:'#145b58',2:'#137f85',3:'#2d67d6',4:'#8548cc'}
LEVEL_FRONT={0:'#07131f',1:'#0a3434',2:'#0c4b52',3:'#193b82',4:'#432469'}
LEVEL_SIDE={0:'#040b13',1:'#072323',2:'#08333a',3:'#10285b',4:'#2d194c'}
DAY_COLORS={0:'#1f2f40',1:'#1f7a6d',2:'#26a899',3:'#5c8cff',4:'#d08cff'}
TOWER_WIDTH=46.0; TOWER_DEPTH=24.0

def _spring_response(dt:float,amplitude:float,kind:str):
    if dt<0 or dt>1.10: return 0.0,1.0,1.0,0.0
    if kind=='hands': omega,damping,phase=13.0,4.8,-.4
    elif kind=='foot': omega,damping,phase=18.0,6.5,0.0
    else: omega,damping,phase=14.5,4.2,0.0
    wave=math.exp(-damping*dt)*math.sin(omega*dt+phase); compress=max(0.0,math.exp(-7*dt)*math.cos(omega*.65*dt))
    dy=amplitude*(.58*wave+.48*compress); sy=1-min(.17,amplitude*.014)*compress+min(.055,amplitude*.004)*wave; sx=1+(1-sy)*.82-.012*wave; tilt=amplitude*.13*math.exp(-5.2*dt)*math.sin(omega*.85*dt)
    return dy,sx,sy,tilt

def _physics_frames(events,total):
    moments={0.0,total}
    for when,_,_ in events:
        for d in (-.05,0,.045,.09,.15,.23,.34,.48,.66,.88,1.08): moments.add(max(0,min(total,when+d)))
    vals=[]
    for t in sorted(moments):
        dy=tilt=0.0; sx=sy=1.0
        for when,amp,kind in events:
            ddy,ssx,ssy,tt=_spring_response(t-when,amp,kind); dy+=ddy; sx+=ssx-1; sy+=ssy-1; tilt+=tt
        vals.append((t,max(-10,min(12,dy)),max(.88,min(1.18,sx)),max(.80,min(1.12,sy)),max(-3.2,min(3.2,tilt))))
    keys=';'.join(fmt(t/total) for t,*_ in vals); trans=';'.join(f'0 {fmt(dy)}' for _,dy,_,_,_ in vals); scales=';'.join(f'{fmt(sx)} {fmt(sy)}' for _,_,sx,sy,_ in vals); tilts=';'.join(f'{fmt(r)} 0 0' for *_,r in vals)
    return keys,trans,scales,tilts

def _ripples(index,x,top_abs,events,total):
    if not events:return ''
    moments={0.0,total}
    for when,_,_ in events:
        for d in (0,.08,.18,.32,.48): moments.add(max(0,min(total,when+d)))
    ordered=sorted(moments); keys=';'.join(fmt(t/total) for t in ordered); op=[]; sc=[]
    for t in ordered:
        o=0;s=1
        for when,amp,_ in events:
            dt=t-when
            if 0<=dt<=.48: o=max(o,max(0,1-dt/.48)*min(.55,.18+amp*.04)); s=max(s,1+dt*5)
        op.append(fmt(o)); sc.append(f'{fmt(s)} {fmt(s)}')
    return f'<g id="impact-ripple-{index}" transform="translate({fmt(x)} {fmt(top_abs-2)})"><animate attributeName="opacity" values="{";".join(op)}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="scale" additive="sum" values="{";".join(sc)}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><ellipse rx="22" ry="7" fill="none" stroke="#b7ffff" stroke-width="1.3" opacity=".7"/></g>'

def _tower(index,week,count,events,total):
    x,top_abs=position(index,week,count); top=top_abs-BASE_Y; level=week.terrain_level; half=TOWER_WIDTH/2; depth=TOWER_DEPTH; keys,trans,scales,tilts=_physics_frames(events,total)
    shadow=f'M{-half+depth*.2} 6 L{half+depth*1.35} 6 L{half+depth*2.2} {-depth*.76} L{-half+depth*.7} {-depth*.76} Z'; front=f'{-half},{top} {half},{top} {half},0 {-half},0'; side=f'{half},{top} {half+depth},{top-depth} {half+depth},{-depth} {half},0'; topface=f'{-half},{top} {half},{top} {half+depth},{top-depth} {-half+depth},{top-depth}'
    studs=[]; levels=week.levels or (0,)
    for day,day_level in enumerate(levels[:7]):
        px=-half+4+day*(max(1,TOWER_WIDTH-8)/max(1,min(6,len(levels)-1))); py=top-depth*.43-(day%2)*.55; studs.append(f'<ellipse cx="{fmt(px+depth*.38)}" cy="{fmt(py)}" rx="2.7" ry="1.5" fill="{DAY_COLORS.get(day_level,DAY_COLORS[0])}" stroke="#e6ffff" stroke-opacity=".28"/>')
    return f'<g id="tower-{index}" transform="translate({fmt(x)} {fmt(BASE_Y)})"><g><animateTransform attributeName="transform" type="translate" values="{trans}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g><animateTransform attributeName="transform" type="rotate" values="{tilts}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="tower-jello-{index}"><animateTransform attributeName="transform" type="scale" values="{scales}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><path d="{shadow}" fill="#000" opacity=".26" filter="url(#blur4)"/><!-- TOWER_FRONT_FACE --><polygon points="{front}" fill="{LEVEL_FRONT[level]}" stroke="#4d6f8d" stroke-opacity=".32"/><!-- TOWER_SIDE_FACE --><polygon points="{side}" fill="{LEVEL_SIDE[level]}" stroke="#34506d" stroke-opacity=".30"/><!-- TOWER_TOP_FACE --><polygon points="{topface}" fill="{LEVEL_TOP[level]}" stroke="#c8fdff" stroke-opacity=".48" stroke-width="1.1"/>{"".join(studs)}</g></g></g></g>{_ripples(index,x,top_abs,events,total)}'

def _defs():
    return '''<defs><linearGradient id="worldBg"><stop stop-color="#01040a"/><stop offset="1" stop-color="#06101c"/></linearGradient><radialGradient id="greenNear"><stop stop-color="#d9ffdc"/><stop offset=".5" stop-color="#2bae46"/><stop offset="1" stop-color="#062f15"/></radialGradient><radialGradient id="greenFar"><stop stop-color="#95ef9b"/><stop offset="1" stop-color="#0a3d1e"/></radialGradient><radialGradient id="torsoGreen"><stop stop-color="#b6ffbb"/><stop offset=".52" stop-color="#249b40"/><stop offset="1" stop-color="#062c17"/></radialGradient><radialGradient id="trapGreen"><stop stop-color="#bbffc0"/><stop offset="1" stop-color="#0b4822"/></radialGradient><radialGradient id="pecGreen"><stop stop-color="#9dffa5"/><stop offset="1" stop-color="#135526"/></radialGradient><radialGradient id="faceGreen"><stop stop-color="#9df7a4"/><stop offset="1" stop-color="#0b4821"/></radialGradient><linearGradient id="neckGreen"><stop stop-color="#66dd70"/><stop offset="1" stop-color="#125126"/></linearGradient><radialGradient id="fistGreen"><stop stop-color="#c0ffc3"/><stop offset="1" stop-color="#0a4720"/></radialGradient><linearGradient id="shortsPurple"><stop stop-color="#6b3f82"/><stop offset=".48" stop-color="#42204f"/><stop offset="1" stop-color="#211128"/></linearGradient><filter id="titanShadow"><feDropShadow dx="0" dy="5" stdDeviation="4" flood-color="#000" flood-opacity=".48"/></filter><filter id="blur4"><feGaussianBlur stdDeviation="4"/></filter><pattern id="deck" width="72" height="28" patternUnits="userSpaceOnUse"><path d="M0 28L36 0L72 28M36 0V56" fill="none" stroke="#72a7ff" stroke-opacity=".045"/></pattern></defs>'''

def render_activity_world(cells:list[Cell])->str:
    weeks=group_weeks(cells)
    if len(weeks)<2: raise ValueError('activity world requires at least two week columns')
    frames,arrivals=build_frames(weeks); total=frames[-1].t; keys=';'.join(fmt(f.t/total) for f in frames); camera=camera_values(frames,len(weeks)); reactive=defaultdict(list)
    for index,events in arrivals.items():
        reactive[index].extend(events)
        for dist,factor,delay in ((1,.34,.055),(2,.14,.10)):
            for neighbor in (index-dist,index+dist):
                if 0<=neighbor<len(weeks): reactive[neighbor].extend((moment+delay,amp*factor,kind) for moment,amp,kind in events)
    towers=''.join(_tower(i,w,len(weeks),reactive.get(i,[]),total) for i,w in enumerate(weeks)); states=classify_steps([w.height for w in weeks])+classify_steps([w.height for w in reversed(weeks)]); counts={s:states.count(s) for s in ('jump','climb','sprint')}
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 820" role="img" aria-label="Cinematic 3D contribution activity world with TITAN traversing real GitHub activity terrain">{_defs()}<rect width="1600" height="820" rx="26" fill="url(#worldBg)"/><rect y="392" width="1600" height="428" fill="url(#deck)"/><text x="62" y="62" fill="#e2fcff" font-size="20" font-weight="700">ACTIVITY WORLD // TITAN RUN</text><text x="62" y="90" fill="#70869b" font-size="11">CONTINUOUS SKELETAL RIG → CONTACT-AWARE MOTION → SPRING-MASS JELLO TERRAIN</text><text x="1538" y="90" text-anchor="end" fill="#6ee7b7" font-size="10">JUMP {counts['jump']:02d} // CLIMB {counts['climb']:02d} // SPRINT {counts['sprint']:02d}</text><g id="camera-follow"><animateTransform attributeName="transform" type="translate" values="{camera}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="terrain"><!-- COLUMN_SETTLE --><!-- JELLO_SPRING_PHYSICS -->{towers}</g>{render_titan(frames,total)}</g><rect x="57" y="731" width="1486" height="52" rx="13" fill="#07111f" fill-opacity=".72"/><text x="80" y="762" fill="#d1edf2" font-size="11">run → articulated stride  //  jump → crouch + flight + brace  //  climb → reach + hang + pull + plant  //  impact → spring decay + neighbor wave</text></svg>'''
