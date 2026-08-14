# Activity World + Identity Headboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the live GitHub profile with a readable animated identity headboard and a real-contribution-driven Activity World featuring BRICK, an original terrain-aware traversal mascot, while preserving the existing Dave Command visual system and hardened workflow model.

**Architecture:** Keep the headboard as a hand-authored self-hosted SVG and generate the Activity World deterministically from the existing contribution-grid SVG. A Python generator parses only expected contribution cell geometry/classes, derives terrain heights and movement states, then emits a self-contained script-free SVG. GitHub Actions generates the source contribution grid and Activity World in a read-only job; a separate publisher receives artifacts and writes exact generated paths.

**Tech Stack:** GitHub README HTML/Markdown, SVG/SMIL, Python 3 standard library, GitHub Actions, existing pinned profile generation actions.

## Global Constraints

- Everything renders directly on the GitHub profile README.
- No JavaScript, WebGL, iframe, canvas, or separate site.
- Primary visuals are self-hosted.
- Dave remains immediately below identity; Activity World remains immediately below Dave.
- Contribution terrain is derived from real public contribution data.
- Third-party Actions remain pinned to immutable SHAs.
- Generation jobs remain read-only; publishing jobs stage exact known paths only.
- No private Dave repo name, personal Gmail address, school, age, or exact home location in the README.
- Motion must preserve readability and avoid strobing/rapid flashing.

---

### Task 1: Create identity headboard

**Files:**
- Create: `assets/identity-headboard.svg`
- Modify: `.github/workflows/validate-profile.yml`

**Interfaces:**
- Produces: self-contained SVG at `assets/identity-headboard.svg` with readable `AARON SLUTSKY`, smaller `@coolguytuff`, operator subtitle, animated highlight/depth, and two rare minimal easter-egg silhouettes.
- Consumes: existing Dave palette conventions only.

- [ ] **Step 1: Create the headboard SVG**
  - 1200×340 viewBox.
  - Add layered name text, outline/shadow depth, scanline/highlight sweep, subtle grid/radar background, operator lights, username/subtitle.
  - Add rare yellow sponge-like and teal platypus-like silhouette pop-ups using original primitive geometry.
  - Do not use external images, fonts, scripts, or links.

- [ ] **Step 2: Validate XML and executable-content invariants**
  - Parse with Python `xml.etree.ElementTree`.
  - Assert `<script`, `javascript:`, `onload=`, and external `href=http` are absent.

- [ ] **Step 3: Extend repository validator**
  - Require `assets/identity-headboard.svg`.
  - Assert README references it before `assets/dave-command-core.svg` once README is updated.
  - Assert SVG contains `AARON SLUTSKY` and `@coolguytuff`.

- [ ] **Step 4: Commit**
  - Commit message: `feat: add animated identity headboard`.

---

### Task 2: Build deterministic Activity World generator

**Files:**
- Create: `scripts/generate_activity_world.py`
- Create: `tests/test_generate_activity_world.py`

**Interfaces:**
- Consumes: an SVG contribution grid file containing rect-like cell geometry/classes produced by the profile contribution generator.
- Produces: `assets/activity-world.svg`.
- Public functions:
  - `parse_cells(svg_text: str) -> list[Cell]`
  - `terrain_height(level: int) -> int`
  - `classify_steps(heights: list[int]) -> list[str]`
  - `build_route(cells: list[Cell]) -> list[RouteStep]`
  - `render_activity_world(cells: list[Cell]) -> str`

- [ ] **Step 1: Write parser tests**
  - Use a compact fixture SVG containing contribution cells at multiple class levels.
  - Assert only numeric geometry and expected `c0`…`c4` intensity classes are consumed.
  - Assert script/event-handler content in the input is ignored rather than copied.

- [ ] **Step 2: Implement contribution cell parsing**
  - Standard-library XML/re parsing only.
  - Normalize cells in chronological left-to-right then row-aware order suitable for traversal.
  - Do not carry arbitrary input attributes into output.

- [ ] **Step 3: Write terrain/movement classification tests**
  - Heights `[1,1,1,1]` must produce a sprint run for the interior traversal.
  - Small positive delta must produce `climb`.
  - Larger/non-flat transitions must produce `jump`.
  - Endpoints must produce turnaround markers in the rendered route.

