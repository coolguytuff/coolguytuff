# Hero Topology + TITAN Activity World v3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote the generated 3D contribution topology under the identity header, make the header dissolve seamlessly into GitHub light/dark backgrounds, and rebuild the contribution runner world as a clearer cinematic pseudo-3D scene with an original green powerhouse runner and complete terrain-aware movement choreography.

**Architecture:** Keep the README as the composition layer, the headboard as a static self-hosted SVG asset, and Activity World as a deterministic Python-generated SVG derived from the pinned contribution source. Preserve the existing read-only generation → validated artifact → isolated write publisher trust boundary.

**Tech Stack:** GitHub Markdown/HTML, SVG/SMIL/CSS media queries, Python 3 standard library, unittest, GitHub Actions.

## Global Constraints

- No JavaScript or separate site.
- 3D contribution topology must be directly below the identity headboard.
- Dave must follow the promoted topology.
- Activity World must remain generated from real contribution signal.
- Character is an original green powerhouse; uploaded comic art is inspiration only.
- Light/dark adaptation uses `prefers-color-scheme`; no fake viewer-local time detection.
- Third-party Actions remain pinned to immutable SHAs.
- Generation job remains `contents: read`; publication remains isolated and exact-path staged.
- Generated SVG must be self-contained and script/event/external-resource free.

---

### Task 1: Recompose the hero hierarchy

**Files:**
- Modify: `README.md`
- Test: `.github/workflows/validate-profile.yml`

**Interfaces:**
- Consumes: existing `identity-headboard.svg`, `profile-3d-contrib/*`, `dave-command-core.svg`, `activity-world.svg`
- Produces: README ordering `headboard → topology → Dave → Activity World → Signal`

- [ ] **Step 1: Update the validator hierarchy assertion first**

Require these markers in increasing order:

