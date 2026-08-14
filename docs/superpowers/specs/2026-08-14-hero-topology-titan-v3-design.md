# Hero Topology + TITAN Activity World v3 — Design Spec

## Goal

Upgrade the GitHub profile’s top-of-page experience so the strongest visuals appear first and feel like one seamless scene:

1. a borderless/fading identity headboard,
2. the full generated 3D contribution topology immediately under the identity headboard,
3. Dave below the topology,
4. a rebuilt contribution Activity World featuring an original, large green powerhouse runner with clearer pseudo-3D anatomy and terrain interactions,
5. the existing lower profile sections preserved beneath those hero systems.

The result must remain fully native to a GitHub profile README: no JavaScript, no external site, and no fake mouse interaction.

## Approved Visual Hierarchy

Top-to-bottom:

1. `assets/identity-headboard.svg`
2. generated 3D contribution topology (`profile-3d-contrib/...`)
3. `assets/dave-command-core.svg`
4. Dave description block
5. `assets/activity-world.svg`
6. Signal
7. Execution Loop
8. Build Domains
9. Public Lab
10. Tool Deck
11. Telemetry
12. Operating Principles
13. Transmission end

The Activity World no longer embeds a second copy of the full 3D topology because the topology is promoted to the hero position directly beneath the identity header.

## Identity Headboard v3

### Seamless perimeter

The headboard must visually dissolve into GitHub’s page background rather than ending as a rounded rectangular card.

Implementation:

- transparent SVG outer background,
- center-only atmospheric field,
- radial/linear alpha masks that fade all four edges to transparent,
- no visible full-frame border,
- visual elements near the perimeter must also fade instead of being clipped abruptly.

### Light/dark behavior

Use SVG CSS with `@media (prefers-color-scheme: light)` and default dark variables.

Dark mode:
- deep navy/black center haze,
- cyan/violet highlights,
- bright cool-white name.

Light mode:
- nearly transparent pale-blue/white atmospheric haze,
- darker blue/violet type and outlines,
- reduced glow strength so the text remains crisp on GitHub’s light background.

Time-of-day behavior is intentionally not implemented because a static README SVG cannot know each viewer’s local time. Viewer color-scheme adaptation is deterministic and GitHub-native.

### Name treatment

`AARON SLUTSKY` remains the dominant identity object.

Enhancements:
- layered depth/shadow lettering,
- moving specular highlight,
- subtle internal scan/energy motion,
- large readable silhouette even when animation is paused,
- `@coolguytuff` directly beneath in a smaller monospaced operator style,
- existing rare comedic cameos remain tiny and secondary.

## 3D Contribution Topology Promotion

The generated `profile-night-rainbow.svg` / `profile-gitblock.svg` picture block moves immediately below the identity headboard.

The topology remains untouched as source-of-truth generated art; only README hierarchy and surrounding framing/copy change.

The surrounding copy should be compact so the actual 3D contribution art remains the focus.

## Activity World v3

### Character

Replace the small cyber-gel mascot silhouette with a large original green powerhouse runner, internally named `TITAN` while preserving `BRICK` in code compatibility markers if useful.

The uploaded muscular green comic reference is used only as visual inspiration for mass, anatomy, posture, and impact—not copied as character art.

Character design:
- green synthetic/gel-muscle body,
- huge shoulders, chest, traps, forearms, hands, thighs,
- compact head and aggressive forward posture,
- original face/visor treatment,
- dark graphite utility shorts/waist armor rather than any recognizable superhero costume,
- cyan/violet energy seams to keep the Dave visual language,
- multiple gradients and occlusion layers for 3D volume,
- limb foreshortening and depth ordering that change with travel direction.

### Terrain

The current narrow flat prisms are replaced with larger, clearer pseudo-isometric contribution towers.

Each weekly tower uses:
- broad top face,
- front face,
- right/left side face depending on scene perspective,
- cast shadow,
- top studs / contribution indicators,
- contribution-level color and height,
- subtle atmospheric depth scaling across the scene.

The terrain must remain derived from real contribution signal.

### Camera and perspective

Use a fixed cinematic pseudo-3D camera:
- horizon line above the towers,
- deck/floor perspective grid,
- towers recede slightly with depth,
- runner travels along a visually clear top ridge,
- nearest foreground faces are darker and more saturated,
- highlights remain readable on both large and small GitHub profile widths.

### Motion states

The existing behavior requirements remain and are upgraded visually:

#### Jump
- anticipation crouch,
- squash at launch,
- stretched airborne body,
- parabolic arc,
- torso lean follows direction,
- fists/arms lead the motion,
- landing compression,
- terrain impact response.

#### Small-rise climb
When target height is only modestly higher:
- TITAN reaches forward,
- hand contacts the ledge,
- body hangs briefly below top,
- opposite arm and legs compress,
- he pulls torso above the ledge,
- feet plant on top,
- target column shakes lightly like gel and settles exactly back to data height.

#### Sprint
On flat patches of 3 or more equal-height weekly towers:
- lower center of gravity,
- faster forward translation,
- alternating arm/leg pose silhouettes,
- slight body bob,
- repeated foot-contact micro-bounces on the towers,
- automatically returns to jump/climb when terrain changes.

#### Turnaround
At both endpoints:
- braking skid/compression,
- upper body twist,
- direction flip,
- brief power stance,
- reverse traversal.

### Terrain response

Landing and running contacts must not permanently alter data geometry.

Each impacted column:
1. compresses downward,
2. overshoots upward,
3. wobbles with decreasing amplitude,
4. settles exactly at contribution-derived height.

Neighboring towers receive smaller delayed secondary oscillations.

### Loop

The complete forward-and-reverse traversal should remain long enough to feel cinematic rather than repetitive. Target approximately 45–75 seconds depending on contribution topology.

## Data and Generator Architecture

`Platane/snk` remains the pinned read-only contribution source generator.

`scripts/generate_activity_world.py`:
- parses only contribution-cell geometry/intensity,
- groups cells into weekly columns,
- classifies movement states,
- creates numeric timelines,
- emits the full self-contained `assets/activity-world.svg`,
- never copies arbitrary input SVG elements into output.

No new runtime dependencies.

## Security and Reliability

Maintain existing guarantees:
- third-party Actions pinned to immutable SHAs,
- generator job `contents: read`,
- separate write-capable publish job,
- publisher stages explicit generated paths only,
- generated SVG boundary validation occurs before artifact upload/publish,
- no `<script>`, `javascript:`, inline event handlers, foreign objects, external hrefs/images, or unsafe embedded resources,
- contribution parser rejects malformed/oversized/non-finite input.

Validator additions:
- README hierarchy is `headboard → topology → Dave → Activity World → Signal`,
- headboard includes edge-fade mask and color-scheme media query,
- Activity World includes jump/climb/sprint/turn/settle markers,
- Activity World contains multi-face 3D tower markers and TITAN body-depth markers,
- generated output remains valid XML and self-contained.

## Accessibility

- Every README image has useful alt text.
- Name and username remain readable without animation.
- Critical information is not encoded only through color or motion.
- Decorative cameos remain non-essential.

## Acceptance Criteria

The change is complete only when:

1. profile validator passes on the feature branch,
2. PR diff/security review finds no unresolved reportable issue,
3. PR is merged to `main`,
4. post-merge asset generation succeeds,
5. generated Activity World is published from live contribution data,
6. final steady-state `main` is rechecked after the bot-generated asset commit.