- [ ] **Step 4: Implement deterministic terrain mapping**
  - Map levels 0–4 to visible column heights while retaining zero-day platforms.
  - Include a minimum platform height so BRICK always has continuous terrain.

- [ ] **Step 5: Implement locomotion classification**
  - Flat runs of at least 3 consecutive equal-height cells become sprint segments.
  - Small upward differences become climbs.
  - Remaining transitions become jumps.

- [ ] **Step 6: Implement route timing**
  - Forward traversal and reverse traversal share the same terrain but have mirrored facing.
  - Sprint segments use shorter duration per cell.
  - Climb segments include grab/hang/pull timing.
  - Jump segments include anticipation, arc, impact, recovery timing.

- [ ] **Step 7: Render self-contained SVG**
  - Pseudo-3D terrain blocks with top/front/side faces.
  - BRICK drawn from original SVG primitives: gel torso, armor plates, shoulders, forearms, legs, visor.
  - Use `animateMotion`, `animateTransform`, grouped opacity/state sequences, and terrain reaction animations.
  - Include metadata markers/comments `BRICK_STATE_JUMP`, `BRICK_STATE_CLIMB`, `BRICK_STATE_SPRINT`, `BRICK_ROUTE_FORWARD`, `BRICK_ROUTE_REVERSE`, `COLUMN_SETTLE` for validation.
  - Output contains no scripts/event handlers/external resources.

- [ ] **Step 8: Run unit tests**
  - Command: `python3 -m unittest tests.test_generate_activity_world -v`.
  - Expected: all parser, classification, route, and output-safety tests pass.

- [ ] **Step 9: Commit**
  - Commit message: `feat: generate animated contribution activity world`.

---

### Task 3: Generate the first Activity World from real profile contribution data

**Files:**
- Create: `assets/activity-world.svg`

**Interfaces:**
- Consumes: current real contribution-grid SVG from the `output` branch or generated source artifact.
- Produces: checked-in real-data Activity World used by README.

- [ ] **Step 1: Fetch current contribution source**
  - Use the current public generated contribution SVG as the authoritative terrain input.

- [ ] **Step 2: Run generator against that source**
  - `CONTRIBUTION_SVG=<source> ACTIVITY_WORLD_OUT=assets/activity-world.svg python3 scripts/generate_activity_world.py`.

- [ ] **Step 3: Validate the generated scene**
  - XML parse succeeds.
  - No script/event/external URL primitives.
  - Contains terrain blocks and BRICK markers.
  - Contains forward/reverse route markers.
  - Contains at least jump plus sprint or climb markers based on current data.

- [ ] **Step 4: Commit**
  - Commit message: `feat: add real-data activity world`.

---

### Task 4: Recompose the README hierarchy

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: `assets/identity-headboard.svg`, `assets/dave-command-core.svg`, `assets/activity-world.svg`, existing execution/tool/telemetry assets.
- Produces: final profile ordering and accessible captions.

- [ ] **Step 1: Replace plain heading with identity headboard**
  - First visible visual is `assets/identity-headboard.svg`.
  - Keep a hidden/plain-text semantic identity line only if needed for accessibility/search, not as a competing visual heading.

- [ ] **Step 2: Place Dave immediately after identity**
  - Preserve current Dave caption and privacy framing.

- [ ] **Step 3: Place Activity World immediately after Dave**
  - Caption explains it is the real contribution history rendered as a traversal world.
  - Mention BRICK behavior concisely without overwhelming the page.

- [ ] **Step 4: Move existing sections down and renumber**
  - Signal → Execution Loop → Build Domains → Public Lab → Tool Deck → Telemetry → Operating Principles → Transmission End.
  - Remove the standalone contribution snake section from README.

- [ ] **Step 5: Preserve readability**
  - Avoid giant explanatory paragraphs around the two hero visuals.
  - Keep all `<img>` tags meaningful alt text.

- [ ] **Step 6: Commit**
  - Commit message: `feat: recompose profile around Dave activity world`.

---

### Task 5: Integrate Activity World into hardened generation workflow

**Files:**
- Modify: `.github/workflows/profile-assets.yml`
- Modify: `.github/workflows/snake.yml` only if needed to share source data cleanly.