```python
hierarchy = [
    './assets/identity-headboard.svg',
    './profile-3d-contrib/profile-night-rainbow.svg',
    './assets/dave-command-core.svg',
    './assets/activity-world.svg',
    '## `03 // SIGNAL`',
]
```

- [ ] **Step 2: Reorder README**

Move the theme-aware 3D topology `<picture>` immediately under the headboard. Put Dave core and Dave description after it. Keep Activity World below Dave and remove the second topology copy from Activity World.

- [ ] **Step 3: Run validator**

Expected: hierarchy passes and all local assets resolve.

- [ ] **Step 4: Commit**

Commit message: `feat: promote 3d contribution topology into hero`

---

### Task 2: Make the identity headboard seamless and theme-aware

**Files:**
- Modify: `assets/identity-headboard.svg`
- Modify: `.github/workflows/validate-profile.yml`

**Interfaces:**
- Produces: self-contained transparent-edge identity SVG with dark/light variables.

- [ ] **Step 1: Add validator requirements**

Require the asset to contain:

```text
id="edgeFade"
@media (prefers-color-scheme: light)
AARON SLUTSKY
@coolguytuff
```

Also preserve cameo IDs.

- [ ] **Step 2: Replace the opaque frame**

Remove the full opaque rounded-card background and full-frame stroke. Add a centered atmospheric haze masked through a four-edge fade mask.

- [ ] **Step 3: Add light/dark CSS variables**

Default dark variables and a light media query must drive name, haze, grid, metadata, and username colors.

- [ ] **Step 4: Preserve/upgrade readable name depth**

Keep multiple name layers and moving specular highlight while ensuring the base name remains readable if animation pauses.

- [ ] **Step 5: Validate XML and security**

Parse with `xml.etree.ElementTree`; assert no scripts, event handlers, external refs, or unsafe URLs.

- [ ] **Step 6: Commit**

Commit message: `feat: dissolve identity header into github theme`

---

### Task 3: Define TITAN movement and 3D terrain tests

**Files:**
- Modify: `tests/test_generate_activity_world.py`
- Modify: `scripts/generate_activity_world.py`

**Interfaces:**
- Produces movement states `jump`, `climb`, `sprint`, `turn` and generated markers.

- [ ] **Step 1: Add failing tests for hierarchy-independent generator behavior**

Test that:
- flat runs of 3+ classify as sprint,
- modest rises classify as climb,
- rough changes classify as jump,
- route contains both directions and endpoint turns,
- generated SVG contains `TITAN_BODY_DEPTH`, `TOWER_TOP_FACE`, `TOWER_FRONT_FACE`, `TOWER_SIDE_FACE`, `COLUMN_SETTLE`, and all state markers.

- [ ] **Step 2: Run tests and confirm expected failure**

Run:

```bash
python3 -m unittest tests.test_generate_activity_world -v
```

- [ ] **Step 3: Add/normalize `turn` markers and state metadata**

Preserve existing classification API while making generated route metadata explicitly include endpoint turns.

- [ ] **Step 4: Run tests**

Expected: state tests pass except for visual marker tests not implemented yet.

- [ ] **Step 5: Commit**

Commit message: `test: define titan 3d activity choreography`

---

### Task 4: Rebuild contribution towers as cinematic pseudo-3D blocks

**Files:**
- Modify: `scripts/generate_activity_world.py`
- Modify: `assets/activity-world.svg` bootstrap/check-in output
- Test: `tests/test_generate_activity_world.py`

**Interfaces:**
- Consumes: `Week.terrain_level`, `Week.height`, per-day levels
- Produces: multi-face isometric tower groups with stable top landing points.

- [ ] **Step 1: Introduce perspective projection helpers**

Create deterministic helpers for tower center, top plane, front face, side face, shadow, and runner landing anchor. Keep output numeric only.

- [ ] **Step 2: Increase tower readability**

Use wider blocks, deeper side faces, stronger top highlights, cast shadows, and top studs/indicators while keeping all week columns visible at README width.

- [ ] **Step 3: Preserve exact data height**

Wobble must be transform-only; never rewrite contribution-derived base geometry.

- [ ] **Step 4: Render neighbor damping**

Keep delayed lower-amplitude oscillation on adjacent towers.

- [ ] **Step 5: Run unit tests and XML parse**

Expected: all tower marker and safety assertions pass.

- [ ] **Step 6: Commit**

Commit message: `feat: rebuild activity terrain as 3d block world`

---

### Task 5: Replace BRICK sprite with TITAN-grade original powerhouse

**Files:**
- Modify: `scripts/generate_activity_world.py`
- Test: `tests/test_generate_activity_world.py`

**Interfaces:**
- Consumes: position timeline, direction timeline, pose timeline
- Produces: layered vector body with depth, muscle volume, directional foreshortening, and squash/stretch.

- [ ] **Step 1: Build layered body groups**

Create separate back-arm, torso, chest/shoulders, head, near-arm, hands, legs, and foreground-highlight groups. Use multiple radial/linear gradients and shadows.

- [ ] **Step 2: Create original green powerhouse styling**

Use green synthetic muscle, dark graphite waist/short armor, cyan/violet energy seams, and an original face/visor. Do not reproduce recognizable superhero logos/costume details.

- [ ] **Step 3: Add state-specific pose deformation**

Jump: crouch → stretch → land squash.
Climb: reach/hang → pull → plant.
Sprint: low torso, alternating arm/leg rhythm, contact bob.
Turn: skid/compress → twist → reverse.

- [ ] **Step 4: Make direction change alter depth order**

Mirror primary geometry and use direction-specific near/far limb opacity/highlight so reverse traversal reads as 3D rather than a flat flip.

- [ ] **Step 5: Run tests and inspect generated SVG**

Expected: marker and XML/safety tests pass; character is materially larger and clearer than v2.

- [ ] **Step 6: Commit**

Commit message: `feat: rebuild runner as titan powerhouse`

---

### Task 6: Harden validator and generation boundary

**Files:**
- Modify: `.github/workflows/validate-profile.yml`
- Modify: `.github/workflows/profile-assets.yml` only if generated paths or validation commands change

**Interfaces:**
- Consumes: generated SVG output
- Produces: CI gate for theme/fade/hierarchy/3D/motion/security invariants.

- [ ] **Step 1: Extend profile validator**

Assert:
- new hero hierarchy,
- headboard edge fade and light-mode media query,
- Activity World TITAN and 3D tower markers,
- jump/climb/sprint/turn/settle markers,
- no external image sources,
- no SVG scripts/events/external refs.

- [ ] **Step 2: Keep workflow pin/write checks**

Retain immutable 40-hex action refs, no `@latest`, no `git add -A`, no `pull_request_target`, and exact generated-path staging.

- [ ] **Step 3: Run complete validator locally/CI**

Expected: green.

- [ ] **Step 4: Commit**

Commit message: `test: enforce v3 profile visual and safety invariants`

---

### Task 7: PR, review, merge, and steady-state verification

**Files:** all changed files in branch

**Interfaces:**
- Produces: verified `main` plus generated steady-state assets.

- [ ] **Step 1: Compare branch against `main`**

Review every changed file.

- [ ] **Step 2: Open PR**

Describe hierarchy, theme behavior, TITAN motion, data derivation, and security boundary.

- [ ] **Step 3: Require green profile validation**

Do not merge on failed/pending validation.

- [ ] **Step 4: Perform security diff review**

Review generator input handling, SVG output construction, workflow permissions, third-party Actions, generated file staging, and README privacy.

- [ ] **Step 5: Merge after green review**

Merge to `main` using expected head SHA.

- [ ] **Step 6: Verify post-merge profile-assets workflow**

Confirm generation boundary and publisher both succeed.

- [ ] **Step 7: Verify bot-generated steady-state commit**

Fetch live `README.md`, `identity-headboard.svg`, and `activity-world.svg` from final `main`; confirm new hierarchy and generated data-based scene are present.
