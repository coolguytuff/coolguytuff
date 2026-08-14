import importlib.util
import pathlib
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("activity", ROOT / "scripts" / "generate_activity_world.py")
activity = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = activity
assert spec.loader is not None
spec.loader.exec_module(activity)


def fixture_svg():
    styles = ".c.a{fill:var(--c1)}.c.b{fill:var(--c2)}.c.c3x{fill:var(--c3)}.c.d{fill:var(--c4)}"
    rects = []
    levels = [
        [0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0],
        [2, 2, 1, 1, 0, 0, 0],
        [4, 4, 3, 2, 1, 1, 1],
    ]
    token = {0: "", 1: "a", 2: "b", 3: "c3x", 4: "d"}
    for x_idx, week in enumerate(levels):
        for y_idx, level in enumerate(week):
            cls = "c" if level == 0 else f"c {token[level]}"
            rects.append(f'<rect class="{cls}" x="{x_idx*16}" y="{y_idx*16}" width="12" height="12"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg"><style>{styles}</style><script>alert(1)</script>{"".join(rects)}</svg>'


class ActivityWorldTests(unittest.TestCase):
    def test_parse_cells_uses_expected_geometry_and_levels(self):
        cells = activity.parse_cells(fixture_svg())
        self.assertEqual(len(cells), 42)
        self.assertEqual(max(cell.level for cell in cells), 4)
        self.assertEqual(min(cell.level for cell in cells), 0)

    def test_group_weeks_preserves_week_columns(self):
        weeks = activity.group_weeks(activity.parse_cells(fixture_svg()))
        self.assertEqual(len(weeks), 6)
        self.assertTrue(all(len(week.levels) == 7 for week in weeks))

    def test_flat_run_becomes_sprint(self):
        self.assertEqual(activity.classify_steps([46, 46, 46, 46]), ["sprint", "sprint", "sprint"])

    def test_small_rise_becomes_climb(self):
        self.assertEqual(activity.classify_steps([46, 66]), ["climb"])

    def test_large_or_downward_change_becomes_jump(self):
        self.assertEqual(activity.classify_steps([46, 110]), ["jump"])
        self.assertEqual(activity.classify_steps([110, 66]), ["jump"])

    def test_route_is_bidirectional(self):
        weeks = activity.group_weeks(activity.parse_cells(fixture_svg()))
        route = activity.build_route(weeks)
        self.assertEqual(route[0].source, 0)
        self.assertEqual(route[0].target, 1)
        self.assertEqual(route[-1].target, 0)
        self.assertEqual(len(route), (len(weeks) - 1) * 2)

    def test_render_is_valid_script_free_svg_with_markers(self):
        output = activity.render_activity_world(activity.parse_cells(fixture_svg()))
        ET.fromstring(output)
        lower = output.lower()
        self.assertNotIn("<script", lower)
        self.assertNotIn("javascript:", lower)
        self.assertNotIn("onload=", lower)
        self.assertIn("BRICK_ROUTE_FORWARD", output)
        self.assertIn("BRICK_ROUTE_REVERSE", output)
        self.assertIn("COLUMN_SETTLE", output)
        self.assertIn("BRICK_STATE_JUMP", output)
        self.assertIn("BRICK_STATE_SPRINT", output)
        self.assertIn("ACTIVITY WORLD // BRICK RUN", output)


if __name__ == "__main__":
    unittest.main()
