from __future__ import annotations

from activity_world_model import Frame, fmt


def _state_values(frames: list[Frame], state: str) -> str:
    return ';'.join('1' if frame.state == state else '0' for frame in frames)


def titan_body(pose: str) -> str:
    if pose == 'sprint':
        torso_rot, head = -11, (8, -79)
        far_arm, far_fist = 'M-20 -58 Q-39 -46 -44 -27', (-45, -27)
        near_arm, near_fist = 'M20 -55 Q41 -48 49 -30', (50, -30)
        leg1, foot1 = 'M-13 -9 Q-28 10 -38 25', (-39, 27)
        leg2, foot2 = 'M13 -8 Q24 7 35 19', (37, 21)
    elif pose == 'climb':
        torso_rot, head = -7, (3, -84)
        far_arm, far_fist = 'M-20 -58 Q-39 -71 -42 -92', (-42, -94)
        near_arm, near_fist = 'M21 -57 Q42 -75 46 -101', (46, -103)
        leg1, foot1 = 'M-12 -8 Q-29 5 -31 23', (-32, 25)
        leg2, foot2 = 'M12 -8 Q24 4 20 23', (21, 25)
    elif pose == 'jump':
        torso_rot, head = -5, (2, -80)
        far_arm, far_fist = 'M-20 -58 Q-39 -85 -34 -109', (-34, -111)
        near_arm, near_fist = 'M21 -58 Q46 -49 58 -24', (59, -23)
        leg1, foot1 = 'M-12 -8 Q-25 5 -30 20', (-31, 22)
        leg2, foot2 = 'M12 -8 Q24 4 30 20', (32, 22)
    elif pose == 'turn':
        torso_rot, head = 5, (-3, -80)
        far_arm, far_fist = 'M-19 -57 Q-35 -45 -39 -28', (-40, -28)
        near_arm, near_fist = 'M20 -57 Q33 -45 39 -28', (40, -28)
        leg1, foot1 = 'M-13 -8 Q-22 8 -18 25', (-20, 27)
        leg2, foot2 = 'M13 -8 Q23 8 19 25', (21, 27)
    else:
        torso_rot, head = 0, (0, -80)
        far_arm, far_fist = 'M-20 -58 Q-37 -48 -39 -30', (-40, -30)
        near_arm, near_fist = 'M20 -58 Q37 -48 39 -30', (40, -30)
        leg1, foot1 = 'M-12 -8 Q-20 8 -20 26', (-22, 28)
        leg2, foot2 = 'M12 -8 Q20 8 20 26', (22, 28)

    hx, hy = head
    ffx, ffy = far_fist
    nfx, nfy = near_fist
    f1x, f1y = foot1
    f2x, f2y = foot2
    return f'''
<g transform="rotate({torso_rot})">
  <circle cx="-24" cy="-56" r="14" fill="url(#greenFar)" stroke="#75d887" stroke-opacity=".24"/>
  <path d="{far_arm}" fill="none" stroke="url(#greenFar)" stroke-width="17" stroke-linecap="round"/>
  <g transform="translate({ffx} {ffy})"><ellipse rx="12.5" ry="11.5" fill="url(#greenFar)" stroke="#83e893" stroke-opacity=".32"/><path d="M-7 -3H7M-6 2H7" stroke="#0a4b20" stroke-width="1.1" opacity=".58"/></g>
  <path d="{leg1}" fill="none" stroke="url(#legGreen)" stroke-width="18" stroke-linecap="round"/>
  <ellipse cx="{f1x}" cy="{f1y}" rx="16" ry="8" fill="#11241a" stroke="#4cd56f" stroke-opacity=".45"/>

  <ellipse cx="0" cy="-61" rx="35" ry="24" fill="url(#trapGreen)" stroke="#8ffca5" stroke-opacity=".30"/>
  <path d="M-34 -57 Q-28 -80 0 -83 Q28 -80 34 -57 Q36 -31 23 -15 Q0 -4 -23 -15 Q-36 -31 -34 -57Z" fill="url(#torsoGreen)" stroke="#8ffca5" stroke-opacity=".44" stroke-width="1.25" filter="url(#titanShadow)"/>
  <ellipse cx="-12" cy="-53" rx="15.5" ry="12" fill="url(#pecGreen)" opacity=".94"/>
  <ellipse cx="12" cy="-53" rx="15.5" ry="12" fill="url(#pecGreen)" opacity=".94"/>
  <path d="M0 -66V-29M-22 -38Q0 -27 22 -38" stroke="#073d1b" stroke-width="1.5" opacity=".72" fill="none"/>
  <path d="M-17 -29Q0 -21 17 -29M-13 -23Q0 -17 13 -23" stroke="#8eff9e" stroke-width="1" opacity=".22" fill="none"/>

  <path d="M-19 -18 Q0 -10 19 -18 L18 4 Q8 11 0 8 Q-8 11 -18 4Z" fill="url(#shorts)" stroke="#68718d" stroke-width="1"/>
  <path d="M0 -13V7" stroke="#75eaff" stroke-opacity=".42" stroke-width="1.3"/>
  <path d="{leg2}" fill="none" stroke="url(#greenNear)" stroke-width="20" stroke-linecap="round"/>
  <ellipse cx="{f2x}" cy="{f2y}" rx="17.5" ry="8.7" fill="#14251b" stroke="#83ff9d" stroke-opacity=".56"/>

  <path d="M-11 -75L-9 -89H9L12 -75Z" fill="url(#neckGreen)"/>
  <g transform="translate({hx} {hy})">
    <path d="M-15 -7 Q-10 -19 1 -19 Q14 -16 17 -5 L13 13 Q4 20 -8 16 Q-16 8 -15 -7Z" fill="url(#faceGreen)" stroke="#b0ffbe" stroke-opacity=".40"/>
    <path d="M-12 -6L-2 -2M5 -2L14 -6" stroke="#052b14" stroke-width="2.8" stroke-linecap="round"/>
    <path d="M-7 7 Q1 13 9 7" stroke="#082b17" stroke-width="2.1" fill="none"/>
    <path d="M-5 8L-2 11M1 10L4 12M7 8L10 10" stroke="#f1fff2" stroke-width="1.5"/>
    <circle cx="-4" cy="0" r="1.6" fill="#b8ffff" filter="url(#softGlow)"/><circle cx="7" cy="0" r="1.6" fill="#d7b5ff" filter="url(#softGlow)"/>
  </g>

  <circle cx="25" cy="-56" r="16.5" fill="url(#greenNear)" stroke="#a6ffb1" stroke-opacity=".38"/>
  <path d="{near_arm}" fill="none" stroke="url(#greenNear)" stroke-width="20" stroke-linecap="round"/>
  <g transform="translate({nfx} {nfy})"><ellipse rx="16.5" ry="14.5" fill="url(#fistGreen)" stroke="#baffc3" stroke-opacity=".46"/><path d="M-10 -5H10M-8 1H10M-5 7H8" stroke="#0b4d22" stroke-width="1.25" opacity=".64"/></g>

  <path d="M-22 -68 Q0 -59 22 -68M-15 -24Q0 -18 15 -24" fill="none" stroke="url(#energy)" stroke-width="1.55" opacity=".56" filter="url(#softGlow)"/>
  <path d="M-26 -52Q-20 -43 -16 -38M26 -52Q20 -43 16 -38" stroke="#d8ffd9" stroke-width="1" opacity=".18"/>
  <circle cx="0" cy="-41" r="2.5" fill="#9ff7ff" opacity=".82" filter="url(#softGlow)"/>
</g>'''


