from __future__ import annotations

import dataclasses
import math
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

MAX_INPUT_BYTES = 3_000_000
CANVAS_W = 1600.0
BASE_Y = 620.0
LEFT = 720.0
RIGHT = 720.0
TRACK_STEP = 58.0
LEVEL_HEIGHT = {0: 42, 1: 68, 2: 98, 3: 132, 4: 174}


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


@dataclasses.dataclass(frozen=True)
class Frame:
    t: float
    x: float
    y: float
    state: str
    direction: int
    sx: float = 1.0
    sy: float = 1.0


def _local(tag: str) -> str:
    return tag.rsplit('}', 1)[-1]


def fmt(value: float) -> str:
    if abs(value - round(value)) < 1e-7:
        return str(int(round(value)))
    return f'{value:.4f}'.rstrip('0').rstrip('.')


def parse_cells(svg_text: str) -> list[Cell]:
    if len(svg_text.encode('utf-8')) > MAX_INPUT_BYTES:
        raise ValueError('contribution SVG is too large')
    lower = svg_text.lower()
    if '<!doctype' in lower or '<!entity' in lower:
        raise ValueError('DTD/entity declarations are not accepted')

    class_to_level: dict[str, int] = {}
    for match in re.finditer(
        r'\.c\.([A-Za-z0-9_-]+)\s*\{[^{}]*?fill\s*:\s*var\(--c([0-4])\)',
        svg_text,
        re.S,
    ):
        class_to_level[match.group(1)] = int(match.group(2))

    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as exc:
        raise ValueError(f'invalid contribution SVG: {exc}') from exc

    cells: list[Cell] = []
    for element in root.iter():
        if _local(element.tag) != 'rect':
            continue
        classes = element.attrib.get('class', '').split()
        if 'c' not in classes:
            continue

        level = 0
        for token in classes:
            if token in class_to_level:
                level = class_to_level[token]
                break
        inline_level = re.search(r'var\(--c([0-4])\)', element.attrib.get('style', ''))
        if inline_level:
            level = int(inline_level.group(1))

        try:
            x = float(element.attrib.get('x', 'nan'))
            y = float(element.attrib.get('y', 'nan'))
        except ValueError:
            continue
        if not (math.isfinite(x) and math.isfinite(y)):
            continue
        if abs(x) > 100_000 or abs(y) > 100_000:
            continue
        cells.append(Cell(x, y, max(0, min(4, level))))

    if not cells:
        raise ValueError('no contribution cells found in SVG')
    return cells


def group_weeks(cells: list[Cell]) -> list[Week]:
    grouped: dict[float, dict[float, int]] = defaultdict(dict)
    for cell in cells:
        x = round(cell.x, 3)
        y = round(cell.y, 3)
        grouped[x][y] = max(grouped[x].get(y, 0), cell.level)
    ys = sorted({y for per_week in grouped.values() for y in per_week})[:7]
    return [Week(x, tuple(grouped[x].get(y, 0) for y in ys)) for x in sorted(grouped)]


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
    flat = _flat_transition_indices(heights)
    states: list[str] = []
    for index, (current, target) in enumerate(zip(heights, heights[1:])):
        if index in flat:
            states.append('sprint')
        elif target > current and target - current <= 32:
            states.append('climb')
        else:
            states.append('jump')
    return states


def build_route(weeks: list[Week]) -> list[RouteStep]:
    heights = [week.height for week in weeks]
    route: list[RouteStep] = []
    for index, state in enumerate(classify_steps(heights)):
        route.append(RouteStep(index, index + 1, state))
    reverse = list(reversed(heights))
    for reverse_index, state in enumerate(classify_steps(reverse)):
        source = len(weeks) - 1 - reverse_index
        route.append(RouteStep(source, source - 1, state))
    return route


def position(index: int, week: Week, count: int) -> tuple[float, float]:
    x = LEFT + index * TRACK_STEP
    perspective_raise = 8.0 * math.sin((index / max(1, count - 1)) * math.pi)
    return x, BASE_Y - week.height - perspective_raise


def world_width(count: int) -> float:
    return LEFT + max(0, count - 1) * TRACK_STEP + RIGHT


def camera_values(frames: list[Frame], count: int) -> str:
    min_x = min(0.0, CANVAS_W - world_width(count))
    values: list[str] = []
    for frame in frames:
        desired = CANVAS_W * 0.46 - frame.x
        camera_x = max(min_x, min(0.0, desired))
        values.append(f'{fmt(camera_x)} 0')
    return ';'.join(values)


