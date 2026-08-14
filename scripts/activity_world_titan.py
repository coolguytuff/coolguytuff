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
        s = math.sin(p * math.tau)
        c = math.cos(p * math.tau)
        return Pose(
            -12 + 3 * c,
            1.5 * abs(s),
            3 - 2.5 * c,
            48 * s - 12,
            56 + 18 * max(0, -s),
            -48 * s + 14,
            58 + 16 * max(0, s),
            -40 * s + 5,
            26 + 46 * max(0, s),
            40 * s - 5,
            26 + 46 * max(0, -s),
            1.12 + .17 * max(0, -s),
            1.8 * abs(s),
        )
    if frame.state == 'jump':
        if p < .14:
            q = p / .14
            return Pose(-9, 5 * q, 3, -34, 76, 32, 72, 28, 86, -24, 84, 1.22, 4 * q)
        if p < .46:
            q = (p - .14) / .32
            return Pose(
                _lerp(-9, -2, q), _lerp(5, -4, q), _lerp(3, -4, q),
                _lerp(-34, -78, q), _lerp(76, 24, q),
                _lerp(32, 58, q), _lerp(72, 28, q),
                _lerp(28, -24, q), _lerp(86, 24, q),
                _lerp(-24, 22, q), _lerp(84, 30, q), 1.30, _lerp(4, -3, q),
            )
        if p < .78:
            q = (p - .46) / .32
            return Pose(-2, -4, -4, -78, 24, 58, 28,
                        _lerp(-24, 22, q), _lerp(24, 66, q),
                        _lerp(22, -14, q), _lerp(30, 68, q), 1.33, -3)
        q = (p - .78) / .22
        return Pose(
            _lerp(-2, 5, q), _lerp(-4, 5, q), _lerp(-4, 4, q),
            _lerp(-78, -24, q), _lerp(24, 74, q),
            _lerp(58, 20, q), _lerp(28, 78, q),
            _lerp(22, 26, q), _lerp(66, 88, q),
            _lerp(-14, -24, q), _lerp(68, 86, q),
            _lerp(1.33, 1.20, q), _lerp(-3, 5, q),
        )
    if frame.state == 'climb':
        if p < .22:
            q = p / .22
            return Pose(_lerp(-8, -16, q), 1, _lerp(2, -6, q),
                        _lerp(-6, -74, q), _lerp(58, 18, q),
                        _lerp(8, -105, q), _lerp(56, 12, q),
                        -8, 54, 12, 48, _lerp(1.16, 1.34, q), 0)
        if p < .50:
            q = (p - .22) / .28
            return Pose(-16, 3 + 1.4 * math.sin(q * math.pi), -6,
                        -76, 18, -108, 10, -18, 68, 18, 62, 1.36, 2)
        if p < .82:
            q = (p - .50) / .32
            return Pose(_lerp(-16, -6, q), _lerp(3, 0, q), _lerp(-6, 1, q),
                        _lerp(-76, -38, q), _lerp(18, 90, q),
                        _lerp(-108, -44, q), _lerp(10, 92, q),
                        _lerp(-18, 24, q), _lerp(68, 90, q),
                        _lerp(18, -14, q), _lerp(62, 94, q),
                        _lerp(1.36, 1.22, q), _lerp(2, 0, q))
        q = (p - .82) / .18
        return Pose(_lerp(-6, 0, q), 0, _lerp(1, 0, q),
                    _lerp(-38, 0, q), _lerp(90, 56, q),
                    _lerp(-44, 0, q), _lerp(92, 56, q),
                    _lerp(24, 0, q), _lerp(90, 24, q),
                    _lerp(-14, 0, q), _lerp(94, 24, q),
                    _lerp(1.22, 1.16, q), 0)
    if frame.state == 'turn':
        s = math.sin(p * math.pi)
        return Pose(20 * s, 2 * s, -12 * s, -28 * s, 66, 36 * s, 68, 24 * s, 74, -20 * s, 74, 1.24, 2 * s)
    breathe = math.sin(frame.t * 2) if frame.t else 0
    return Pose(0, 0, -breathe, -7, 58, 7, 58, -2, 22, 2, 22, 1.18, .45 * breathe)


