#!/usr/bin/env python3
from __future__ import annotations

import dataclasses
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

INPUT = Path(os.environ.get("CONTRIBUTION_SVG", "dist/activity-source.svg"))
OUTPUT = Path(os.environ.get("ACTIVITY_WORLD_OUT", "assets/activity-world.svg"))

LEVEL_HEIGHT = {0: 46, 1: 66, 2: 86, 3: 110, 4: 138}
LEVEL_TOP = {0: "#102238", 1: "#123c4b", 2: "#15577a", 3: "#285bd8", 4: "#8756d9"}
LEVEL_FRONT = {0: "#071321", 1: "#0b2730", 2: "#10364f", 3: "#193774", 4: "#452d73"}
LEVEL_SIDE = {0: "#050d18", 1: "#081a21", 2: "#0b2638", 3: "#112752", 4: "#332153"}
DAY_COLORS = {0: "#162235", 1: "#1c6b73", 2: "#1c9ab3", 3: "#4a7bff", 4: "#c084fc"}


@dataclasses.dataclass(frozen=True)
class Cell:
    x: float
    y: float
    level: int


@dataclasses.dataclass(frozen=True)
class Week:
    x: float
    levels: tuple[int, ...]

    @property
    def score(self) -> int:
        return sum(self.levels)

    @property
    def terrain_level(self) -> int:
        score = self.score
        if score <= 0:
            return 0
        if score <= 2:
            return 1
        if score <= 5:
            return 2
        if score <= 9:
            return 3
        return 4

    @property
    def height(self) -> int:
        return LEVEL_HEIGHT[self.terrain_level]


@dataclasses.dataclass(frozen=True)
class RouteStep:
    source: int
    target: int
    state: str


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_cells(svg_text: str) -> list[Cell]:
    """Extract only contribution-cell geometry and intensity from a Platane/snk SVG."""
    class_to_level: dict[str, int] = {}
    for match in re.finditer(
        r"\.c\.([A-Za-z0-9_-]+)\s*\{[^{}]*?fill\s*:\s*var\(--c([0-4])\)",
        svg_text,
        flags=re.DOTALL,
    ):
        class_to_level[match.group(1)] = int(match.group(2))

    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as exc:
        raise ValueError(f"invalid contribution SVG: {exc}") from exc

    cells: list[Cell] = []
    for element in root.iter():
        if _local_name(element.tag) != "rect":
            continue
        classes = element.attrib.get("class", "").split()
        if "c" not in classes:
            continue

        level = 0
        for token in classes:
            if token in class_to_level:
                level = class_to_level[token]
                break

        inline = element.attrib.get("style", "")
        inline_level = re.search(r"var\(--c([0-4])\)", inline)
        if inline_level:
            level = int(inline_level.group(1))

        try:
            x = float(element.attrib.get("x", "nan"))
            y = float(element.attrib.get("y", "nan"))
        except ValueError:
            continue
        if x != x or y != y:
            continue

        cells.append(Cell(x=x, y=y, level=max(0, min(4, level))))

    if not cells:
        raise ValueError("no contribution cells found in SVG")
    return cells


def group_weeks(cells: list[Cell]) -> list[Week]:
    grouped: dict[float, dict[float, int]] = defaultdict(dict)
    for cell in cells:
        x = round(cell.x, 3)
        y = round(cell.y, 3)
        grouped[x][y] = max(grouped[x].get(y, 0), cell.level)

    xs = sorted(grouped)
    if not xs:
        return []

    all_ys = sorted({y for per_week in grouped.values() for y in per_week})
    if len(all_ys) > 7:
        all_ys = all_ys[:7]

    weeks: list[Week] = []
    for x in xs:
        levels = tuple(grouped[x].get(y, 0) for y in all_ys)
        weeks.append(Week(x=x, levels=levels))
    return weeks


def terrain_height(level: int) -> int:
    return LEVEL_HEIGHT[max(0, min(4, int(level)))]


def _flat_transition_indices(heights: list[int]) -> set[int]:
    result: set[int] = set()
    start = 0
    while start < len(heights):
        end = start + 1
        while end < len(heights) and heights[end] == heights[start]:
            end += 1
        if end - start >= 3:
            result.update(range(start, end - 1))
        start = end
    return result


def classify_steps(heights: list[int]) -> list[str]:
    if len(heights) < 2:
        return []
    flat = _flat_transition_indices(heights)
    states: list[str] = []
    for index, (current, target) in enumerate(zip(heights, heights[1:])):
        if index in flat:
            states.append("sprint")
        elif target > current and target - current <= 24:
            states.append("climb")
        else:
            states.append("jump")
    return states


