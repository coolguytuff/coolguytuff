from __future__ import annotations

import math
from dataclasses import dataclass

from activity_world_model import Frame, RUNNER_FOOTLINE, fmt

THIGH_FAR = 50.0
SHIN_FAR = 44.0
FOOT_FAR = 11.0
THIGH_NEAR = 52.0
SHIN_NEAR = 46.0
FOOT_NEAR = 12.0


@dataclass(frozen=True)
class Pose:
    torso: float
    pelvis_y: float
    head: float
    shoulder_far: float
    elbow_far: float
    shoulder_near: float
    elbow_near: float
    hip_far: float
    knee_far: float
    hip_near: float
    knee_near: float
    fist_near_scale: float
    body_bob: float


def _lerp(a, b, p):
    return a + (b - a) * p


def pose_for(frame: Frame) -> Pose:
    p = max(0.0, min(1.0, frame.phase))
    if frame.state == 'sprint':
        s = math.sin(p * math.tau); c = math.cos(p * math.tau)
        return Pose(-12+3*c,1.5*abs(s),3-2.5*c,48*s-12,56+18*max(0,-s),-48*s+14,58+16*max(0,s),-40*s+5,26+46*max(0,s),40*s-5,26+46*max(0,-s),1.12+.17*max(0,-s),1.8*abs(s))
    if frame.state == 'jump':
        if p < .14:
            q=p/.14; return Pose(-9,5*q,3,-34,76,32,72,28,86,-24,84,1.22,4*q)
        if p < .46:
            q=(p-.14)/.32; return Pose(_lerp(-9,-2,q),_lerp(5,-4,q),_lerp(3,-4,q),_lerp(-34,-78,q),_lerp(76,24,q),_lerp(32,58,q),_lerp(72,28,q),_lerp(28,-24,q),_lerp(86,24,q),_lerp(-24,22,q),_lerp(84,30,q),1.30,_lerp(4,-3,q))
        if p < .78:
            q=(p-.46)/.32; return Pose(-2,-4,-4,-78,24,58,28,_lerp(-24,22,q),_lerp(24,66,q),_lerp(22,-14,q),_lerp(30,68,q),1.33,-3)
        q=(p-.78)/.22; return Pose(_lerp(-2,5,q),_lerp(-4,5,q),_lerp(-4,4,q),_lerp(-78,-24,q),_lerp(24,74,q),_lerp(58,20,q),_lerp(28,78,q),_lerp(22,26,q),_lerp(66,88,q),_lerp(-14,-24,q),_lerp(68,86,q),_lerp(1.33,1.20,q),_lerp(-3,5,q))
    if frame.state == 'climb':
        if p < .22:
            q=p/.22; return Pose(_lerp(-8,-16,q),1,_lerp(2,-6,q),_lerp(-6,-74,q),_lerp(58,18,q),_lerp(8,-105,q),_lerp(56,12,q),-8,54,12,48,_lerp(1.16,1.34,q),0)
        if p < .50:
            q=(p-.22)/.28; return Pose(-16,3+1.4*math.sin(q*math.pi),-6,-76,18,-108,10,-18,68,18,62,1.36,2)
        if p < .82:
            q=(p-.50)/.32; return Pose(_lerp(-16,-6,q),_lerp(3,0,q),_lerp(-6,1,q),_lerp(-76,-38,q),_lerp(18,90,q),_lerp(-108,-44,q),_lerp(10,92,q),_lerp(-18,24,q),_lerp(68,90,q),_lerp(18,-14,q),_lerp(62,94,q),_lerp(1.36,1.22,q),_lerp(2,0,q))
        q=(p-.82)/.18; return Pose(_lerp(-6,0,q),0,_lerp(1,0,q),_lerp(-38,0,q),_lerp(90,56,q),_lerp(-44,0,q),_lerp(92,56,q),_lerp(24,0,q),_lerp(90,24,q),_lerp(-14,0,q),_lerp(94,24,q),_lerp(1.22,1.16,q),0)
    if frame.state == 'turn':
        s=math.sin(p*math.pi); return Pose(20*s,2*s,-12*s,-28*s,66,36*s,68,24*s,74,-20*s,74,1.24,2*s)
    breathe=math.sin(frame.t*2) if frame.t else 0
    return Pose(0,0,-breathe,-7,58,7,58,-2,22,2,22,1.18,.45*breathe)


