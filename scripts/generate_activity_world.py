#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from activity_world_model import (  # noqa: E402
    Cell,
    Frame,
    RouteStep,
    Week,
    build_frames,
    build_route,
    classify_steps,
    group_weeks,
    parse_cells,
)
from activity_world_render import render_activity_world  # noqa: E402

INPUT = Path(os.environ.get('CONTRIBUTION_SVG', 'dist/activity-source.svg'))
OUTPUT = Path(os.environ.get('ACTIVITY_WORLD_OUT', 'assets/activity-world.svg'))


def main() -> int:
    if not INPUT.is_file():
        print(f'activity-world: missing input {INPUT}', file=sys.stderr)
        return 2
    cells = parse_cells(INPUT.read_text(encoding='utf-8'))
    output = render_activity_world(cells)
    ET.fromstring(output)
    lower = output.lower()
    for token in ('<script', 'javascript:', 'onload=', 'onclick=', 'onerror=', 'foreignobject'):
        if token in lower:
            raise RuntimeError(f'unsafe output token: {token}')
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(output, encoding='utf-8')
    print(f'wrote {OUTPUT} from {len(cells)} contribution cells / {len(group_weeks(cells))} week columns')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