def build_route(weeks: list[Week]) -> list[RouteStep]:
    heights = [week.height for week in weeks]
    forward_states = classify_steps(heights)
    reverse_states = classify_steps(list(reversed(heights)))

    route: list[RouteStep] = []
    for index, state in enumerate(forward_states):
        route.append(RouteStep(index, index + 1, state))
    for reverse_index, state in enumerate(reverse_states):
        source = len(weeks) - 1 - reverse_index
        route.append(RouteStep(source, source - 1, state))
    return route


def _fmt(value: float) -> str:
    if abs(value - round(value)) < 1e-8:
        return str(int(round(value)))
    return f"{value:.4f}".rstrip("0").rstrip(".")


def _position_for(index: int, week: Week, count: int) -> tuple[float, float]:
    canvas_width = 1600.0
    left = 104.0
    right = 104.0
    usable = canvas_width - left - right
    step = usable / max(1, count - 1)
    x = left + index * step
    baseline = 565.0
    y = baseline - week.height - 13.0
    return x, y


def _route_frames(weeks: list[Week]):
    if len(weeks) < 2:
        raise ValueError("need at least two contribution weeks")

    positions = [_position_for(i, week, len(weeks)) for i, week in enumerate(weeks)]
    times: list[float] = [0.0]
    points: list[tuple[float, float]] = [positions[0]]
    poses: list[tuple[float, float]] = [(1.0, 1.0)]
    dirs: list[int] = [1]
    states_at_frames: list[str] = ["idle"]
    arrivals: dict[int, list[tuple[float, float]]] = defaultdict(list)

    t = 0.0

    def add(dt: float, point: tuple[float, float], pose=(1.0, 1.0), direction=1, state="jump"):
        nonlocal t
        t += dt
        times.append(t)
        points.append(point)
        poses.append(pose)
        dirs.append(direction)
        states_at_frames.append(state)

    add(0.55, positions[0], (1.0, 1.0), 1, "idle")

    def transition(source: int, target: int, state: str, direction: int):
        sx, sy = positions[source]
        tx, ty = positions[target]
        if state == "sprint":
            add(0.10, (sx, sy + 2), (1.08, 0.92), direction, state)
            add(0.16, (tx, ty + 1), (1.11, 0.90), direction, state)
            add(0.08, (tx, ty), (1.0, 1.0), direction, state)
        elif state == "climb":
            approach_x = tx - direction * 11
            hang_y = ty + 18
            add(0.13, (sx, sy + 2), (1.10, 0.90), direction, state)
            add(0.16, (approach_x, hang_y), (0.94, 1.08), direction, state)
            add(0.18, (approach_x, hang_y), (1.04, 0.96), direction, state)
            add(0.18, (tx, ty + 5), (0.91, 1.12), direction, state)
            add(0.10, (tx, ty), (1.08, 0.92), direction, state)
            add(0.11, (tx, ty), (1.0, 1.0), direction, state)
        else:
            apex = min(sy, ty) - 40 - min(20, abs(ty - sy) * 0.25)
            mx = (sx + tx) / 2
            add(0.09, (sx, sy + 4), (1.12, 0.86), direction, state)
            add(0.20, (mx, apex), (0.90, 1.14), direction, state)
            add(0.17, (tx, ty + 4), (1.15, 0.84), direction, state)
            add(0.11, (tx, ty), (0.96, 1.04), direction, state)
            add(0.10, (tx, ty), (1.0, 1.0), direction, state)
        arrivals[target].append((t, 4.8 if state == "jump" else 3.4 if state == "climb" else 2.0))

    forward_states = classify_steps([w.height for w in weeks])
    for index, state in enumerate(forward_states):
        transition(index, index + 1, state, 1)

    end = positions[-1]
    add(0.18, (end[0] + 7, end[1] + 2), (1.18, 0.82), 1, "turn")
    add(0.28, end, (0.88, 1.12), -1, "turn")
    add(0.28, end, (1.0, 1.0), -1, "turn")

    reverse_heights = [w.height for w in reversed(weeks)]
    reverse_states = classify_steps(reverse_heights)
    for rev_index, state in enumerate(reverse_states):
        source = len(weeks) - 1 - rev_index
        transition(source, source - 1, state, -1)

    start = positions[0]
    add(0.18, (start[0] - 7, start[1] + 2), (1.18, 0.82), -1, "turn")
    add(0.28, start, (0.88, 1.12), 1, "turn")
    add(0.38, start, (1.0, 1.0), 1, "turn")

    return times, points, poses, dirs, arrivals, states_at_frames, t


