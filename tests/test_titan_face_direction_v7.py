import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import activity_world_model as model
import activity_world_titan as titan


class TitanFaceDirectionV7Tests(unittest.TestCase):
    def _output(self):
        frames = [
            model.Frame(0.0, 0.0, 0.0, 'idle', 1, phase=0.0, contact='both'),
            model.Frame(1.0, 12.0, 0.0, 'idle', 1, phase=1.0, contact='both'),
        ]
        return titan.render_titan(frames, 1.0)

    def test_face_is_unmistakably_side_facing_toward_positive_x(self):
        output = self._output()
        for marker in (
            'TRUE_SIDE_FACING_PROFILE_V7',
            'id="titan-face-silhouette-forward"',
            'id="titan-nose-silhouette"',
            'id="titan-chin-forward"',
            'id="titan-brow-ridge-forward"',
        ):
            self.assertIn(marker, output)
        self.assertIn('id="titan-eye-far" opacity=".08"', output)
        self.assertIn('id="titan-head" transform="translate(16 -156)"', output)

    def test_chest_and_shoulders_share_the_same_forward_depth_cue(self):
        output = self._output()
        self.assertIn('id="titan-pec-far" transform="translate(-15 0) scale(.42 1)"', output)
        self.assertIn('id="titan-pec-near" transform="translate(14 0) scale(1.16 1)"', output)
        self.assertIn('id="far-shoulder" transform="translate(-36 -92) scale(.58)"', output)
        self.assertIn('id="near-shoulder" transform="translate(84 -85) scale(1.12)"', output)
        self.assertIn('id="titan-sternum-forward" d="M22 -84Q28 -50 23 -13"', output)


if __name__ == '__main__':
    unittest.main()
