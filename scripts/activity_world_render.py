from __future__ import annotations

from collections import defaultdict

from activity_world_model import BASE_Y, Cell, build_frames, camera_values, classify_steps, fmt, group_weeks, position
from activity_world_titan import render_titan

LEVEL_TOP = {0:'#193149',1:'#145b58',2:'#137f85',3:'#2d67d6',4:'#8548cc'}
LEVEL_FRONT = {0:'#07131f',1:'#0a3434',2:'#0c4b52',3:'#193b82',4:'#432469'}
LEVEL_SIDE = {0:'#040b13',1:'#072323',2:'#08333a',3:'#10285b',4:'#2d194c'}
DAY_COLORS = {0:'#1f2f40',1:'#1f7a6d',2:'#26a899',3:'#5c8cff',4:'#d08cff'}
TOWER_WIDTH = 43.0
TOWER_DEPTH = 22.0


def _wobble(events: list[tuple[float, float]], total: float) -> tuple[str, str, str]:
    frames = [(0.0, 0.0, 1.0)]
    for when, amplitude in sorted(events):
        for offset, dy, scale in [(-.06,0,1),(0,amplitude,.93),(.07,-amplitude*.62,1.07),(.14,amplitude*.35,.965),(.23,-amplitude*.15,1.018),(.34,0,1)]:
            frames.append((max(0, min(total, when + offset)), dy, scale))
    frames.append((total, 0, 1))
    merged = {round(moment,4):(dy,scale) for moment,dy,scale in frames}
    ordered = sorted(merged.items())
    key_times = ';'.join(fmt(moment / total) for moment, _ in ordered)
    translations = ';'.join(f'0 {fmt(values[0])}' for _, values in ordered)
    scales = ';'.join(f'1 {fmt(values[1])}' for _, values in ordered)
    return key_times, translations, scales


def _tower(index: int, week, count: int, events: list[tuple[float, float]], total: float) -> str:
    x, top_absolute = position(index, week, count)
    top = top_absolute - BASE_Y
    level = week.terrain_level
    half, depth = TOWER_WIDTH / 2, TOWER_DEPTH
    key_times, translations, scales = _wobble(events, total)
    shadow = f'M{-half+depth*.2} 5 L{half+depth*1.35} 5 L{half+depth*2.1} {-depth*.75} L{-half+depth*.65} {-depth*.75} Z'
    front = f'{-half},{top} {half},{top} {half},0 {-half},0'
    side = f'{half},{top} {half+depth},{top-depth} {half+depth},{-depth} {half},0'
    top_face = f'{-half},{top} {half},{top} {half+depth},{top-depth} {-half+depth},{top-depth}'
    studs = []
    levels = week.levels or (0,)
    for day, day_level in enumerate(levels[:7]):
        px = -half + 4 + day * (max(1, TOWER_WIDTH - 8) / max(1, min(6, len(levels) - 1)))
        py = top - depth * .42 - (day % 2) * .6
        studs.append(f'<ellipse cx="{fmt(px+depth*.38)}" cy="{fmt(py)}" rx="2.4" ry="1.35" fill="{DAY_COLORS.get(day_level, DAY_COLORS[0])}" stroke="#d5ffff" stroke-opacity=".20"/>')
    return f'''<g id="tower-{index}" transform="translate({fmt(x)} {fmt(BASE_Y)})" data-level="{level}"><g id="tower-wobble-{index}"><animateTransform attributeName="transform" type="translate" additive="sum" values="{translations}" keyTimes="{key_times}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="tower-squish-{index}"><animateTransform attributeName="transform" type="scale" additive="sum" values="{scales}" keyTimes="{key_times}" dur="{fmt(total)}s" repeatCount="indefinite"/><path d="{shadow}" fill="#000" opacity=".22" filter="url(#blur4)"/><!-- TOWER_FRONT_FACE --><polygon points="{front}" fill="{LEVEL_FRONT[level]}" stroke="#4d6f8d" stroke-opacity=".30"/><!-- TOWER_SIDE_FACE --><polygon points="{side}" fill="{LEVEL_SIDE[level]}" stroke="#34506d" stroke-opacity=".28"/><!-- TOWER_TOP_FACE --><polygon points="{top_face}" fill="{LEVEL_TOP[level]}" stroke="#b4fbff" stroke-opacity=".40" stroke-width="1"/><path d="M{-half+2} {top+4}H{half-2}" stroke="#e7ffff" stroke-opacity=".10"/>{''.join(studs)}</g></g></g>'''


