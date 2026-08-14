from __future__ import annotations

import math
from dataclasses import dataclass
from activity_world_model import Frame, fmt

@dataclass(frozen=True)
class Pose:
    torso:float; pelvis_y:float; head:float
    shoulder_far:float; elbow_far:float; shoulder_near:float; elbow_near:float
    hip_far:float; knee_far:float; hip_near:float; knee_near:float
    fist_near_scale:float; body_bob:float

def _lerp(a,b,p): return a+(b-a)*p

def pose_for(frame:Frame)->Pose:
    p=max(0.0,min(1.0,frame.phase))
    if frame.state=='sprint':
        s=math.sin(p*math.tau); c=math.cos(p*math.tau)
        return Pose(-13+3*c,3.5*abs(s),7-2*c,42*s-10,48+20*max(0,-s),-42*s+12,52+18*max(0,s),-34*s+4,30+38*max(0,s),34*s-4,30+38*max(0,-s),1.08+.13*max(0,-s),2.5*abs(s))
    if frame.state=='jump':
        if p<.15:
            q=p/.15; return Pose(-7,8*q,4,-30,74,28,68,25,80,-22,78,1.18,6*q)
        if p<.45:
            q=(p-.15)/.30; return Pose(_lerp(-7,-3,q),_lerp(8,-2,q),_lerp(4,-2,q),_lerp(-30,-72,q),_lerp(74,26,q),_lerp(28,52,q),_lerp(68,34,q),_lerp(25,-20,q),_lerp(80,24,q),_lerp(-22,18,q),_lerp(78,28,q),1.25,_lerp(6,-2,q))
        if p<.78:
            q=(p-.45)/.33; return Pose(-3,-2,-2,-72,26,52,34,_lerp(-20,18,q),_lerp(24,62,q),_lerp(18,-12,q),_lerp(28,66,q),1.28,-2)
        q=(p-.78)/.22; return Pose(_lerp(-3,4,q),_lerp(-2,10,q),_lerp(-2,6,q),_lerp(-72,-20,q),_lerp(26,72,q),_lerp(52,18,q),_lerp(34,76,q),_lerp(18,22,q),_lerp(62,86,q),_lerp(-12,-20,q),_lerp(66,84,q),_lerp(1.28,1.18,q),_lerp(-2,8,q))
    if frame.state=='climb':
        if p<.20:
            q=p/.20; return Pose(_lerp(-8,-15,q),2,_lerp(4,-5,q),_lerp(0,-70,q),_lerp(60,18,q),_lerp(10,-98,q),_lerp(55,12,q),-8,52,12,45,_lerp(1.14,1.28,q),1)
        if p<.48:
            q=(p-.20)/.28; return Pose(-15,8+2*math.sin(q*math.pi),-5,-72,20,-102,10,-18,66,18,58,1.30,7)
        if p<.80:
            q=(p-.48)/.32; return Pose(_lerp(-15,-5,q),_lerp(8,1,q),_lerp(-5,1,q),_lerp(-72,-36,q),_lerp(20,88,q),_lerp(-102,-42,q),_lerp(10,92,q),_lerp(-18,22,q),_lerp(66,88,q),_lerp(18,-12,q),_lerp(58,92,q),_lerp(1.30,1.20,q),_lerp(7,1,q))
        q=(p-.80)/.20; return Pose(_lerp(-5,0,q),_lerp(1,0,q),_lerp(1,0,q),_lerp(-36,0,q),_lerp(88,55,q),_lerp(-42,0,q),_lerp(92,55,q),_lerp(22,0,q),_lerp(88,20,q),_lerp(-12,0,q),_lerp(92,20,q),_lerp(1.20,1.14,q),_lerp(1,0,q))
    if frame.state=='turn':
        s=math.sin(p*math.pi); return Pose(18*s,5*s,-12*s,-25*s,62,32*s,64,22*s,72,-18*s,72,1.20,4*s)
    breathe=math.sin(frame.t*2) if frame.t else 0
    return Pose(0,0,-breathe,-6,58,6,58,-2,22,2,22,1.16,.8*breathe)

