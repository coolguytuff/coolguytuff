import importlib.util
import pathlib
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).resolve().parents[1]
GEN=ROOT/'scripts'/'generate_activity_world.py'
spec=importlib.util.spec_from_file_location('activity',GEN)
activity=importlib.util.module_from_spec(spec); sys.modules[spec.name]=activity; assert spec.loader is not None; spec.loader.exec_module(activity)
sys.path.insert(0,str(ROOT/'scripts'))
import activity_world_model as model
import activity_world_render as render
import activity_world_titan as titan

def fixture_svg():
    styles='.c.a{fill:var(--c1)}.c.b{fill:var(--c2)}.c.c3x{fill:var(--c3)}.c.d{fill:var(--c4)}'; rects=[]
    levels=[[0]*7,[0]*7,[0]*7,[0]*7,[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,1,1,0,0,0,0],[2,2,1,1,0,0,0],[2,2,1,1,0,0,0],[2,2,1,1,0,0,0],[4,4,3,2,1,1,1]]; token={0:'',1:'a',2:'b',3:'c3x',4:'d'}
    for xi,week in enumerate(levels):
        for yi,level in enumerate(week):
            cls='c' if level==0 else f'c {token[level]}'; rects.append(f'<rect class="{cls}" x="{xi*16}" y="{yi*16}" width="12" height="12"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg"><style>{styles}</style><script>alert(1)</script>{"".join(rects)}</svg>'

class ActivityWorldTests(unittest.TestCase):
    def test_parse_group_and_route(self):
        cells=activity.parse_cells(fixture_svg()); self.assertEqual(len(cells),77); weeks=activity.group_weeks(cells); self.assertEqual(len(weeks),11); route=activity.build_route(weeks); self.assertEqual(route[0].target,1); self.assertEqual(route[-1].target,0)

    def test_step_classification(self):
        self.assertEqual(activity.classify_steps([42,42,42,42]),['sprint']*3); self.assertEqual(activity.classify_steps([42,68]),['climb']); self.assertEqual(activity.classify_steps([42,98]),['jump'])

    def test_parser_rejects_unsafe_or_nonfinite_input(self):
        with self.assertRaises(ValueError): activity.parse_cells('<!DOCTYPE svg><svg/>')
        with self.assertRaises(ValueError): activity.parse_cells('<svg xmlns="http://www.w3.org/2000/svg"><style>.c.a{fill:var(--c1)}</style><rect class="c a" x="nan" y="0"/></svg>')

    def test_motion_is_continuous_and_contact_aware(self):
        weeks=activity.group_weeks(activity.parse_cells(fixture_svg())); frames,arrivals=activity.build_frames(weeks); self.assertGreater(len(frames),80); self.assertTrue(any(f.state=='sprint' and f.contact in {'left','right'} for f in frames)); self.assertTrue(any(f.state=='climb' and f.contact=='hands' for f in frames)); self.assertTrue(any(f.state=='jump' and f.contact=='none' for f in frames)); self.assertTrue(any(kind=='hands' for events in arrivals.values() for _,_,kind in events))

    def test_runner_surface_anchor_places_feet_on_tower_top(self):
        weeks=model.group_weeks(model.parse_cells(fixture_svg())); frames,_=model.build_frames(weeks)
        _,surface_y=model.position(0,weeks[0],len(weeks))
        self.assertGreaterEqual(model.RUNNER_FOOTLINE,88.0)
        self.assertAlmostEqual(frames[0].y+model.RUNNER_FOOTLINE,surface_y,places=3)
        self.assertLess(frames[0].y,surface_y-80.0)

    def test_sprint_translation_keeps_nearly_constant_forward_velocity(self):
        weeks=model.group_weeks(model.parse_cells(fixture_svg())); frames,_=model.build_frames(weeks)
        sprint=[f for f in frames if f.state=='sprint' and f.direction==1][:14]
        self.assertEqual(len(sprint),14)
        deltas=[b.x-a.x for a,b in zip(sprint,sprint[1:])]
        self.assertLess(max(deltas)-min(deltas),1e-6)
        self.assertTrue(any(f.contact=='none' for f in sprint))

    def test_jump_is_ballistic_dense_and_impact_synced_to_touchdown(self):
        weeks=model.group_weeks(model.parse_cells(fixture_svg())); frames,arrivals=model.build_frames(weeks)
        jump=[f for f in frames if f.state=='jump' and f.direction==1]
        self.assertGreaterEqual(len(jump),28)
        airborne=[f for f in jump if f.contact=='none']
        self.assertTrue(airborne)
        self.assertLess(min(f.y for f in airborne),min(f.y for f in jump if f.contact=='both')-25)
        touchdown=min(f.t for f in jump if f.contact=='both' and f.phase>=.82)
        impact_times=[moment for events in arrivals.values() for moment,_,kind in events if kind=='feet']
        self.assertTrue(impact_times)
        self.assertTrue(any(abs(moment-touchdown)<1e-7 for moment in impact_times))

    def test_skeletal_pose_has_real_joint_range(self):
        weeks=activity.group_weeks(activity.parse_cells(fixture_svg())); frames,_=activity.build_frames(weeks); poses=[titan.pose_for(f) for f in frames if f.state=='sprint']; self.assertGreater(max(p.shoulder_near for p in poses)-min(p.shoulder_near for p in poses),30); self.assertGreater(max(p.hip_near for p in poses)-min(p.hip_near for p in poses),20)

    def test_running_head_counter_rotation_stabilizes_forward_gaze(self):
        weeks=model.group_weeks(model.parse_cells(fixture_svg())); frames,_=model.build_frames(weeks)
        poses=[titan.pose_for(f) for f in frames if f.state=='sprint']
        self.assertTrue(poses)
        self.assertLess(max(abs(p.torso+p.head) for p in poses),2.0)

    def test_forward_sprint_pose_leans_into_travel(self):
        frame=model.Frame(1.0,0,0,'sprint',1,phase=.25,contact='none')
        pose=titan.pose_for(frame)
        self.assertGreater(pose.torso,4.0)
        self.assertLess(pose.head,-4.0)
        self.assertLess(abs(pose.torso+pose.head),2.0)

    def test_forward_sprint_tucks_swing_knee_not_trailing_knee(self):
        frame=model.Frame(1.0,0,0,'sprint',1,phase=.25,contact='none')
        pose=titan.pose_for(frame)
        self.assertLess(pose.hip_near,-20.0)
        self.assertGreater(pose.hip_far,20.0)
        self.assertGreater(pose.knee_near,pose.knee_far+20.0)

    def test_jump_leads_with_foreground_fist_in_travel_direction(self):
        frame=model.Frame(1.0,0,0,'jump',1,phase=.55,contact='none')
        pose=titan.pose_for(frame)
        self.assertLess(pose.shoulder_near,-40)
        self.assertGreater(pose.shoulder_far,0)
        self.assertGreaterEqual(pose.fist_near_scale,1.25)

    def test_joint_animations_preserve_static_translations(self):
        weeks=model.group_weeks(model.parse_cells(fixture_svg())); frames,_=model.build_frames(weeks); output=titan.render_titan(frames,frames[-1].t)
        for joint in ('titan-head','near-shoulder','far-shoulder'):
            start=output.index(f'id="{joint}"'); window=output[start:start+700]
            self.assertIn('additive="sum"',window,f'{joint} animation must preserve its static translation')

    def test_hulk_visual_contract_has_directional_profile_and_mass(self):
        weeks=model.group_weeks(model.parse_cells(fixture_svg())); frames,_=model.build_frames(weeks); output=titan.render_titan(frames,frames[-1].t)
        for marker in ('HULK_MASS_SILHOUETTE','HULK_DIRECTIONAL_PROFILE','BIOMECHANICAL_MOTION_V5','id="titan-hair"','id="titan-face"','id="titan-ear"','id="titan-nose"','id="titan-eye-near"','id="titan-brow"','id="titan-jaw"','id="titan-mouth"','id="titan-traps"','id="titan-chest"','id="titan-purple-shorts"'):
            self.assertIn(marker,output)
        self.assertIn('id="titan-head" transform="translate(8 -156)"',output)

    def test_spring_physics_deforms_then_settles(self):
        a=render._spring_response(0,7,'feet'); b=render._spring_response(.18,7,'feet'); c=render._spring_response(1.8,7,'feet'); self.assertNotEqual(a,(0,1,1,0)); self.assertNotEqual(b,(0,1,1,0)); self.assertEqual(c,(0,1,1,0)); self.assertTrue(a[1]>1 or a[2]<1)

    def test_feet_landings_use_deeper_longer_jello_profile(self):
        landing=render._spring_response(0,7,'feet'); generic=render._spring_response(0,7,'generic')
        self.assertNotEqual(landing,generic)
        self.assertGreaterEqual(landing[0],6.0)
        self.assertGreaterEqual(landing[1],1.20)
        self.assertLessEqual(landing[2],.75)
        self.assertNotEqual(render._spring_response(1.25,7,'feet'),(0,1,1,0))
        self.assertEqual(render._spring_response(1.8,7,'feet'),(0,1,1,0))

    def test_render_is_valid_safe_rigged_3d_svg(self):
        output=activity.render_activity_world(activity.parse_cells(fixture_svg())); ET.fromstring(output); lower=output.lower(); self.assertNotIn('<script',lower); self.assertNotIn('javascript:',lower)
        for marker in ('BRICK_ROUTE_FORWARD','BRICK_ROUTE_REVERSE','COLUMN_SETTLE','BRICK_STATE_JUMP','BRICK_STATE_CLIMB','BRICK_STATE_SPRINT','BRICK_STATE_TURN','TITAN_BODY_DEPTH','TITAN_CONTINUOUS_RIG','TITAN_FOOT_CONTACT_CYCLE','HULK_DIRECTIONAL_PROFILE','BIOMECHANICAL_MOTION_V5','JELLO_SPRING_PHYSICS','TOWER_TOP_FACE','TOWER_FRONT_FACE','TOWER_SIDE_FACE','near-shoulder-anim','near-elbow-anim','near-hip-anim','near-knee-anim','camera-follow','ACTIVITY WORLD // TITAN RUN'):
            self.assertIn(marker,output)

if __name__=='__main__': unittest.main()
