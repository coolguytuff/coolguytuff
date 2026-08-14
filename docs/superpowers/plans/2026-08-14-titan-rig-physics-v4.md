# TITAN Continuous Rig + Spring Physics v4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Activity World pose-swapping runner and simple wobble with a continuous articulated powerhouse rig and damped spring-mass jello terrain.

**Architecture:** Keep the existing model/render/character module split. Extend model frames with phase/contact data, map phases to articulated joint angles in the character module, and use bounded damped spring responses for tower deformation in the renderer.

**Tech Stack:** Python 3 stdlib, SVG/SMIL, GitHub Actions, unittest.

## Global Constraints
- GitHub-native only; no JavaScript or separate site.
- Keep the character original while strongly reflecting the supplied green muscular comic-body inspiration.
- Preserve real contribution-derived terrain and exact rest heights.
- Generated SVG stays self-contained and safe.
- Existing workflow permission/pinning boundaries remain unchanged.

### Task 1: Continuous motion data
- [x] Extend `Frame` with normalized `phase` and `contact`.
- [x] Sample sprint, jump, climb, and turn phases continuously.
- [x] Add contact-aware tests.

### Task 2: Articulated TITAN rig
- [x] Add `Pose` joint-angle model and `pose_for(frame)`.
- [x] Render chained shoulder/elbow and hip/knee transforms.
- [x] Increase traps, chest, delts, fists, legs, hair, face aggression, and torn purple shorts while remaining original.
- [x] Add near-fist foreshortening and head stabilization.

### Task 3: Spring-mass jello
- [x] Implement bounded damped spring response for translate/scale/tilt.
- [x] Couple vertical compression with horizontal bulge.
- [x] Add delayed first/second-neighbor propagation and impact ripple rings.
- [x] Preserve exact rest state.

### Task 4: Verification
- [x] Unit-test route classification, parser bounds, contacts, articulation, spring decay, XML validity, and safety markers.
- [x] Local result: 8/8 tests green.

### Task 5: Integration
- [ ] Push implementation branch.
- [ ] Open PR and require GitHub validator success.
- [ ] Review diff and merge with expected head SHA.
- [ ] Verify post-merge real contribution-data asset generation and publisher.
