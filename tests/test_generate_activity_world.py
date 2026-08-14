import importlib.util
import pathlib
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1] if '__file__' in globals() else pathlib.Path('/tmp/v3build')
GEN = ROOT / 'scripts' / 'generate_activity_world.py'
if not GEN.exists():
    GEN = pathlib.Path('/tmp/v3build/generate_activity_world.py')
spec = importlib.util.spec_from_file_location('activity', GEN)
activity = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = activity
assert spec.loader is not None
spec.loader.exec_module(activity)


def fixture_svg():
    styles = '.c.a{fill:var(--c1)}.c.b{fill:var(--c2)}.c.c3x{fill:var(--c3)}.c.d{fill:var(--c4)}'
    rects = []
    levels = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0],
        [2, 2, 1, 1, 0, 0, 0],
        [2, 2, 1, 1, 0, 0, 0],
        [2, 2, 1, 1, 0, 0, 0],
        [4, 4, 3, 2, 1, 1, 1],
    ]
    token = {0: '', 1: 'a', 2: 'b', 3: 'c3x', 4: 'd'}
    for x_idx, week in enumerate(levels):
        for y_idx, level in enumerate(week):
            cls = 'c' if level == 0 else f'c {token[level]}'
            rects.append(f'<rect class="{cls}" x="{x_idx*16}" y="{y_idx*16}" width="12" height="12"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg"><style>{styles}</style><script>alert(1)</script>{"".join(rects)}</svg>'


class ActivityWorldTests(unittest.TestCase):
    def test_parse_cells_uses_expected_geometry_and_levels(self):
        cells = activity.parse_cells(fixture_svg())
        self.assertEqual(len(cells), 77)
        self.assertEqual(max(cell.level for cell in cells), 4)
        self.assertEqual(min(cell.level for cell in cells), 0)

    def test_group_weeks_preserves_week_columns(self):
        weeks = activity.group_weeks(activity.parse_cells(fixture_svg()))
        self.assertEqual(len(weeks), 11)
        self.assertTrue(all(len(week.levels) == 7 for week in weeks))

    def test_flat_run_becomes_sprint(self):
        self.assertEqual(activity.classify_steps([42, 42, 42, 42]), ['sprint', 'sprint', 'sprint'])

    def test_small_rise_becomes_climb(self):
        self.assertEqual(activity.classify_steps([42, 68]), ['climb'])
        self.assertEqual(activity.classify_steps([68, 98]), ['climb'])

    def test_large_or_downward_change_becomes_jump(self):
        self.assertEqual(activity.classify_steps([42, 98]), ['jump'])
        self.assertEqual(activity.classify_steps([132, 68]), ['jump'])

    def test_route_is_bidirectional(self):
        weeks = activity.group_weeks(activity.parse_cells(fixture_svg()))
        route = activity.build_route(weeks)
        self.assertEqual(route[0].source, 0)
        self.assertEqual(route[0].target, 1)
        self.assertEqual(route[-1].target, 0)
        self.assertEqual(len(route), (len(weeks) - 1) * 2)

    def test_parser_rejects_dtd_and_nonfinite_geometry(self):
        with self.assertRaises(ValueError):
            activity.parse_cells('<!DOCTYPE svg><svg/>')
        bad = '<svg xmlns="http://www.w3.org/2000/svg"><style>.c.a{fill:var(--c1)}</style><rect class="c a" x="nan" y="0"/></svg>'
        with self.assertRaises(ValueError):
            activity.parse_cells(bad)

    def test_render_is_valid_script_free_3d_svg_with_full_choreography(self):
        output = activity.render_activity_world(activity.parse_cells(fixture_svg()))
        ET.fromstring(output)
        lower = output.lower()
        self.assertNotIn('<script', lower)
        self.assertNotIn('javascript:', lower)
        self.assertNotIn('onload=', lower)
        for marker in (
            'BRICK_ROUTE_FORWARD', 'BRICK_ROUTE_REVERSE',
            'COLUMN_SETTLE', 'BRICK_STATE_JUMP', 'BRICK_STATE_CLIMB',
            'BRICK_STATE_SPRINT', 'BRICK_STATE_TURN',
            'TITAN_BODY_DEPTH', 'TOWER_TOP_FACE', 'TOWER_FRONT_FACE', 'TOWER_SIDE_FACE',
            'camera-follow', 'ACTIVITY WORLD // TITAN RUN',
        ):
            self.assertIn(marker, output)


if __name__ == '__main__':
    unittest.main()