**Interfaces:**
- Generation job produces `profile-3d-contrib/**`, `assets/telemetry.svg`, contribution source SVG, and `assets/activity-world.svg`.
- Publish job writes only generated paths.

- [ ] **Step 1: Produce contribution source in read-only generation job**
  - Reuse the pinned `Platane/snk` action at the existing immutable SHA or an equivalent already-pinned source.
  - Generate one source SVG into a temporary/generated path.

- [ ] **Step 2: Run Activity World generator**
  - Feed the source SVG to `scripts/generate_activity_world.py`.

- [ ] **Step 3: Extend artifact package**
  - Include `assets/activity-world.svg`.

- [ ] **Step 4: Narrow publisher staging**
  - Exact stage command includes `profile-3d-contrib`, `assets/telemetry.svg`, and `assets/activity-world.svg` only.
  - No `git add -A`.

- [ ] **Step 5: Preserve permissions**
  - Generation job: `contents: read`.
  - Publish job: `contents: write`.
  - No PR-triggered write path.

- [ ] **Step 6: Commit**
  - Commit message: `ci: refresh activity world from contribution data`.

---

### Task 6: Upgrade permanent validation

**Files:**
- Modify: `.github/workflows/validate-profile.yml`

**Interfaces:**
- Produces: CI gate covering hierarchy, SVG safety, animation contract, generator tests, and workflow hardening.

- [ ] **Step 1: Run generator unit tests in CI**
  - `python3 -m unittest tests.test_generate_activity_world -v`.

- [ ] **Step 2: Validate hierarchy order**
  - Assert headboard reference index < Dave reference index < Activity World reference index < Signal section index.

- [ ] **Step 3: Validate Activity World markers**
  - Assert real checked-in output contains BRICK, forward/reverse, column settle, and locomotion markers.

- [ ] **Step 4: Validate all displayed SVGs**
  - XML parse.
  - Reject `<script`, `javascript:`, common inline event handlers, and unapproved external asset URLs.

- [ ] **Step 5: Validate workflow hardening**
  - Reject `@latest`, `git add -A`, `pull_request_target` on write-capable workflows.
  - Assert exact generated staging includes Activity World.

- [ ] **Step 6: Commit**
  - Commit message: `test: validate animated activity world profile`.

---

### Task 7: PR verification and security diff review

**Files:**
- Review every changed file in the branch diff.

**Interfaces:**
- Produces: green validation run and security disposition.

- [ ] **Step 1: Open PR to `main`**
  - Include scope, visual behavior, data source, workflow changes, and test notes.

- [ ] **Step 2: Wait for validation workflow**
  - Require all validator steps to pass.

- [ ] **Step 3: Perform Codex Security-style diff review**
  - Review changed workflows, parser/generator, README, and SVG assets.
  - Threats: malicious/generated SVG content propagation, token scope expansion, arbitrary path writes, external asset injection, unsafe event attributes, private-data leakage.
  - Validate any candidate finding before reporting.

- [ ] **Step 4: Fix any validated issue and re-run CI**
  - Do not merge with unresolved reportable security findings.

---

### Task 8: Merge and steady-state verification

**Files:**
- Live `main` and generated assets.

**Interfaces:**
- Produces: final live GitHub profile and post-generation verified state.

- [ ] **Step 1: Merge reviewed PR**
  - Merge only the verified expected head SHA.

- [ ] **Step 2: Verify first post-merge profile asset generation**
  - Confirm read-only generation and isolated publisher jobs succeed.

- [ ] **Step 3: Verify final `main` after bot-generated asset commit**
  - Fetch README, headboard, Dave, Activity World, telemetry, and workflow outputs.
  - Confirm hierarchy and asset references remain intact.

- [ ] **Step 4: Trigger/obtain final validation on steady-state tree**
  - If `GITHUB_TOKEN` bot commit suppresses recursion, make only a legitimate cleanup/validation-affecting user-authored commit if one is actually needed; otherwise perform explicit equivalent checks and report the non-recursion behavior accurately.

- [ ] **Step 5: Final report**
  - Report merged SHA, generated-asset SHA if different, validator result, workflow result, and security disposition.
