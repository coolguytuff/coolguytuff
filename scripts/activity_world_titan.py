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

    return f'''<!-- TITAN_BODY_DEPTH --><!-- TITAN_CONTINUOUS_RIG --><!-- TITAN_FOOT_CONTACT_CYCLE --><!-- HULK_MASS_SILHOUETTE --><!-- HULK_DIRECTIONAL_PROFILE --><!-- TRUE_RIGHT_FACING_PROFILE_V6 --><!-- TRUE_SIDE_FACING_PROFILE_V7 --><!-- BIOMECHANICAL_MOTION_V5 --><!-- BRICK_STATE_JUMP --><!-- BRICK_STATE_CLIMB --><!-- BRICK_STATE_SPRINT --><!-- BRICK_STATE_TURN --><!-- BRICK_ROUTE_FORWARD --><!-- BRICK_ROUTE_REVERSE -->
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

<g id="far-shoulder" transform="translate(-36 -92) scale(.58)"><g>{_rot('far-shoulder-anim',frames,total,lambda p:p.shoulder_far)}
  <path d="M-29 -15Q-5 -39 24 -14Q39 9 22 39Q7 57 -18 46Q-43 25 -29 -15Z" fill="url(#greenFar)" opacity=".68"/>
  <path d="M-13 27Q8 17 22 32L19 67Q10 84 -8 75Q-24 58 -20 39Z" fill="url(#greenFar)" opacity=".64"/>
  <path d="M-18 42Q3 32 19 45" fill="none" stroke="#0b4d20" stroke-width="2" opacity=".42"/>
  <g transform="translate(2 78)"><g>{_rot('far-elbow-anim',frames,total,lambda p:p.elbow_far)}
    <path d="M-13 -7Q7 -14 19 5L16 48Q6 64 -11 55Q-22 36 -18 8Z" fill="url(#greenFar)" opacity=".66"/>
    <path d="M-23 43Q0 31 24 44Q31 63 7 74Q-20 68 -26 54Z" fill="url(#greenFar)" opacity=".62"/>
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
  <path d="M-64 -57Q-65 -99 -43 -121Q-28 -135 -10 -122Q4 -139 25 -120Q57 -134 81 -108Q104 -82 108 -48Q100 -13 68 10Q39 23 8 11Q-24 17 -49 1Q-69 -18 -64 -57Z" fill="url(#torsoGreen)" stroke="#b9e9b5" stroke-opacity=".34" stroke-width="1.7" filter="url(#titanShadow)"/>
  <path id="titan-back-plane" d="M-58 -103Q-68 -76 -62 -45Q-59 -17 -40 0" fill="none" stroke="#073b18" stroke-width="5.4" opacity=".38"/>
  <g id="titan-traps"><path d="M-53 -94Q-39 -129 -11 -125L6 -106L22 -131Q61 -137 89 -94Q62 -83 38 -89Q19 -94 7 -83Q-6 -93 -21 -90Q-38 -84 -53 -94Z" fill="url(#trapGreen)"/></g>
  <g id="titan-chest">
    <g id="titan-pec-far" transform="translate(-15 0) scale(.42 1)">
      <path d="M-64 -73Q-44 -102 -5 -85L-3 -46Q-35 -34 -64 -52Z" fill="url(#pecGreen)" stroke="#155f2b" stroke-opacity=".34" opacity=".48"/>
      <path d="M-49 -60Q-34 -69 -20 -64M-45 -42Q-28 -31 -8 -36" fill="none" stroke="#6fbd68" stroke-width="1.1" opacity=".14"/>
    </g>
    <g id="titan-pec-near" transform="translate(14 0) scale(1.16 1)">
      <path d="M-1 -86Q49 -108 80 -72L79 -46Q44 -27 0 -44Z" fill="url(#pecGreen)" stroke="#155f2b" stroke-opacity=".64"/>
      <path d="M23 -66Q49 -78 68 -61M18 -42Q44 -27 71 -43" fill="none" stroke="#8cda81" stroke-width="1.6" opacity=".48"/>
    </g>
    <path id="titan-sternum-forward" d="M22 -84Q28 -50 23 -13" fill="none" stroke="#073b18" stroke-width="3" opacity=".90"/>
    <path id="titan-forward-ribcage" d="M23 -67Q60 -62 78 -43Q66 -14 39 2" fill="none" stroke="#0b4f22" stroke-width="2.5" opacity=".45"/>
    <path d="M-29 -22Q-9 -8 8 -17M60 -22Q35 -7 20 -16" fill="none" stroke="#073b18" stroke-width="2.3" opacity=".68"/>
    <path d="M-19 -4Q-8 4 2 -2M25 -2Q38 5 50 -6" fill="none" stroke="#78cf6e" stroke-width="1.3" opacity=".30"/>
  </g>
  <path d="M-13 -115L-10 -143H31L36 -113Q18 -100 -13 -115Z" fill="url(#neckGreen)"/>
  <path d="M-6 -135Q13 -127 29 -136M-3 -125Q13 -118 27 -127" fill="none" stroke="#0a4c20" stroke-width="2" opacity=".64"/>

  <g id="titan-head" transform="translate(16 -156)"><g>{_rot('head-anim',frames,total,lambda p:p.head)}
    <ellipse id="titan-ear" cx="-28" cy="1" rx="6" ry="10.5" fill="#3f9f43" stroke="#0b4c20" stroke-width="1.4"/>
    <g id="titan-face">
      <path id="titan-face-silhouette-forward" d="M-29 -22Q-25 -48 -5 -58Q15 -62 31 -49Q39 -42 41 -30Q47 -24 50 -15Q52 -7 58 0L66 6L61 14L53 18Q52 29 46 38L38 47Q26 57 7 55Q-13 53 -25 40Q-35 29 -36 14Q-37 -2 -32 -13Q-31 -18 -29 -22Z" fill="url(#faceGreen)" stroke="#c7edbd" stroke-opacity=".42" stroke-width="1.8"/>
    </g>
    <path id="titan-hair" d="M-33 -22L-47 -40L-30 -38L-37 -59L-20 -50L-10 -70L1 -54L14 -71L22 -53L38 -62L34 -47L48 -49L37 -29L25 -31L15 -28L5 -35L-7 -27L-20 -34Z" fill="#070b09"/>
    <g id="titan-brow"><path id="titan-brow-ridge-forward" d="M-11 -10Q-4 -16 3 -13M7 -15Q23 -28 39 -10" fill="none" stroke="#062d13" stroke-width="5.5" stroke-linecap="round"/></g>
    <g id="titan-eye-far" opacity=".08"><path d="M-13 -5L-5 -3" stroke="#d7edcc" stroke-width="1.5" stroke-linecap="round"/></g>
    <g id="titan-eye-near"><path d="M10 -4L34 -8" stroke="#e5f4da" stroke-width="3.3" stroke-linecap="round"/><circle cx="24" cy="-6" r="2.9" fill="#07110a"/></g>
    <g id="titan-nose"><path id="titan-nose-silhouette" d="M25 -2Q39 0 52 4L65 7L68 11L61 16L45 17L31 14" fill="#388f3d" stroke="#155f2b" stroke-width="2.6" stroke-linejoin="round"/></g>
    <circle id="titan-profile-nose-tip" cx="66" cy="10" r="3.5" fill="#61bd5d" opacity=".82"/>
    <path id="titan-cheek-forward" d="M30 12Q50 13 55 24Q50 35 39 42" fill="none" stroke="#75c76c" stroke-width="2.1" opacity=".48"/>
    <path d="M-14 8Q-6 12 1 10M33 16Q47 20 56 15" fill="none" stroke="#246f2e" stroke-width="1.7" opacity=".62"/>
    <path id="titan-jaw" d="M-20 18Q-2 13 19 16L48 21L49 34Q38 49 17 55Q-7 53 -23 38Z" fill="#2d8436" stroke="#0a421b" stroke-width="1.8"/>
    <path id="titan-chin-forward" d="M18 51Q35 48 46 35Q42 51 24 58Z" fill="#2a7831" stroke="#0a421b" stroke-width="1.2"/>
    <path id="titan-mouth" d="M13 26Q30 20 49 25Q43 37 25 40Q14 36 13 26Z" fill="#220b0c"/>
    <path d="M18 26Q31 22 43 26L39 31Q29 34 19 30Z" fill="#eee9da"/>
    <path d="M23 44Q34 40 43 34" fill="none" stroke="#0b4a1e" stroke-width="2" opacity=".7"/>
  </g></g>

  <g id="near-shoulder" transform="translate(84 -85) scale(1.12)"><g>{_rot('near-shoulder-anim',frames,total,lambda p:p.shoulder_near)}
    <path d="M-37 -17Q-5 -45 33 -16Q52 11 31 47Q13 68 -17 53Q-51 28 -37 -17Z" fill="url(#greenNear)" stroke="#c7f2bf" stroke-opacity=".29" stroke-width="1.2"/>
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
