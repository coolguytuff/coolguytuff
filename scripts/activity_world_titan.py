from __future__ import annotations

import math
from dataclasses import dataclass

from activity_world_model import Frame, RUNNER_FOOTLINE, fmt

THIGH_FAR = 51.0
SHIN_FAR = 45.0
FOOT_FAR = 12.0
THIGH_NEAR = 53.0
SHIN_NEAR = 47.0
FOOT_NEAR = 13.0


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
        # Canonical rig faces +X. Lean the mass into travel and tuck whichever
        # leg is in forward swing; the trailing stance leg stays comparatively
        # extended. Mirroring the rig for -X preserves the same biomechanics.
        s = math.sin(p * math.tau)
        c = math.cos(p * math.tau)
        double_step = .5 - .5 * math.cos(p * math.tau * 2)
        return Pose(
            8.0 + 1.2 * c,
            .4 + .45 * double_step,
            -8.0 - 1.0 * c,
            -38 * s - 6,
            74 + 18 * max(0, s),
            38 * s + 8,
            76 + 18 * max(0, -s),
            34 * s + 3,
            22 + 46 * max(0, -s),
            -34 * s - 3,
            22 + 46 * max(0, s),
            1.08 + .08 * max(0, -s),
            .65 * double_step,
        )

    if frame.state == 'jump':
        if p < .18:
            q = p / .18
            return Pose(
                _lerp(-9, -13, q), _lerp(1, 5, q), _lerp(9, 13, q),
                _lerp(12, 35, q), _lerp(72, 84, q),
                _lerp(16, 40, q), _lerp(74, 84, q),
                _lerp(2, 10, q), _lerp(44, 96, q),
                _lerp(-2, -10, q), _lerp(42, 94, q),
                _lerp(1.10, 1.16, q), _lerp(0, 5, q),
            )
        if p < .42:
            q = (p - .18) / .24
            return Pose(
                _lerp(-13, -5, q), _lerp(5, -2, q), _lerp(13, 5, q),
                _lerp(35, 18, q), _lerp(84, 58, q),
                _lerp(40, -72, q), _lerp(84, 30, q),
                _lerp(10, 26, q), _lerp(96, 34, q),
                _lerp(-10, -24, q), _lerp(94, 30, q),
                _lerp(1.16, 1.33, q), _lerp(5, -2, q),
            )
        if p < .78:
            q = (p - .42) / .36
            tuck = math.sin(math.pi * q)
            return Pose(
                _lerp(-5, -3, q), -2, _lerp(5, 3, q),
                _lerp(18, 10, q), _lerp(58, 64, q),
                _lerp(-72, -55, q), _lerp(30, 38, q),
                _lerp(26, 10, q), 34 + 42 * tuck - 8 * q,
                _lerp(-24, -12, q), 30 + 44 * tuck - 6 * q,
                _lerp(1.33, 1.29, q), -2,
            )
        q = (p - .78) / .22
        return Pose(
            _lerp(-3, 4, q), _lerp(-2, 4, q), _lerp(3, -2, q),
            _lerp(10, -12, q), _lerp(64, 82, q),
            _lerp(-55, -18, q), _lerp(38, 76, q),
            _lerp(10, 8, q), _lerp(28, 82, q),
            _lerp(-12, -8, q), _lerp(24, 80, q),
            _lerp(1.29, 1.14, q), _lerp(-2, 5, q),
        )

    if frame.state == 'climb':
        if p < .22:
            q = p / .22
            return Pose(
                _lerp(-8, -15, q), 1, _lerp(8, 15, q),
                _lerp(-4, -70, q), _lerp(62, 22, q),
                _lerp(-8, -106, q), _lerp(58, 12, q),
                -8, 54, 12, 48, _lerp(1.12, 1.30, q), 0,
            )
        if p < .50:
            q = (p - .22) / .28
            return Pose(-15, 3 + 1.2 * math.sin(q * math.pi), 15,
                        -72, 20, -108, 10, -18, 68, 18, 62, 1.32, 2)
        if p < .82:
            q = (p - .50) / .32
            return Pose(
                _lerp(-15, -6, q), _lerp(3, 0, q), _lerp(15, 6, q),
                _lerp(-72, -34, q), _lerp(20, 88, q),
                _lerp(-108, -42, q), _lerp(10, 90, q),
                _lerp(-18, 24, q), _lerp(68, 88, q),
                _lerp(18, -14, q), _lerp(62, 92, q),
                _lerp(1.32, 1.18, q), _lerp(2, 0, q),
            )
        q = (p - .82) / .18
        return Pose(
            _lerp(-6, -2, q), 0, _lerp(6, 2, q),
            _lerp(-34, -4, q), _lerp(88, 60, q),
            _lerp(-42, -6, q), _lerp(90, 62, q),
            _lerp(24, 0, q), _lerp(88, 24, q),
            _lerp(-14, 0, q), _lerp(92, 24, q),
            _lerp(1.18, 1.12, q), 0,
        )

    if frame.state == 'turn':
        s = math.sin(p * math.pi)
        return Pose(16 * s - 2, 1.5 * s, 2 - 16 * s,
                    -24 * s - 4, 68, 30 * s - 6, 70,
                    20 * s, 70, -18 * s, 70, 1.18, 1.5 * s)

    breathe = math.sin(frame.t * 1.8) if frame.t else 0
    return Pose(-2, 0, 2 - .6 * breathe, -4, 62, -6, 62,
                -2, 18, 2, 18, 1.12, .35 * breathe)