def _column_wobble(events: list[tuple[float, float]], total: float) -> tuple[str, str]:
    frames: list[tuple[float, float]] = [(0.0, 0.0)]
    for event, amp in sorted(events):
        for offset, value in (
            (-0.07, 0.0),
            (0.0, amp),
            (0.07, -amp * 0.55),
            (0.14, amp * 0.28),
            (0.24, -amp * 0.10),
            (0.34, 0.0),
        ):
            moment = max(0.0, min(total, event + offset))
            frames.append((moment, value))
    frames.append((total, 0.0))
    merged: dict[float, float] = {}
    for moment, value in frames:
        merged[round(moment, 4)] = value
    ordered = sorted(merged.items())
    key_times = ";".join(_fmt(moment / total) for moment, _ in ordered)
    values = ";".join(f"0 {_fmt(value)}" for _, value in ordered)
    return key_times, values


def _state_counts(weeks: list[Week]) -> dict[str, int]:
    states = classify_steps([w.height for w in weeks]) + classify_steps([w.height for w in reversed(weeks)])
    result = {"jump": 0, "climb": 0, "sprint": 0}
    for state in states:
        result[state] = result.get(state, 0) + 1
    return result


def render_activity_world(cells: list[Cell]) -> str:
    weeks = group_weeks(cells)
    if len(weeks) < 2:
        raise ValueError("activity world requires at least two week columns")

    times, points, poses, directions, arrivals, state_frames, total = _route_frames(weeks)
    counts = _state_counts(weeks)

    reactive: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for index, events in arrivals.items():
        reactive[index].extend(events)
        for neighbor in (index - 1, index + 1):
            if 0 <= neighbor < len(weeks):
                reactive[neighbor].extend((moment + 0.035, amp * 0.28) for moment, amp in events)

    translate_values = ";".join(f"{_fmt(x)} {_fmt(y)}" for x, y in points)
    key_times = ";".join(_fmt(moment / total) for moment in times)
    pose_values = ";".join(f"{_fmt(sx)} {_fmt(sy)}" for sx, sy in poses)
    dir_values = ";".join(f"{direction} 1" for direction in directions)

    column_parts: list[str] = []
    count = len(weeks)
    for index, week in enumerate(weeks):
        x, _ = _position_for(index, week, count)
        width = max(15.0, min(25.0, 1300.0 / max(1, count)))
        half = width / 2
        depth = 6.0
        base = 578.0
        top = base - week.height
        level = week.terrain_level
        top_color = LEVEL_TOP[level]
        front_color = LEVEL_FRONT[level]
        side_color = LEVEL_SIDE[level]

        top_face = f"{x-half},{top} {x+half},{top} {x+half+depth},{top-depth} {x-half+depth},{top-depth}"
        front_face = f"{x-half},{top} {x+half},{top} {x+half},{base} {x-half},{base}"
        side_face = f"{x+half},{top} {x+half+depth},{top-depth} {x+half+depth},{base-depth} {x+half},{base}"

        wobble_times, wobble_values = _column_wobble(reactive.get(index, []), total)

        dots = []
        levels = week.levels or (0,)
        dot_count = min(7, len(levels))
        for day_index, day_level in enumerate(levels[:dot_count]):
            dx = x - half + 2.5 + day_index * max(1.7, (width - 5) / max(1, dot_count - 1))
            dots.append(
                f'<circle cx="{_fmt(dx)}" cy="{_fmt(top + 9)}" r="1.25" fill="{DAY_COLORS.get(day_level, DAY_COLORS[0])}" opacity=".95"/>'
            )

        column_parts.append(
            f'''<g id="terrain-{index}" data-week="{index}" data-level="{level}">
  <animateTransform attributeName="transform" type="translate" additive="sum"
    values="{wobble_values}" keyTimes="{wobble_times}" dur="{_fmt(total)}s" repeatCount="indefinite"/>
  <polygon points="{front_face}" fill="{front_color}" stroke="#28435f" stroke-opacity=".34" stroke-width=".8"/>
  <polygon points="{side_face}" fill="{side_color}" stroke="#28435f" stroke-opacity=".22" stroke-width=".7"/>
  <polygon points="{top_face}" fill="{top_color}" stroke="#9deeff" stroke-opacity=".28" stroke-width=".8"/>
  <rect x="{_fmt(x-half+1.5)}" y="{_fmt(top+4)}" width="{_fmt(width-3)}" height="1.1" rx=".55" fill="#d5fbff" opacity=".12"/>
  {''.join(dots)}
</g>'''
        )

    stars = []
    for i in range(42):
        x = 37 + ((i * 173) % 1511)
        y = 112 + ((i * 89) % 300)
        r = 0.7 + (i % 3) * 0.35
        opacity = 0.18 + (i % 5) * 0.07
        stars.append(f'<circle cx="{x}" cy="{y}" r="{_fmt(r)}" fill="#b8f7ff" opacity="{_fmt(opacity)}"/>')

    brick = f'''
<!-- BRICK_STATE_JUMP count={counts.get("jump", 0)} -->
<!-- BRICK_STATE_CLIMB count={counts.get("climb", 0)} -->
<!-- BRICK_STATE_SPRINT count={counts.get("sprint", 0)} -->
<!-- BRICK_ROUTE_FORWARD -->
<!-- BRICK_ROUTE_REVERSE -->
<g id="brick-motion" transform="translate({_fmt(points[0][0])} {_fmt(points[0][1])})">
  <animateTransform attributeName="transform" type="translate"
    values="{translate_values}" keyTimes="{key_times}" dur="{_fmt(total)}s" repeatCount="indefinite"/>
  <g id="brick-direction">
    <animateTransform attributeName="transform" type="scale" calcMode="discrete"
      values="{dir_values}" keyTimes="{key_times}" dur="{_fmt(total)}s" repeatCount="indefinite"/>
    <g id="brick-pose">
      <animateTransform attributeName="transform" type="scale" additive="sum"
        values="{pose_values}" keyTimes="{key_times}" dur="{_fmt(total)}s" repeatCount="indefinite"/>
      <ellipse cx="0" cy="10" rx="26" ry="33" fill="url(#brickGel)" stroke="#a7f6ff" stroke-width="1.4"/>
      <path d="M-24 -6 C-42 -10 -51 2 -47 14 C-44 24 -34 25 -25 18 L-17 10 Z" fill="url(#brickArmor)" stroke="#b8f8ff" stroke-opacity=".55"/>
      <path d="M24 -6 C42 -10 51 2 47 14 C44 24 34 25 25 18 L17 10 Z" fill="url(#brickArmor)" stroke="#b8f8ff" stroke-opacity=".55"/>
      <ellipse cx="-47" cy="16" rx="10" ry="13" fill="#2352b7" stroke="#7ff0ff" stroke-width="1"/>
      <ellipse cx="47" cy="16" rx="10" ry="13" fill="#2352b7" stroke="#7ff0ff" stroke-width="1"/>
      <path d="M-23 -5 Q0 -20 23 -5 L19 8 Q0 1 -19 8 Z" fill="#111b42" stroke="#9f86ff" stroke-width="1.2"/>
      <path d="M-15 -3 Q0 -9 15 -3 L11 3 Q0 0 -11 3 Z" fill="url(#visor)" filter="url(#softGlow)"/>
      <path d="M-14 29 Q-9 43 -17 55" fill="none" stroke="#406fe3" stroke-width="9" stroke-linecap="round"/>
      <path d="M14 29 Q9 43 17 55" fill="none" stroke="#406fe3" stroke-width="9" stroke-linecap="round"/>
      <ellipse cx="-18" cy="57" rx="12" ry="5" fill="#13213f" stroke="#7ff0ff" stroke-opacity=".55"/>
      <ellipse cx="18" cy="57" rx="12" ry="5" fill="#13213f" stroke="#7ff0ff" stroke-opacity=".55"/>
      <path d="M-17 4 Q0 14 17 4 L13 25 Q0 34 -13 25 Z" fill="#101a37" opacity=".76"/>
      <path d="M-10 10 H10 M-7 18 H7" stroke="#7ff0ff" stroke-opacity=".42" stroke-width="1"/>
      <circle cx="-6" cy="-2" r="1.8" fill="#fff" opacity=".78"/>
      <circle cx="9" cy="4" r="1.2" fill="#fff" opacity=".42"/>
      <g opacity=".72">
        <animateTransform attributeName="transform" type="rotate" values="-5 0 18;7 0 18;-5 0 18" dur=".42s" repeatCount="indefinite"/>
        <path d="M-28 10 Q-37 20 -39 31" fill="none" stroke="#345ed1" stroke-width="7.5" stroke-linecap="round"/>
      </g>
      <g opacity=".72">
        <animateTransform attributeName="transform" type="rotate" values="6 0 18;-7 0 18;6 0 18" dur=".42s" repeatCount="indefinite"/>
        <path d="M28 10 Q37 20 39 31" fill="none" stroke="#345ed1" stroke-width="7.5" stroke-linecap="round"/>
      </g>
    </g>
  </g>
</g>'''

    state_summary = f"JUMP {counts.get('jump',0):02d} // CLIMB {counts.get('climb',0):02d} // SPRINT {counts.get('sprint',0):02d}"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 720" role="img" aria-label="Animated contribution Activity World with BRICK traversing real public GitHub activity terrain">