def _append_frame(
    frames: list[Frame], dt: float, x: float, y: float, state: str, direction: int,
    sx: float = 1.0, sy: float = 1.0,
) -> None:
    t = (frames[-1].t if frames else 0.0) + dt
    frames.append(Frame(t, x, y, state, direction, sx, sy))


def build_frames(weeks: list[Week]) -> tuple[list[Frame], dict[int, list[tuple[float, float]]]]:
    if len(weeks) < 2:
        raise ValueError('need at least two contribution weeks')
    positions = [position(i, week, len(weeks)) for i, week in enumerate(weeks)]
    frames = [Frame(0.0, positions[0][0], positions[0][1], 'idle', 1)]
    arrivals: dict[int, list[tuple[float, float]]] = defaultdict(list)
    _append_frame(frames, .55, *positions[0], 'idle', 1)

    def transition(source: int, target: int, state: str, direction: int) -> None:
        sx, sy = positions[source]
        tx, ty = positions[target]
        if state == 'sprint':
            _append_frame(frames, .07, sx, sy + 4, 'sprint', direction, 1.13, .86)
            _append_frame(frames, .11, (sx + tx) / 2, (sy + ty) / 2 - 5, 'sprint', direction, 1.04, .96)
            _append_frame(frames, .11, tx, ty + 2, 'sprint', direction, 1.11, .89)
            _append_frame(frames, .06, tx, ty, 'sprint', direction)
            amplitude = 2.3
        elif state == 'climb':
            ledge_x = tx - direction * 11
            hang_y = ty + 29
            _append_frame(frames, .12, sx, sy + 5, 'climb', direction, 1.10, .88)
            _append_frame(frames, .16, ledge_x, hang_y, 'climb', direction, .92, 1.10)
            _append_frame(frames, .22, ledge_x, hang_y, 'climb', direction, 1.02, .98)
            _append_frame(frames, .20, tx, ty + 12, 'climb', direction, .90, 1.15)
            _append_frame(frames, .12, tx, ty + 3, 'climb', direction, 1.09, .90)
            _append_frame(frames, .10, tx, ty, 'climb', direction)
            amplitude = 4.0
        else:
            apex = min(sy, ty) - 50 - min(28, abs(ty - sy) * .30)
            midpoint = (sx + tx) / 2
            _append_frame(frames, .09, sx, sy + 7, 'jump', direction, 1.15, .82)
            _append_frame(frames, .16, (sx + midpoint) / 2, (sy + apex) / 2, 'jump', direction, .92, 1.12)
            _append_frame(frames, .15, midpoint, apex, 'jump', direction, .88, 1.18)
            _append_frame(frames, .15, (midpoint + tx) / 2, (apex + ty) / 2, 'jump', direction, .94, 1.10)
            _append_frame(frames, .11, tx, ty + 6, 'jump', direction, 1.18, .80)
            _append_frame(frames, .11, tx, ty, 'jump', direction, .97, 1.04)
            _append_frame(frames, .08, tx, ty, 'idle', direction)
            amplitude = 6.2
        arrivals[target].append((frames[-1].t, amplitude))

    for index, state in enumerate(classify_steps([week.height for week in weeks])):
        transition(index, index + 1, state, 1)

    end_x, end_y = positions[-1]
    _append_frame(frames, .16, end_x + 9, end_y + 5, 'turn', 1, 1.18, .80)
    _append_frame(frames, .18, end_x, end_y, 'turn', 1, .96, 1.06)
    _append_frame(frames, .20, end_x, end_y, 'turn', -1, 1.04, .96)
    _append_frame(frames, .20, end_x, end_y, 'idle', -1)

    reverse_states = classify_steps([week.height for week in reversed(weeks)])
    for reverse_index, state in enumerate(reverse_states):
        source = len(weeks) - 1 - reverse_index
        transition(source, source - 1, state, -1)

    start_x, start_y = positions[0]
    _append_frame(frames, .16, start_x - 9, start_y + 5, 'turn', -1, 1.18, .80)
    _append_frame(frames, .18, start_x, start_y, 'turn', -1, .96, 1.06)
    _append_frame(frames, .20, start_x, start_y, 'turn', 1, 1.04, .96)
    _append_frame(frames, .30, start_x, start_y, 'idle', 1)
    return frames, arrivals