def _defs() -> str:
    return '''<defs>
  <linearGradient id="worldBg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#01040a"/><stop offset=".46" stop-color="#06101c"/><stop offset="1" stop-color="#02030a"/></linearGradient>
  <radialGradient id="greenNear" cx="28%" cy="20%" r="80%"><stop offset="0" stop-color="#d4ffd6"/><stop offset=".14" stop-color="#78f67e"/><stop offset=".52" stop-color="#28a93f"/><stop offset=".82" stop-color="#14642c"/><stop offset="1" stop-color="#073316"/></radialGradient>
  <radialGradient id="greenFar" cx="28%" cy="22%" r="80%"><stop offset="0" stop-color="#8bea90"/><stop offset=".50" stop-color="#1f8534"/><stop offset="1" stop-color="#0b4020"/></radialGradient>
  <radialGradient id="torsoGreen" cx="32%" cy="18%" r="83%"><stop offset="0" stop-color="#a8ffae"/><stop offset=".18" stop-color="#5fe46a"/><stop offset=".54" stop-color="#20933b"/><stop offset=".84" stop-color="#0e5728"/><stop offset="1" stop-color="#072f18"/></radialGradient>
  <radialGradient id="trapGreen" cx="44%" cy="26%" r="80%"><stop offset="0" stop-color="#a8fcae"/><stop offset=".45" stop-color="#2c9c45"/><stop offset="1" stop-color="#0b4923"/></radialGradient>
  <radialGradient id="pecGreen" cx="42%" cy="32%" r="70%"><stop offset="0" stop-color="#8dfa97"/><stop offset=".58" stop-color="#258f3b"/><stop offset="1" stop-color="#145829"/></radialGradient>
  <linearGradient id="legGreen"><stop offset="0" stop-color="#58d866"/><stop offset="1" stop-color="#0d5b28"/></linearGradient>
  <radialGradient id="faceGreen" cx="35%" cy="20%" r="85%"><stop offset="0" stop-color="#8ff398"/><stop offset=".55" stop-color="#2a9d41"/><stop offset="1" stop-color="#0c4b22"/></radialGradient>
  <linearGradient id="neckGreen"><stop offset="0" stop-color="#57d765"/><stop offset="1" stop-color="#125527"/></linearGradient>
  <radialGradient id="fistGreen" cx="28%" cy="22%" r="80%"><stop offset="0" stop-color="#aaffac"/><stop offset=".47" stop-color="#39b84d"/><stop offset="1" stop-color="#0b4a21"/></radialGradient>
  <linearGradient id="shorts"><stop offset="0" stop-color="#2b3243"/><stop offset=".6" stop-color="#171b28"/><stop offset="1" stop-color="#0b0e18"/></linearGradient>
  <linearGradient id="energy"><stop offset="0" stop-color="#79f4ff"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#b17aff"/></linearGradient>
  <filter id="softGlow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter><filter id="titanShadow" x="-40%" y="-40%" width="180%" height="180%"><feDropShadow dx="0" dy="4" stdDeviation="3" flood-color="#000" flood-opacity=".42"/></filter><filter id="blur4"><feGaussianBlur stdDeviation="4"/></filter>
  <linearGradient id="horizon"><stop offset="0" stop-color="#6ee7ff" stop-opacity="0"/><stop offset=".5" stop-color="#6ee7ff" stop-opacity=".38"/><stop offset="1" stop-color="#b784ff" stop-opacity="0"/></linearGradient>
  <pattern id="deck" width="72" height="28" patternUnits="userSpaceOnUse"><path d="M0 28L36 0L72 28M36 0V56" fill="none" stroke="#72a7ff" stroke-opacity=".045" stroke-width=".8"/></pattern>
</defs>'''