def _rot(name, frames, total, getter):
    keys=';'.join(fmt(f.t/total) for f in frames); vals=';'.join(f'{fmt(getter(pose_for(f)))} 0 0' for f in frames)
    return f'<animateTransform id="{name}" attributeName="transform" type="rotate" additive="sum" values="{vals}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>'


def _leg_foot_bottom(hip_deg:float,knee_deg:float,thigh:float,shin:float,foot:float)->float:
    hip=math.radians(hip_deg); shin_angle=math.radians(hip_deg+knee_deg)
    return thigh*math.cos(hip)+shin*math.cos(shin_angle)+foot


def _pose_foot_bottom(pose:Pose)->float:
    pelvis=pose.pelvis_y+pose.body_bob
    far=pelvis+_leg_foot_bottom(pose.hip_far,pose.knee_far,THIGH_FAR,SHIN_FAR,FOOT_FAR)
    near=pelvis+_leg_foot_bottom(pose.hip_near,pose.knee_near,THIGH_NEAR,SHIN_NEAR,FOOT_NEAR)
    return max(far,near)


def render_titan(frames:list[Frame],total:float)->str:
    keys=';'.join(fmt(f.t/total) for f in frames)
    pos=';'.join(f'{fmt(f.x)} {fmt(f.y-(_pose_foot_bottom(pose_for(f))-RUNNER_FOOTLINE))}' for f in frames)
    shadow_pos=';'.join(f'{fmt(f.x)} {fmt(f.y+RUNNER_FOOTLINE+7)}' for f in frames)
    scales=';'.join(f'{fmt(f.sx)} {fmt(f.sy)}' for f in frames); dirs=';'.join(f'{f.direction} 1' for f in frames)
    pelvis=';'.join(f'0 {fmt(pose_for(f).pelvis_y+pose_for(f).body_bob)}' for f in frames); fists=';'.join(f'{fmt(pose_for(f).fist_near_scale)} {fmt(pose_for(f).fist_near_scale)}' for f in frames)
    return f'''<!-- TITAN_BODY_DEPTH --><!-- TITAN_CONTINUOUS_RIG --><!-- TITAN_FOOT_CONTACT_CYCLE --><!-- HULK_MASS_SILHOUETTE --><!-- BRICK_STATE_JUMP --><!-- BRICK_STATE_CLIMB --><!-- BRICK_STATE_SPRINT --><!-- BRICK_STATE_TURN --><!-- BRICK_ROUTE_FORWARD --><!-- BRICK_ROUTE_REVERSE -->
<g id="titan-shadow-motion"><animateTransform attributeName="transform" type="translate" values="{shadow_pos}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><ellipse rx="64" ry="12" fill="#000" opacity=".46" filter="url(#blur4)"/></g>
<g id="titan-motion"><animateTransform attributeName="transform" type="translate" values="{pos}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="titan-direction"><animateTransform attributeName="transform" type="scale" calcMode="discrete" values="{dirs}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="titan-squash"><animateTransform attributeName="transform" type="scale" values="{scales}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="titan-pelvis"><animateTransform attributeName="transform" type="translate" values="{pelvis}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>
<g id="far-hip">{_rot('far-hip-anim',frames,total,lambda p:p.hip_far)}<path d="M-31 -9Q-18 -27 0 -9Q8 13 -4 38Q-11 54 -25 58Q-43 49 -42 25Q-42 2 -31 -9Z" fill="url(#greenFar)" stroke="#164c25" stroke-width="1.5"/><g transform="translate(-22 53)"><g>{_rot('far-knee-anim',frames,total,lambda p:p.knee_far)}<path d="M-14 -5Q3 -12 15 4L13 39Q8 53 -3 56Q-18 49 -19 34Z" fill="url(#greenFar)"/><path d="M-19 45Q1 36 25 45L33 56Q9 65 -18 58Z" fill="#172019" stroke="#61d777" stroke-opacity=".48"/></g></g></g>
<g id="far-shoulder" transform="translate(-67 -92)"><g>{_rot('far-shoulder-anim',frames,total,lambda p:p.shoulder_far)}<path d="M-28 -13Q-3 -36 23 -13Q38 10 20 37Q5 55 -17 42Q-40 21 -28 -13Z" fill="url(#greenFar)"/><path d="M-12 26Q7 17 20 32L17 66Q8 82 -8 72Q-23 56 -18 39Z" fill="url(#greenFar)"/><g transform="translate(2 77)"><g>{_rot('far-elbow-anim',frames,total,lambda p:p.elbow_far)}<path d="M-12 -7Q6 -13 17 4L15 46Q5 62 -10 52Q-20 34 -17 8Z" fill="url(#greenFar)"/><path d="M-21 43Q1 31 22 44Q28 62 6 72Q-18 66 -24 54Z" fill="url(#greenFar)"/></g></g></g></g>
<g id="titan-purple-shorts"><path d="M-46 -24Q0 -9 46 -24L50 10L35 25L20 16L8 29L-7 18L-22 27L-36 16L-52 9Z" fill="url(#shortsPurple)" stroke="#b995cb" stroke-opacity=".65" stroke-width="1.5"/><path d="M-43 7L-58 24L-32 16M44 7L59 22L32 16M-3 -9L2 15" fill="none" stroke="#d2aedf" stroke-width="2.2" opacity=".58"/></g>
<g id="near-hip">{_rot('near-hip-anim',frames,total,lambda p:p.hip_near)}<path d="M4 -10Q25 -29 43 -9Q52 15 39 41Q31 58 14 61Q-7 51 -6 27Q-5 3 4 -10Z" fill="url(#greenNear)" stroke="#baf9bf" stroke-opacity=".22" stroke-width="1.4"/><path d="M6 7Q28 0 42 14M3 33Q25 24 39 35" fill="none" stroke="#0a5a26" stroke-width="2" opacity=".72"/><g transform="translate(19 55)"><g>{_rot('near-knee-anim',frames,total,lambda p:p.knee_near)}<path d="M-15 -6Q5 -14 18 4L16 42Q9 58 -5 60Q-22 53 -22 32Z" fill="url(#greenNear)"/><path d="M-23 48Q1 38 29 48L38 61Q12 72 -23 64Z" fill="#151e19" stroke="#9affaa" stroke-opacity=".64" stroke-width="1.3"/></g></g></g>
<g id="titan-torso" transform="translate(0 -22)"><g>{_rot('torso-anim',frames,total,lambda p:p.torso)}<path d="M-86 -60Q-82 -103 -55 -121Q-35 -134 -16 -117Q0 -136 18 -117Q38 -135 58 -120Q83 -101 88 -59Q80 -19 48 0Q24 13 0 7Q-25 13 -50 0Q-81 -20 -86 -60Z" fill="url(#torsoGreen)" stroke="#caffce" stroke-opacity=".42" stroke-width="1.7" filter="url(#titanShadow)"/><g id="titan-traps"><path d="M-72 -94Q-51 -136 -12 -125L0 -104L12 -125Q52 -137 74 -92Q48 -84 27 -91Q12 -94 0 -84Q-13 -94 -28 -91Q-50 -83 -72 -94Z" fill="url(#trapGreen)"/></g><g id="titan-chest"><path d="M-67 -72Q-45 -100 -5 -83L-2 -45Q-36 -34 -65 -52Z" fill="url(#pecGreen)" stroke="#155f2b" stroke-opacity=".55"/><path d="M5 -83Q45 -100 68 -71L66 -51Q36 -34 2 -45Z" fill="url(#pecGreen)" stroke="#155f2b" stroke-opacity=".55"/><path d="M0 -81V-15M-54 -43Q-28 -27 -4 -35M54 -43Q28 -27 4 -35M-37 -23Q-18 -10 -3 -18M37 -23Q18 -10 3 -18" fill="none" stroke="#073b18" stroke-width="2.5" opacity=".78"/></g>
<path d="M-23 -114L-20 -141H21L24 -113Q9 -101 -23 -114Z" fill="url(#neckGreen)"/><g id="titan-head" transform="translate(0 -154)"><g>{_rot('head-anim',frames,total,lambda p:p.head)}<path id="titan-face" d="M-34 -20Q-32 -48 -9 -55Q18 -57 35 -36Q43 -11 35 22Q27 43 2 48Q-25 43 -36 22Q-44 0 -34 -20Z" fill="url(#faceGreen)" stroke="#d7ffda" stroke-opacity=".55" stroke-width="1.8"/><path id="titan-hair" d="M-35 -21L-47 -39L-32 -36L-38 -56L-21 -48L-13 -67L-2 -51L11 -68L18 -50L37 -61L32 -43L50 -46L36 -22L23 -30L12 -25L2 -32L-10 -24L-23 -31Z" fill="#070c0a"/><path id="titan-brow" d="M-30 -11Q-17 -25 -4 -12M5 -12Q20 -26 32 -9" fill="none" stroke="#062d13" stroke-width="5.5" stroke-linecap="round"/><path d="M-25 -5L-7 -1M7 -1L27 -6" stroke="#d8ffe0" stroke-width="3" stroke-linecap="round"/><circle cx="-12" cy="-3" r="2.6" fill="#07110a"/><circle cx="15" cy="-3" r="2.6" fill="#07110a"/><path d="M2 1L-3 12L6 14" fill="none" stroke="#17622d" stroke-width="2.6"/><path id="titan-jaw" d="M-29 17Q0 7 30 17L25 37Q2 51 -25 36Z" fill="#267e37" stroke="#0a421b" stroke-width="1.8"/><path d="M-21 23Q1 15 23 23L19 35Q0 41 -18 34Z" fill="#220b0c"/><path d="M-16 23H19L15 30H-12Z" fill="#f5efe3"/></g></g>
<g id="near-shoulder" transform="translate(72 -91)"><g>{_rot('near-shoulder-anim',frames,total,lambda p:p.shoulder_near)}<path d="M-35 -15Q-4 -42 30 -15Q49 11 29 44Q12 64 -15 50Q-47 26 -35 -15Z" fill="url(#greenNear)" stroke="#d6ffda" stroke-opacity=".35"/><path d="M-16 31Q9 17 26 36L22 76Q10 96 -10 82Q-29 62 -24 43Z" fill="url(#greenNear)"/><path d="M-13 39Q7 27 23 42M-17 64Q6 49 22 62" fill="none" stroke="#0b5c28" stroke-width="2.1" opacity=".75"/><g transform="translate(1 66)"><g>{_rot('near-elbow-anim',frames,total,lambda p:p.elbow_near)}<path d="M-18 -8Q5 -16 21 6L18 51Q7 71 -13 61Q-28 40 -24 11Z" fill="url(#greenNear)"/><g id="near-fist" transform="translate(0 58)"><animateTransform attributeName="transform" type="scale" additive="sum" values="{fists}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><path d="M-38 -23Q-9 -43 31 -21Q52 2 38 33Q15 55 -21 42Q-49 22 -38 -23Z" fill="url(#fistGreen)" stroke="#e0ffe2" stroke-opacity=".55" stroke-width="1.6"/><path d="M-27 -9Q-6 -17 26 -9M-30 4Q-6 -5 30 5M-23 18Q-2 10 24 18" stroke="#0a5423" stroke-width="2.2" fill="none" opacity=".78"/></g></g></g></g></g>
</g></g></g></g></g></g></g>'''
