# TITAN Continuous Rig + Spring Physics v4 Design

## Goal

Make the Activity World runner read as a genuinely muscular, Hulk-inspired original powerhouse with continuous running, jumping, climbing, and turning motion, while making the contribution towers behave like convincing jello under impact.

## Locked direction

- Keep the profile GitHub-native: SVG/SMIL + Python generation, no JavaScript or separate site.
- Preserve the current hero hierarchy and 3D contribution map.
- Replace pose swapping with a continuous articulated skeleton.
- Keep the character original while moving the physical language closer to the supplied muscular green comic reference: massive traps, delts, chest, thighs, forearms, fists, dark messy hair, angry expression, torn purple shorts, strong foreshortening.
- Preserve real contribution-derived terrain geometry and exact rest heights.
- Keep pinned Actions, read-only generation, SVG validation, and isolated exact-path publication.

## Motion architecture

`activity_world_model.py` owns route classification, transition timing, contact states, phase sampling, and camera tracking. Each frame carries a normalized motion phase and contact state.

`activity_world_titan.py` maps those phases into an articulated body pose: torso, head, shoulders, elbows, hips, knees, pelvis bob, and near-fist foreshortening. The SVG renders one rig whose joints animate continuously.

`activity_world_render.py` owns tower geometry and spring response. Impacts are modeled as damped oscillations affecting vertical displacement, vertical compression, horizontal bulge, and small tilt. Energy propagates to first- and second-neighbor towers at reduced amplitude and delayed timing.

## Choreography

- Sprint: alternating arm swing, knee drive, stance/flight contacts, torso lean/twist, pelvis bob.
- Jump: crouch, explosive extension, airborne stretch/tuck, landing brace, recoil.
- Climb: reach, hand latch, hang, elbow flexion, knee tuck, foot plant, hip rise, top-out.
- Turn: skid/compress, torso rotation, foot plant, reverse.
- Impact: squash, lateral bulge, rebound, overshoot, damped settle, ripple ring, neighbor wave.

## Safety / correctness

- Contribution input remains bounded numeric geometry only.
- No source markup is copied to output.
- Output remains script/event/external-resource free.
- Spring response is clamped and returns exactly to rest.
- Tests cover articulation, contact states, spring decay, parser bounds, choreography markers, XML validity, and security invariants.
