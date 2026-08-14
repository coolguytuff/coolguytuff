# Dave Command Profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current profile with an elite GitHub-native Dave Command interface featuring a custom pseudo-3D Dave core, robust repo-hosted telemetry, refined information architecture, and hardened generation workflows.

**Architecture:** Keep the profile completely native to GitHub README rendering. Use self-hosted SVG assets for the primary visual language, generated 3D contribution art for real depth, a small Python generator for telemetry, and minimal GitHub Actions with pinned third-party dependencies and narrow write behavior.

**Tech Stack:** GitHub Markdown/HTML, SVG/SMIL animation, Python 3 stdlib, GitHub Actions, GitHub REST API.

## Global Constraints

- Primary experience stays on the GitHub profile; no separate site.
- True JavaScript/WebGL drag rotation is out of scope because GitHub README rendering does not permit it.
- The Dave visual should rotate slowly in a convincing horizontal pseudo-3D motion without mouse interaction.
- Dave remains private R&D and must not expose private repository internals or security architecture.
- Remove the current broken GitHub stats / Top languages link-text failure mode.
- Avoid mutable `@latest` action refs.
- Grant workflow permissions only where required and stage only intended generated paths.
- Do not expose school, age, exact home location, personal email, or unnecessary personal data.

---

### Task 1: Dave Command Core

**Files:**
- Create: `assets/dave-command-core.svg`
- Remove from README usage: `assets/neural-core.svg`

**Interfaces:**
- Consumes: Dave visual concepts from the approved design and uploaded renderer.
- Produces: `./assets/dave-command-core.svg`, a GitHub-safe animated SVG used by README.

- [ ] Build a dark-space command-frame background with grid, scanlines, HUD corners, and restrained glow.
- [ ] Build a layered nucleus inspired by Dave's dense intelligence core: hot central slit, plasma glow, containment arcs, shards, route filaments, and distributed nodes.
- [ ] Implement horizontal pseudo-3D rotation by animating orbital nodes across ellipses with synchronized scale/opacity/depth changes; keep labels fixed so they remain readable.
- [ ] Add mode/status subsystem labels: `STANDARD`, `RESEARCH`, `BUILD`, `REVIEW`, `GUARDIAN`, `NIGHTWATCH`, plus `CONTEXT`, `ROUTES`, `EVALUATION`, and `LOCAL-FIRST`.
- [ ] Add slow route pulses and state readout language without pretending to show realtime Dave runtime status.
- [ ] Validate the SVG is well-formed XML and contains no script elements or external JavaScript.
- [ ] Commit the asset.

### Task 2: Self-Hosted Telemetry

**Files:**
- Create: `scripts/generate_telemetry.py`
- Create: `assets/telemetry.svg`
- Create: `.github/workflows/profile-assets.yml`
- Delete: `.github/workflows/profile-3d.yml`

**Interfaces:**
- Consumes: `GITHUB_REPOSITORY_OWNER`, optional `GITHUB_TOKEN`, GitHub REST public user/repository data.
- Produces: `assets/telemetry.svg` and refreshed `profile-3d-contrib/*` assets.

- [ ] Implement a Python stdlib-only telemetry generator that fetches the authenticated owner's public profile and public repositories.
- [ ] Aggregate only truthful public metrics: public repositories, followers, total stars on owned public repos, and top repository languages by repo count.
- [ ] Render a polished dark SVG HUD with explicit labels and graceful `DATA UNAVAILABLE` output if GitHub API calls fail.
- [ ] Add a combined scheduled/manual workflow that checks out the repo, runs the pinned 3D renderer, generates telemetry, stages only `profile-3d-contrib` and `assets/telemetry.svg`, and pushes only when those files changed.
- [ ] Give the job only `contents: write` and no other elevated permission.
- [ ] Remove the old 3D workflow after the combined workflow exists.
- [ ] Commit and verify YAML/file paths.

### Task 3: Snake Workflow Hardening

**Files:**
- Modify: `.github/workflows/snake.yml`

**Interfaces:**
- Consumes: GitHub contribution data.
- Produces: snake SVGs on the `output` branch.

- [ ] Replace floating or weak third-party action refs with stable pinned refs where available.
- [ ] Keep `contents: write` only.
- [ ] Keep generation isolated to `dist` and publication isolated to the `output` branch.
- [ ] Verify the workflow still references `github.repository_owner` rather than hard-coded identity.
- [ ] Commit the workflow hardening.

### Task 4: Elite README Rebuild

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: `assets/dave-command-core.svg`, `assets/telemetry.svg`, `profile-3d-contrib/profile-night-rainbow.svg`, contribution snake output.
- Produces: the complete public GitHub profile experience.

- [ ] Replace the generic neural-core section with the Dave Command Core.
- [ ] Rework the page into a coherent command-console hierarchy with less text and stronger visual pacing.
- [ ] Make Dave clearly the flagship private R&D system without disclosing internals.
- [ ] Replace external GitHub stats and language cards with the repo-hosted telemetry SVG so broken alt-link text cannot recur.
- [ ] Retain the 3D contribution city but present it as `ACTIVITY TOPOLOGY` with system-style framing.
- [ ] Keep project links usable and descriptive without a giant badge wall.
- [ ] Keep the contribution snake as a playful secondary motion element.
- [ ] Ensure all image alt text is meaningful and all local asset paths exist.
- [ ] Commit the README.

### Task 5: Verification and Security Review

**Files:**
- Review all files changed from `main...profile/dave-command-elite`.

**Interfaces:**
- Consumes: final branch diff.
- Produces: verified branch ready to merge.

- [ ] Re-fetch every modified file from GitHub and confirm intended contents landed.
- [ ] Verify README no longer contains `github-readme-stats.vercel.app` or the old streak-card URL.
- [ ] Verify local asset references exist at the expected branch paths.
- [ ] Review workflow changes for token scope, untrusted-input execution, generated-path staging, branch writes, and third-party action pinning.
- [ ] Confirm no private Dave implementation/security details or personal email were added.
- [ ] Open a PR from `profile/dave-command-elite` to `main` and inspect the complete diff.
- [ ] Merge only after the diff review passes.
- [ ] Inspect the first post-merge workflow runs; if a generation workflow fails, diagnose and repair before declaring completion.