def _rot(name,frames,total,getter):
    keys=';'.join(fmt(f.t/total) for f in frames); vals=';'.join(f'{fmt(getter(pose_for(f)))} 0 0' for f in frames)
    return f'<animateTransform id="{name}" attributeName="transform" type="rotate" values="{vals}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>'

def render_titan(frames:list[Frame],total:float)->str:
    keys=';'.join(fmt(f.t/total) for f in frames); pos=';'.join(f'{fmt(f.x)} {fmt(f.y)}' for f in frames); scales=';'.join(f'{fmt(f.sx)} {fmt(f.sy)}' for f in frames); dirs=';'.join(f'{f.direction} 1' for f in frames); pelvis=';'.join(f'0 {fmt(pose_for(f).pelvis_y+pose_for(f).body_bob)}' for f in frames); fists=';'.join(f'{fmt(pose_for(f).fist_near_scale)} {fmt(pose_for(f).fist_near_scale)}' for f in frames)
    return f'''<!-- TITAN_BODY_DEPTH --><!-- TITAN_CONTINUOUS_RIG --><!-- TITAN_FOOT_CONTACT_CYCLE --><!-- BRICK_STATE_JUMP --><!-- BRICK_STATE_CLIMB --><!-- BRICK_STATE_SPRINT --><!-- BRICK_STATE_TURN --><!-- BRICK_ROUTE_FORWARD --><!-- BRICK_ROUTE_REVERSE -->
<g id="titan-motion"><animateTransform attributeName="transform" type="translate" values="{pos}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="titan-direction"><animateTransform attributeName="transform" type="scale" calcMode="discrete" values="{dirs}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="titan-squash"><animateTransform attributeName="transform" type="scale" values="{scales}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><ellipse cx="0" cy="7" rx="58" ry="13" fill="#000" opacity=".40" filter="url(#blur4)"/><g id="titan-pelvis"><animateTransform attributeName="transform" type="translate" values="{pelvis}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>
<g id="far-hip">{_rot('far-hip-anim',frames,total,lambda p:p.hip_far)}<ellipse cx="-14" cy="-8" rx="19" ry="22" fill="url(#greenFar)"/><rect x="-22" y="-3" width="19" height="42" rx="9" fill="url(#greenFar)"/><g transform="translate(-13 34)">{_rot('far-knee-anim',frames,total,lambda p:p.knee_far)}<rect x="-9" width="18" height="39" rx="9" fill="url(#greenFar)"/><ellipse cx="3" cy="42" rx="23" ry="9" fill="#172019" stroke="#61d777" stroke-opacity=".45"/></g></g>
<g id="far-shoulder" transform="translate(-39 -72)">{_rot('far-shoulder-anim',frames,total,lambda p:p.shoulder_far)}<ellipse rx="24" ry="22" fill="url(#greenFar)"/><rect x="-11" y="-1" width="22" height="48" rx="11" fill="url(#greenFar)"/><g transform="translate(0 44)">{_rot('far-elbow-anim',frames,total,lambda p:p.elbow_far)}<rect x="-9" width="18" height="43" rx="9" fill="url(#greenFar)"/><ellipse cy="47" rx="17" ry="15" fill="url(#greenFar)"/></g></g>
<path d="M-29 -18Q0 -8 29 -18L32 10L17 18L5 11L-5 19L-18 12L-33 9Z" fill="url(#shortsPurple)" stroke="#b284c8" stroke-opacity=".5"/><path d="M-31 6L-40 16L-24 12M32 6L42 15L25 12" fill="none" stroke="#c297d6" stroke-width="2" opacity=".58"/>
<g id="near-hip">{_rot('near-hip-anim',frames,total,lambda p:p.hip_near)}<ellipse cx="15" cy="-8" rx="22" ry="24" fill="url(#greenNear)"/><rect x="5" y="-3" width="22" height="44" rx="11" fill="url(#greenNear)"/><g transform="translate(15 36)">{_rot('near-knee-anim',frames,total,lambda p:p.knee_near)}<rect x="-10" width="20" height="43" rx="10" fill="url(#greenNear)"/><ellipse cx="5" cy="46" rx="26" ry="10" fill="#151e19" stroke="#91ff9e" stroke-opacity=".58"/></g></g>
<g id="titan-torso" transform="translate(0 -16)">{_rot('torso-anim',frames,total,lambda p:p.torso)}<path d="M-60 -63Q-50 -105 -20 -112Q0 -124 20 -112Q50 -105 60 -63Q56 -25 32 -9Q0 6 -32 -9Q-56 -25 -60 -63Z" fill="url(#torsoGreen)" stroke="#c5ffca" stroke-opacity=".46" stroke-width="1.5" filter="url(#titanShadow)"/><ellipse cx="-29" cy="-90" rx="38" ry="24" fill="url(#trapGreen)" transform="rotate(17 -29 -90)"/><ellipse cx="29" cy="-90" rx="38" ry="24" fill="url(#trapGreen)" transform="rotate(-17 29 -90)"/><ellipse cx="-21" cy="-64" rx="28" ry="19" fill="url(#pecGreen)"/><ellipse cx="21" cy="-64" rx="28" ry="19" fill="url(#pecGreen)"/><path d="M0 -80V-22M-35 -39Q0 -23 35 -39M-23 -29Q0 -19 23 -29M-17 -18Q0 -11 17 -18" fill="none" stroke="#063b19" stroke-width="2.2" opacity=".7"/>
<path d="M-17 -101L-14 -124H14L18 -101Z" fill="url(#neckGreen)"/><g id="titan-head" transform="translate(0 -128)">{_rot('head-anim',frames,total,lambda p:p.head)}<path d="M-22 -8Q-18 -32 0 -35Q20 -31 24 -7L20 19Q6 30 -12 24Q-25 12 -22 -8Z" fill="url(#faceGreen)" stroke="#d0ffd4" stroke-opacity=".42"/><path d="M-21 -11L-29 -25L-17 -21L-20 -35L-7 -28L-2 -40L6 -28L15 -38L15 -26L27 -31L21 -13Q4 -22 -21 -11Z" fill="#0a100d"/><path d="M-18 -6L-5 -1M6 -1L20 -6" stroke="#062b13" stroke-width="3.5" stroke-linecap="round"/><circle cx="-6" cy="2" r="2.1" fill="#fff"/><circle cx="9" cy="2" r="2.1" fill="#fff"/><path d="M-10 13Q2 22 14 12" fill="none" stroke="#072813" stroke-width="3"/><path d="M-7 14L-3 18M2 18L7 17M10 14L14 16" stroke="#fff" stroke-width="1.8"/></g>
<g id="near-shoulder" transform="translate(45 -76)">{_rot('near-shoulder-anim',frames,total,lambda p:p.shoulder_near)}<ellipse rx="29" ry="26" fill="url(#greenNear)" stroke="#d2ffd5" stroke-opacity=".43"/><rect x="-13" y="-1" width="26" height="52" rx="13" fill="url(#greenNear)"/><g transform="translate(0 48)">{_rot('near-elbow-anim',frames,total,lambda p:p.elbow_near)}<rect x="-12" width="24" height="48" rx="12" fill="url(#greenNear)"/><g id="near-fist" transform="translate(0 54)"><animateTransform attributeName="transform" type="scale" additive="sum" values="{fists}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><ellipse rx="27" ry="23" fill="url(#fistGreen)" stroke="#ddffdf" stroke-opacity=".52"/><path d="M-17 -8H17M-14 0H18M-10 9H13" stroke="#09491f" stroke-width="1.9" opacity=".7"/></g></g></g></g></g></g></g></g>'''