def _rot(name, frames, total, getter):
    keys = ';'.join(fmt(f.t / total) for f in frames)
    vals = ';'.join(f'{fmt(getter(pose_for(f)))} 0 0' for f in frames)
    return (
        f'<animateTransform id="{name}" attributeName="transform" type="rotate" '
        f'additive="sum" calcMode="linear" values="{vals}" keyTimes="{keys}" '
        f'dur="{fmt(total)}s" repeatCount="indefinite"/>'
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
    pos = ';'.join(
        f'{fmt(f.x)} {fmt(f.y - (_pose_foot_bottom(pose_for(f)) - RUNNER_FOOTLINE))}'
        for f in frames
    )
    shadow_pos = ';'.join(f'{fmt(f.x)} {fmt(f.y + RUNNER_FOOTLINE + 7)}' for f in frames)
    scales = ';'.join(f'{fmt(f.sx)} {fmt(f.sy)}' for f in frames)
    dirs = ';'.join(f'{f.direction} 1' for f in frames)
    pelvis = ';'.join(f'0 {fmt(pose_for(f).pelvis_y + pose_for(f).body_bob)}' for f in frames)
    fists = ';'.join(f'{fmt(pose_for(f).fist_near_scale)} {fmt(pose_for(f).fist_near_scale)}' for f in frames)

    return f'''<!-- TITAN_BODY_DEPTH --><!-- TITAN_CONTINUOUS_RIG --><!-- TITAN_FOOT_CONTACT_CYCLE --><!-- HULK_MASS_SILHOUETTE --><!-- HULK_DIRECTIONAL_PROFILE --><!-- TRUE_RIGHT_FACING_PROFILE_V6 --><!-- BIOMECHANICAL_MOTION_V5 --><!-- BRICK_STATE_JUMP --><!-- BRICK_STATE_CLIMB --><!-- BRICK_STATE_SPRINT --><!-- BRICK_STATE_TURN --><!-- BRICK_ROUTE_FORWARD --><!-- BRICK_ROUTE_REVERSE -->
<g id="titan-shadow-motion"><animateTransform attributeName="transform" type="translate" calcMode="linear" values="{shadow_pos}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><ellipse cx="0" cy="0" rx="67" ry="12" fill="#000" opacity=".46" filter="url(#blur4)"/></g>
<g id="titan-motion"><animateTransform attributeName="transform" type="translate" calcMode="linear" values="{pos}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="titan-direction"><animateTransform attributeName="transform" type="scale" calcMode="discrete" values="{dirs}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="titan-squash"><animateTransform attributeName="transform" type="scale" calcMode="linear" values="{scales}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="titan-pelvis"><animateTransform attributeName="transform" type="translate" calcMode="linear" values="{pelvis}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>

<g id="far-hip">{_rot('far-hip-anim',frames,total,lambda p:p.hip_far)}
  <path d="M-33 -10Q-18 -30 1 -10Q10 12 -3 39Q-12 56 -27 60Q-47 50 -46 24Q-46 1 -33 -10Z" fill="url(#greenFar)" stroke="#123f20" stroke-width="1.6"/>
  <path d="M-37 11Q-18 2 -3 15M-41 35Q-19 23 -5 37" fill="none" stroke="#0b4e22" stroke-width="2" opacity=".68"/>
  <g transform="translate(-24 54)"><g>{_rot('far-knee-anim',frames,total,lambda p:p.knee_far)}
    <path d="M-16 -6Q4 -14 17 4L15 40Q9 56 -4 59Q-21 53 -22 33Z" fill="url(#greenFar)"/>
    <path d="M-22 47Q-2 39 23 45Q36 49 42 57Q32 65 10 65Q-11 66 -25 59Z" fill="url(#greenFar)" stroke="#164c25" stroke-width="1.2"/>
    <path d="M16 52L37 57M9 56L31 62M1 57L21 64" fill="none" stroke="#0b4d20" stroke-width="1.3" opacity=".72"/>
  </g></g>
</g>

<g id="far-shoulder" transform="translate(-48 -91) scale(.78)"><g>{_rot('far-shoulder-anim',frames,total,lambda p:p.shoulder_far)}
  <path d="M-29 -15Q-5 -39 24 -14Q39 9 22 39Q7 57 -18 46Q-43 25 -29 -15Z" fill="url(#greenFar)" opacity=".82"/>
  <path d="M-13 27Q8 17 22 32L19 67Q10 84 -8 75Q-24 58 -20 39Z" fill="url(#greenFar)" opacity=".80"/>
  <path d="M-18 42Q3 32 19 45" fill="none" stroke="#0b4d20" stroke-width="2" opacity=".58"/>
  <g transform="translate(2 78)"><g>{_rot('far-elbow-anim',frames,total,lambda p:p.elbow_far)}
    <path d="M-13 -7Q7 -14 19 5L16 48Q6 64 -11 55Q-22 36 -18 8Z" fill="url(#greenFar)" opacity=".82"/>
    <path d="M-23 43Q0 31 24 44Q31 63 7 74Q-20 68 -26 54Z" fill="url(#greenFar)" opacity=".80"/>
  </g></g>
</g></g>

<g id="titan-purple-shorts">
  <path d="M-50 -24Q-15 -13 4 -17Q27 -12 50 -25L54 10L38 27L20 18L9 31L-7 20L-23 29L-38 17L-55 9Z" fill="url(#shortsPurple)" stroke="#b995cb" stroke-opacity=".62" stroke-width="1.5"/>
  <path d="M-48 6L-61 25L-34 17M48 6L62 23L34 17M-3 -11L3 17M-31 -14L-18 24M31 -15L18 23" fill="none" stroke="#d2aedf" stroke-width="2" opacity=".52"/>
  <path d="M-53 10L-41 4L-34 17L-22 10L-15 24M52 10L41 4L34 17L23 10L17 24" fill="none" stroke="#2a1333" stroke-width="2.2" opacity=".8"/>
</g>

<g id="near-hip">{_rot('near-hip-anim',frames,total,lambda p:p.hip_near)}
  <path d="M3 -11Q25 -32 46 -10Q56 15 41 43Q31 61 13 64Q-10 53 -8 27Q-7 2 3 -11Z" fill="url(#greenNear)" stroke="#aee9a9" stroke-opacity=".20" stroke-width="1.4"/>
  <path d="M5 8Q29 -1 44 15M1 35Q26 23 41 37" fill="none" stroke="#0a5423" stroke-width="2.2" opacity=".74"/>
  <g transform="translate(20 57)"><g>{_rot('near-knee-anim',frames,total,lambda p:p.knee_near)}
    <path d="M-17 -7Q6 -16 20 4L18 43Q10 61 -6 63Q-25 55 -24 33Z" fill="url(#greenNear)"/>
    <path d="M-25 50Q-2 40 27 48Q41 51 49 61Q37 72 12 73Q-14 73 -28 64Z" fill="url(#greenNear)" stroke="#c6f6bf" stroke-opacity=".22" stroke-width="1.2"/>
    <path d="M20 55L44 61M12 59L36 67M3 61L26 69" fill="none" stroke="#0a5423" stroke-width="1.5" opacity=".76"/>
  </g></g>
</g>

<g id="titan-torso" transform="translate(0 -22)"><g>{_rot('torso-anim',frames,total,lambda p:p.torso)}
  <path d="M-68 -56Q-68 -99 -47 -121Q-31 -136 -12 -122Q3 -139 23 -120Q52 -133 76 -109Q99 -85 101 -50Q94 -15 64 9Q35 22 4 11Q-27 17 -51 2Q-72 -17 -68 -56Z" fill="url(#torsoGreen)" stroke="#b9e9b5" stroke-opacity=".34" stroke-width="1.7" filter="url(#titanShadow)"/>
  <path id="titan-back-plane" d="M-61 -101Q-72 -75 -66 -46Q-63 -18 -45 -1" fill="none" stroke="#073b18" stroke-width="5" opacity=".34"/>
  <g id="titan-traps"><path d="M-58 -94Q-43 -130 -13 -125L4 -106L20 -130Q57 -137 84 -95Q58 -84 35 -90Q17 -95 5 -84Q-8 -94 -24 -91Q-42 -85 -58 -94Z" fill="url(#trapGreen)"/></g>
  <g id="titan-chest">
    <g id="titan-pec-far" transform="translate(-9 0) scale(.64 1)">
      <path d="M-64 -73Q-44 -102 -5 -85L-3 -46Q-35 -34 -64 -52Z" fill="url(#pecGreen)" stroke="#155f2b" stroke-opacity=".42" opacity=".72"/>
      <path d="M-49 -60Q-34 -69 -20 -64M-45 -42Q-28 -31 -8 -36" fill="none" stroke="#6fbd68" stroke-width="1.2" opacity=".22"/>
    </g>
    <g id="titan-pec-near" transform="translate(8 0) scale(1.08 1)">
      <path d="M-1 -86Q48 -106 77 -72L76 -47Q42 -28 0 -44Z" fill="url(#pecGreen)" stroke="#155f2b" stroke-opacity=".58"/>
      <path d="M23 -66Q47 -76 64 -62M18 -42Q42 -28 67 -43" fill="none" stroke="#83d279" stroke-width="1.5" opacity=".42"/>
    </g>
    <path id="titan-sternum-forward" d="M10 -82Q15 -51 10 -14" fill="none" stroke="#073b18" stroke-width="2.8" opacity=".86"/>
    <path d="M-38 -22Q-16 -8 2 -17M49 -22Q27 -7 9 -16" fill="none" stroke="#073b18" stroke-width="2.3" opacity=".70"/>
    <path d="M-25 -4Q-13 4 -2 -2M16 -2Q31 5 43 -6" fill="none" stroke="#78cf6e" stroke-width="1.3" opacity=".32"/>
  </g>
  <path d="M-18 -115L-15 -143H27L31 -113Q14 -100 -18 -115Z" fill="url(#neckGreen)"/>
  <path d="M-11 -135Q8 -127 24 -136M-8 -125Q8 -118 22 -127" fill="none" stroke="#0a4c20" stroke-width="2" opacity=".64"/>

  <g id="titan-head" transform="translate(8 -156)"><g>{_rot('head-anim',frames,total,lambda p:p.head)}
    <ellipse id="titan-ear" cx="-30" cy="2" rx="6.5" ry="11" fill="#3f9f43" stroke="#0b4c20" stroke-width="1.4"/>
    <path id="titan-face" d="M-31 -20Q-27 -49 -5 -57Q18 -60 36 -44Q45 -35 45 -19Q51 -9 57 5L49 12Q47 31 31 44Q13 55 -8 50Q-27 43 -34 27Q-40 11 -35 -6Q-34 -14 -31 -20Z" fill="url(#faceGreen)" stroke="#c7edbd" stroke-opacity=".42" stroke-width="1.8"/>
    <path id="titan-hair" d="M-35 -21L-49 -40L-31 -38L-39 -59L-21 -50L-12 -70L0 -53L13 -70L21 -52L39 -62L34 -46L49 -49L38 -27L25 -31L15 -27L5 -34L-7 -26L-21 -33Z" fill="#070b09"/>
    <path id="titan-brow" d="M-21 -11Q-13 -19 -5 -13M6 -14Q21 -27 35 -10" fill="none" stroke="#062d13" stroke-width="5.2" stroke-linecap="round"/>
    <g id="titan-eye-far" opacity=".24"><path d="M-18 -5L-7 -3" stroke="#d7edcc" stroke-width="2" stroke-linecap="round"/><circle cx="-10" cy="-4" r="1.6" fill="#07110a"/></g>
    <g id="titan-eye-near"><path d="M6 -4L31 -8" stroke="#e5f4da" stroke-width="3.2" stroke-linecap="round"/><circle cx="21" cy="-6" r="2.8" fill="#07110a"/></g>
    <path id="titan-nose" d="M21 -2Q34 1 47 7L54 10L47 17L27 15" fill="#388f3d" stroke="#155f2b" stroke-width="2.5" stroke-linejoin="round"/>
    <circle id="titan-profile-nose-tip" cx="53" cy="10" r="3.2" fill="#61bd5d" opacity=".78"/>
    <path id="titan-cheek-forward" d="M24 12Q43 13 48 24Q42 34 31 39" fill="none" stroke="#75c76c" stroke-width="2.1" opacity=".46"/>
    <path d="M-19 8Q-10 12 -2 10M25 16Q38 19 47 15" fill="none" stroke="#246f2e" stroke-width="1.7" opacity=".65"/>
    <path id="titan-jaw" d="M-24 18Q-6 12 18 15L43 21L42 34Q29 48 8 51Q-13 48 -27 36Z" fill="#2d8436" stroke="#0a421b" stroke-width="1.8"/>
    <path id="titan-mouth" d="M5 25Q22 20 40 25Q34 36 16 39Q6 35 5 25Z" fill="#220b0c"/>
    <path d="M10 25Q24 22 35 26L31 31Q20 34 10 30Z" fill="#eee9da"/>
    <path d="M13 42Q25 39 34 33" fill="none" stroke="#0b4a1e" stroke-width="2" opacity=".7"/>
  </g></g>

  <g id="near-shoulder" transform="translate(76 -86) scale(1.06)"><g>{_rot('near-shoulder-anim',frames,total,lambda p:p.shoulder_near)}
    <path d="M-37 -17Q-5 -45 33 -16Q52 11 31 47Q13 68 -17 53Q-51 28 -37 -17Z" fill="url(#greenNear)" stroke="#c7f2bf" stroke-opacity=".27" stroke-width="1.2"/>
    <path d="M-17 32Q10 16 29 37L24 80Q10 101 -12 86Q-31 64 -26 44Z" fill="url(#greenNear)"/>
    <path d="M-14 40Q9 26 26 42M-19 65Q7 49 24 63M-8 12Q10 5 25 14" fill="none" stroke="#0b5c28" stroke-width="2.2" opacity=".76"/>
    <path d="M18 20Q31 31 22 48" fill="none" stroke="#7bd471" stroke-width="1.4" opacity=".42"/>
    <g transform="translate(1 69)"><g>{_rot('near-elbow-anim',frames,total,lambda p:p.elbow_near)}
      <path d="M-20 -8Q6 -17 23 6L20 53Q8 75 -15 64Q-31 41 -26 11Z" fill="url(#greenNear)"/>
      <path d="M-15 15Q6 5 21 18M-18 40Q6 28 20 42" fill="none" stroke="#0a5423" stroke-width="2" opacity=".72"/>
      <g id="near-fist" transform="translate(0 61)"><animateTransform attributeName="transform" type="scale" additive="sum" calcMode="linear" values="{fists}" keyTimes="{keys}" dur="{fmt(total)}s" repeatCount="indefinite"/>
        <path d="M-40 -25Q-10 -46 34 -23Q57 2 41 37Q16 61 -24 46Q-54 24 -40 -25Z" fill="url(#fistGreen)" stroke="#d5f3cd" stroke-opacity=".42" stroke-width="1.6"/>
        <path d="M-29 -10Q-5 -20 29 -10M-32 4Q-5 -7 33 5M-25 20Q-1 10 27 19" stroke="#0a5423" stroke-width="2.3" fill="none" opacity=".80"/>
        <path d="M-21 -20Q-12 -5 -18 10M-3 -25Q4 -7 -1 10M16 -23Q23 -4 17 11" fill="none" stroke="#8ed47f" stroke-width="1.3" opacity=".34"/>
      </g>
    </g></g>
  </g></g>
</g></g>
</g></g></g></g>'''