def _rot(name, frames, total, getter):
    keys = ';'.join(fmt(f.t / total) for f in frames)
    vals = ';'.join(f'{fmt(getter(pose_for(f)))} 0 0' for f in frames)
    # additive=sum is essential: these animated rotations sit inside translated
    # joint groups and must not replace their static joint placement.
    return (
        f'<animateTransform id="{name}" attributeName="transform" type="rotate" '
        f'additive="sum" values="{vals}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>'
    )


def _leg_foot_bottom(hip_deg: float, knee_deg: float, thigh: float, shin: float, foot: float) -> float:
    hip = math.radians(hip_deg)
    shin_angle = math.radians(hip_deg + knee_deg)
    return thigh * math.cos(hip) + shin * math.cos(shin_angle) + foot


def _pose_foot_bottom(pose: Pose) -> float:
    pelvis = pose.pelvis_y + pose.body_bob
    far = pelvis + _leg_foot_bottom(pose.hip_far, pose.knee_far, THIGH_FAR, SHIN_FAR, FOOT_FAR)
    near = pelvis + _leg_foot_bottom(pose.hip_near, pose.knee_near, THIGH_NEAR, SHIN_NEAR, FOOT_NEAR)
    return max(far, near)


def render_titan(frames: list[Frame], total: float) -> str:
    keys = ';'.join(fmt(f.t / total) for f in frames)
    # Frame.y + RUNNER_FOOTLINE is the intended contact plane. Pose-specific
    # compensation keeps the lowest foot on/above that plane throughout the rig.
    pos = ';'.join(
        f'{fmt(f.x)} {fmt(f.y - (_pose_foot_bottom(pose_for(f)) - RUNNER_FOOTLINE))}'
        for f in frames
    )
    shadow_pos = ';'.join(f'{fmt(f.x)} {fmt(f.y + RUNNER_FOOTLINE + 7)}' for f in frames)
    scales = ';'.join(f'{fmt(f.sx)} {fmt(f.sy)}' for f in frames)
    dirs = ';'.join(f'{f.direction} 1' for f in frames)
    pelvis = ';'.join(f'0 {fmt(pose_for(f).pelvis_y + pose_for(f).body_bob)}' for f in frames)
    fists = ';'.join(f'{fmt(pose_for(f).fist_near_scale)} {fmt(pose_for(f).fist_near_scale)}' for f in frames)

    return f'''<!-- TITAN_BODY_DEPTH --><!-- TITAN_CONTINUOUS_RIG --><!-- TITAN_FOOT_CONTACT_CYCLE --><!-- HULK_MASS_SILHOUETTE --><!-- BRICK_STATE_JUMP --><!-- BRICK_STATE_CLIMB --><!-- BRICK_STATE_SPRINT --><!-- BRICK_STATE_TURN --><!-- BRICK_ROUTE_FORWARD --><!-- BRICK_ROUTE_REVERSE -->
<g id="titan-shadow-motion"><animateTransform attributeName="transform" type="translate" values="{shadow_pos}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><ellipse cx="0" cy="0" rx="64" ry="12" fill="#000" opacity=".46" filter="url(#blur4)"/></g>
<g id="titan-motion"><animateTransform attributeName="transform" type="translate" values="{pos}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="titan-direction"><animateTransform attributeName="transform" type="scale" calcMode="discrete" values="{dirs}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="titan-squash"><animateTransform attributeName="transform" type="scale" values="{scales}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="titan-pelvis"><animateTransform attributeName="transform" type="translate" values="{pelvis}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>

<!-- FAR LEG: deeper, darker limb for 2.5D depth -->
<g id="far-hip">{_rot('far-hip-anim',frames,total,lambda p:p.hip_far)}
  <path d="M-26 -8Q-16 -22 -2 -8Q4 11 -5 31Q-10 44 -21 49Q-35 42 -34 22Q-34 3 -26 -8Z" fill="url(#greenFar)" stroke="#164c25" stroke-width="1.5"/>
  <g transform="translate(-18 45)"><g>{_rot('far-knee-anim',frames,total,lambda p:p.knee_far)}
    <path d="M-11 -4Q2 -9 11 3L9 34Q6 44 -2 48Q-13 43 -14 31Z" fill="url(#greenFar)"/>
    <path d="M-14 39Q0 33 19 39L25 49Q7 56 -13 50Z" fill="#172019" stroke="#61d777" stroke-opacity=".48"/>
  </g></g>
</g>

<!-- FAR ARM -->
<g id="far-shoulder" transform="translate(-57 -90)"><g>{_rot('far-shoulder-anim',frames,total,lambda p:p.shoulder_far)}
  <path d="M-22 -10Q-2 -28 18 -10Q29 8 15 29Q3 43 -12 34Q-30 18 -22 -10Z" fill="url(#greenFar)"/>
  <path d="M-9 22Q5 16 15 28L12 57Q6 69 -5 63Q-16 53 -13 36Z" fill="url(#greenFar)"/>
  <g transform="translate(1 57)"><g>{_rot('far-elbow-anim',frames,total,lambda p:p.elbow_far)}
    <path d="M-9 -5Q4 -9 13 3L11 39Q3 52 -8 43Q-14 28 -12 7Z" fill="url(#greenFar)"/>
    <path d="M-15 37Q1 28 16 39Q20 54 4 62Q-14 58 -18 47Z" fill="url(#greenFar)"/>
  </g></g>
</g></g>

<!-- RIPPED PURPLE SHORTS -->
<g id="titan-purple-shorts">
  <path d="M-39 -22Q0 -10 39 -22L43 8L30 22L18 14L7 25L-6 16L-19 24L-31 14L-45 8Z" fill="url(#shortsPurple)" stroke="#b995cb" stroke-opacity=".65" stroke-width="1.5"/>
  <path d="M-36 7L-49 21L-28 15M38 7L51 19L28 15M-3 -9L2 13" fill="none" stroke="#d2aedf" stroke-width="2.2" opacity=".58"/>
</g>

<!-- NEAR LEG -->
<g id="near-hip">{_rot('near-hip-anim',frames,total,lambda p:p.hip_near)}
  <path d="M7 -9Q24 -24 38 -7Q45 13 34 35Q28 49 15 53Q-1 45 0 25Q0 4 7 -9Z" fill="url(#greenNear)" stroke="#baf9bf" stroke-opacity=".22" stroke-width="1.4"/>
  <path d="M10 6Q27 2 37 14M7 29Q23 23 34 31" fill="none" stroke="#0a5a26" stroke-width="2" opacity=".72"/>
  <g transform="translate(20 48)"><g>{_rot('near-knee-anim',frames,total,lambda p:p.knee_near)}
    <path d="M-12 -5Q4 -11 14 4L12 37Q7 50 -4 52Q-17 46 -17 29Z" fill="url(#greenNear)"/>
    <path d="M-18 42Q1 34 23 42L31 54Q11 63 -18 56Z" fill="#151e19" stroke="#9affaa" stroke-opacity=".64" stroke-width="1.3"/>
  </g></g>
</g>

<!-- TORSO / TRAPS / CHEST: intentionally huge but no longer occludes the face -->
<g id="titan-torso" transform="translate(0 -22)"><g>{_rot('torso-anim',frames,total,lambda p:p.torso)}
  <path d="M-74 -62Q-69 -99 -47 -113Q-29 -125 -15 -113Q0 -127 16 -113Q31 -125 49 -112Q70 -97 76 -61Q69 -25 43 -5Q22 8 0 4Q-23 8 -44 -5Q-69 -27 -74 -62Z" fill="url(#torsoGreen)" stroke="#caffce" stroke-opacity=".42" stroke-width="1.7" filter="url(#titanShadow)"/>
  <g id="titan-traps">
    <path d="M-61 -92Q-43 -126 -10 -118L0 -101L10 -118Q44 -126 63 -91Q42 -84 25 -88Q12 -91 0 -82Q-12 -91 -25 -88Q-43 -83 -61 -92Z" fill="url(#trapGreen)"/>
  </g>
  <g id="titan-chest">
    <path d="M-57 -72Q-39 -94 -5 -80L-2 -48Q-31 -38 -55 -54Z" fill="url(#pecGreen)" stroke="#155f2b" stroke-opacity=".55"/>
    <path d="M5 -80Q39 -94 58 -71L56 -53Q31 -38 2 -48Z" fill="url(#pecGreen)" stroke="#155f2b" stroke-opacity=".55"/>
    <path d="M0 -78V-17M-45 -42Q-24 -29 -4 -36M45 -42Q24 -29 4 -36M-30 -24Q-15 -15 -3 -20M30 -24Q15 -15 3 -20" fill="none" stroke="#073b18" stroke-width="2.5" opacity=".78"/>
  </g>

  <!-- short neck + large, explicit face group -->
  <path d="M-20 -111L-18 -136H19L22 -110Q8 -101 -20 -111Z" fill="url(#neckGreen)"/>
  <g id="titan-head" transform="translate(0 -151)"><g>{_rot('head-anim',frames,total,lambda p:p.head)}
    <path id="titan-face" d="M-34 -18Q-31 -46 -8 -52Q18 -54 34 -34Q42 -10 34 21Q22 41 1 46Q-23 40 -35 20Q-42 0 -34 -18Z" fill="url(#faceGreen)" stroke="#d7ffda" stroke-opacity=".55" stroke-width="1.8"/>
    <path id="titan-hair" d="M-34 -22L-45 -38L-31 -35L-36 -54L-19 -47L-12 -64L0 -50L12 -66L17 -49L35 -59L31 -42L48 -45L35 -23Q18 -40 -3 -38Q-21 -37 -34 -22Z" fill="#070c0a"/>
    <path id="titan-brow" d="M-28 -10Q-17 -20 -5 -10M6 -10Q19 -21 30 -8" fill="none" stroke="#062d13" stroke-width="5.5" stroke-linecap="round"/>
    <path d="M-24 -5L-7 -2M7 -2L25 -6" stroke="#d8ffe0" stroke-width="3" stroke-linecap="round"/>
    <circle cx="-12" cy="-3" r="2.6" fill="#07110a"/><circle cx="15" cy="-3" r="2.6" fill="#07110a"/>
    <path d="M2 1L-3 12L6 14" fill="none" stroke="#17622d" stroke-width="2.6"/>
    <path id="titan-jaw" d="M-25 18Q0 9 27 18L22 34Q1 47 -22 33Z" fill="#267e37" stroke="#0a421b" stroke-width="1.8"/>
    <path d="M-18 21Q1 14 21 21Q12 35 0 36Q-12 34 -18 21Z" fill="#220b0c"/>
    <path d="M-14 22H17L13 28H-10Z" fill="#f5efe3"/>
    <path d="M-28 15Q-34 24 -29 31M29 14Q35 23 30 31" fill="none" stroke="#0a421b" stroke-width="2.2" opacity=".75"/>
  </g></g>

  <!-- NEAR ARM: giant shoulder/biceps/forearm/fist with foreshortening -->
  <g id="near-shoulder" transform="translate(62 -88)"><g>{_rot('near-shoulder-anim',frames,total,lambda p:p.shoulder_near)}
    <path d="M-28 -12Q-3 -34 25 -13Q39 8 24 35Q10 51 -10 40Q-35 23 -28 -12Z" fill="url(#greenNear)" stroke="#d6ffda" stroke-opacity=".35"/>
    <path d="M-12 26Q7 15 20 31L17 65Q8 81 -7 70Q-21 54 -18 37Z" fill="url(#greenNear)"/>
    <path d="M-10 34Q5 25 17 37M-13 54Q4 43 16 54" fill="none" stroke="#0b5c28" stroke-width="2.1" opacity=".75"/>
    <g transform="translate(1 66)"><g>{_rot('near-elbow-anim',frames,total,lambda p:p.elbow_near)}
      <path d="M-14 -7Q4 -13 16 5L14 45Q5 61 -10 52Q-20 35 -18 10Z" fill="url(#greenNear)"/>
      <g id="near-fist" transform="translate(0 51)"><animateTransform attributeName="transform" type="scale" additive="sum" values="{fists}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>
        <path d="M-30 -18Q-7 -34 24 -17Q40 1 29 25Q12 42 -16 32Q-38 17 -30 -18Z" fill="url(#fistGreen)" stroke="#e0ffe2" stroke-opacity=".55" stroke-width="1.6"/>
        <path d="M-21 -7Q-5 -13 20 -7M-23 3Q-5 -3 23 4M-18 14Q-1 8 18 14" stroke="#0a5423" stroke-width="2.2" fill="none" opacity=".78"/>
      </g>
    </g></g>
  </g></g>
</g></g>
</g></g></g></g>'''