<defs>
  <linearGradient id="worldBg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#02050d"/><stop offset=".52" stop-color="#06111f"/><stop offset="1" stop-color="#03040b"/></linearGradient>
  <linearGradient id="horizon" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7ff0ff" stop-opacity="0"/><stop offset=".5" stop-color="#7ff0ff" stop-opacity=".52"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></linearGradient>
  <radialGradient id="brickGel" cx="35%" cy="22%" r="82%"><stop offset="0" stop-color="#bffcff"/><stop offset=".18" stop-color="#61e8f5"/><stop offset=".54" stop-color="#376fe4"/><stop offset=".84" stop-color="#653bb9"/><stop offset="1" stop-color="#251a49"/></radialGradient>
  <linearGradient id="brickArmor" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16396f"/><stop offset=".45" stop-color="#285fd4"/><stop offset="1" stop-color="#6737a8"/></linearGradient>
  <linearGradient id="visor" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7ff0ff"/><stop offset=".5" stop-color="#fff"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
  <filter id="softGlow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <pattern id="floorGrid" width="52" height="22" patternUnits="userSpaceOnUse"><path d="M0 22L26 0L52 22M26 0V44" fill="none" stroke="#6ba7ff" stroke-opacity=".045" stroke-width=".8"/></pattern>
</defs>