def render_activity_world(cells: list[Cell]) -> str:
    weeks = group_weeks(cells)
    if len(weeks) < 2:
        raise ValueError('activity world requires at least two week columns')
    frames, arrivals = build_frames(weeks)
    total = frames[-1].t
    frame_key_times = ';'.join(fmt(frame.t / total) for frame in frames)
    camera = camera_values(frames, len(weeks))
    reactive: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for index, events in arrivals.items():
        reactive[index].extend(events)
        for neighbor in (index - 1, index + 1):
            if 0 <= neighbor < len(weeks):
                reactive[neighbor].extend((moment + .045, amplitude * .26) for moment, amplitude in events)
    towers = ''.join(_tower(i, week, len(weeks), reactive.get(i, []), total) for i, week in enumerate(weeks))
    stars = ''.join(f'<circle cx="{31+(i*181)%1541}" cy="{125+(i*97)%320}" r="{fmt(.55+(i%3)*.32)}" fill="#b9f8ff" opacity="{fmt(.14+(i%5)*.055)}"/>' for i in range(48))
    movement_states = classify_steps([week.height for week in weeks]) + classify_steps([week.height for week in reversed(weeks)])
    counts = {state: movement_states.count(state) for state in ('jump', 'climb', 'sprint')}
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 820" role="img" aria-label="Cinematic 3D contribution activity world with TITAN traversing real GitHub activity terrain">{_defs()}<rect width="1600" height="820" rx="26" fill="url(#worldBg)"/><rect y="392" width="1600" height="428" fill="url(#deck)"/><path d="M52 390H1548" stroke="url(#horizon)"/>{stars}<g font-family="IBM Plex Mono,JetBrains Mono,ui-monospace,monospace"><text x="62" y="62" fill="#e2fcff" font-size="20" font-weight="700" letter-spacing="3.5">ACTIVITY WORLD // TITAN RUN</text><text x="62" y="90" fill="#70869b" font-size="10.5" letter-spacing="1.8">REAL GITHUB CONTRIBUTION SIGNAL → CINEMATIC FOLLOW-CAM BLOCK TERRAIN</text><text x="1538" y="62" text-anchor="end" fill="#6ee7b7" font-size="10.5" letter-spacing="1.6">● LIVE TERRAIN</text><text x="1538" y="90" text-anchor="end" fill="#64778b" font-size="9.5">JUMP {counts['jump']:02d} // CLIMB {counts['climb']:02d} // SPRINT {counts['sprint']:02d}</text></g><g id="camera-follow"><animateTransform attributeName="transform" type="translate" values="{camera}" keyTimes="{frame_key_times}" dur="{fmt(total)}s" repeatCount="indefinite"/><g id="terrain"><!-- COLUMN_SETTLE -->{towers}</g>{render_titan(frames, total)}</g><g font-family="IBM Plex Mono,JetBrains Mono,ui-monospace,monospace"><rect x="57" y="731" width="1486" height="52" rx="13" fill="#07111f" fill-opacity=".72" stroke="#264561" stroke-opacity=".42"/><text x="80" y="751" fill="#879aad" font-size="9.4" letter-spacing="1.5">TERRAIN LOGIC</text><text x="80" y="771" fill="#d1edf2" font-size="10.6">rough → leap  //  small rise → grab + pull  //  3+ flat → sprint  //  impact → squish + overshoot + damp → exact data height</text><text x="1517" y="763" text-anchor="end" fill="#86f8ff" font-size="9.4" letter-spacing="1.4">LOOP {fmt(total)}s</text></g></svg>'''