def render_titan(frames: list[Frame], total: float) -> str:
    key_times = ';'.join(fmt(frame.t / total) for frame in frames)
    positions = ';'.join(f'{fmt(frame.x)} {fmt(frame.y)}' for frame in frames)
    scales = ';'.join(f'{fmt(frame.sx)} {fmt(frame.sy)}' for frame in frames)
    directions = ';'.join(f'{frame.direction} 1' for frame in frames)

    pose_groups = []
    for state, offset in (('idle', -40), ('jump', -40), ('climb', -40), ('sprint', -40), ('turn', -40)):
        body_pose = 'neutral' if state == 'idle' else state
        pose_groups.append(f'''
      <g id="titan-{state}" opacity="{'1' if state == 'idle' else '0'}">
        <animate attributeName="opacity" calcMode="discrete" values="{_state_values(frames, state)}" keyTimes="{key_times}" dur="{fmt(total)}s" repeatCount="indefinite"/>
        <g transform="translate(0 {offset})"><g transform="scale(1.55)">{titan_body(body_pose)}</g></g>
      </g>''')

    return f'''<!-- TITAN_BODY_DEPTH -->
<!-- BRICK_STATE_JUMP --><!-- BRICK_STATE_CLIMB --><!-- BRICK_STATE_SPRINT --><!-- BRICK_STATE_TURN -->
<!-- BRICK_ROUTE_FORWARD --><!-- BRICK_ROUTE_REVERSE -->
<g id="titan-motion" transform="translate({fmt(frames[0].x)} {fmt(frames[0].y)})">
  <animateTransform attributeName="transform" type="translate" values="{positions}" keyTimes="{key_times}" dur="{fmt(total)}s" repeatCount="indefinite"/>
  <g id="titan-direction">
    <animateTransform attributeName="transform" type="scale" calcMode="discrete" values="{directions}" keyTimes="{key_times}" dur="{fmt(total)}s" repeatCount="indefinite"/>
    <g id="titan-squash">
      <animateTransform attributeName="transform" type="scale" values="{scales}" keyTimes="{key_times}" dur="{fmt(total)}s" repeatCount="indefinite"/>
      <ellipse cx="0" cy="8" rx="43" ry="10" fill="#02050a" opacity=".42" filter="url(#blur4)"/>
      {''.join(pose_groups)}
    </g>
  </g>
</g>'''