<rect width="1600" height="720" rx="28" fill="url(#worldBg)"/>
<rect x="1" y="1" width="1598" height="718" rx="27" fill="none" stroke="#7ff0ff" stroke-opacity=".20"/>
<rect y="390" width="1600" height="330" fill="url(#floorGrid)" opacity=".72"/>
<path d="M55 388H1545" stroke="url(#horizon)" stroke-width="1.3"/>
{''.join(stars)}

<g font-family="IBM Plex Mono,JetBrains Mono,ui-monospace,monospace">
  <text x="64" y="66" fill="#dffcff" font-size="20" font-weight="700" letter-spacing="3.4">ACTIVITY WORLD // BRICK RUN</text>
  <text x="64" y="94" fill="#687d93" font-size="10.5" letter-spacing="1.9">REAL CONTRIBUTION SIGNAL → WEEKLY TERRAIN // FORWARD + REVERSE LOOP</text>
  <text x="1535" y="66" text-anchor="end" fill="#6ee7b7" font-size="10.5" letter-spacing="1.7">● TERRAIN LINKED</text>
  <text x="1535" y="94" text-anchor="end" fill="#66768b" font-size="9.5" letter-spacing="1.4">{html.escape(state_summary)}</text>
</g>

<g id="terrain">
<!-- COLUMN_SETTLE -->
{''.join(column_parts)}
</g>

{brick}

<g font-family="IBM Plex Mono,JetBrains Mono,ui-monospace,monospace">
  <rect x="58" y="630" width="1484" height="48" rx="13" fill="#07111f" fill-opacity=".78" stroke="#234464" stroke-opacity=".45"/>
  <text x="82" y="650" fill="#8396ac" font-size="9.5" letter-spacing="1.6">BRICK BEHAVIOR</text>
  <text x="82" y="668" fill="#ccecf2" font-size="10.5">jump rough terrain  //  pull onto small rises  //  sprint 3+ flat pillars  //  impact → gel wobble → exact data height</text>
  <text x="1517" y="659" text-anchor="end" fill="#7ff0ff" font-size="9.5" letter-spacing="1.5">LOOP {_fmt(total)}s</text>
</g>
</svg>'''
    return svg


def main() -> int:
    if not INPUT.is_file():
        print(f"activity-world: missing input {INPUT}", file=sys.stderr)
        return 2
    svg_text = INPUT.read_text(encoding="utf-8")
    cells = parse_cells(svg_text)
    output = render_activity_world(cells)
    ET.fromstring(output)
    lowered = output.lower()
    forbidden = ("<script", "javascript:", "onload=", "onclick=", "onerror=")
    for token in forbidden:
        if token in lowered:
            raise RuntimeError(f"unsafe output token: {token}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"wrote {OUTPUT} from {len(cells)} contribution cells / {len(group_weeks(cells))} week columns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
