# Third-Person View Migration Plan

This plan breaks the transition from the current top-down/simple-shape game into phased, testable milestones.  
The final phase is dedicated to swapping temporary geometry with proper 3D models once assets are ready.

## Goals
- Move from current camera/gameplay presentation to a third-person experience.
- Keep the game playable at the end of every phase.
- Prepare an optional combat layer with gun + ammunition mechanics.
- Defer asset-heavy work (final character/environment models) to the last phase.

---

## Phase 0 — Baseline & Architecture Preparation
**Objective:** Make the current codebase ready for a staged migration.

### Deliverables
- Document current loop responsibilities (input, movement, collisions, rendering, UI) in the [Phase 0 Baseline Reference](docs/PHASE0_BASELINE_REFERENCE.md).
- Introduce basic module boundaries (e.g., `camera`, `player_controller`, `combat`, `rendering`).
- Add feature flags/toggles for major systems (third-person camera, combat prototype).
- Capture baseline behavior with existing tests + quick manual smoke checklist.

### Exit Criteria
- Existing gameplay still works unchanged.
- New modules exist but can remain pass-through/stubbed.

---

## Phase 1 — World/Coordinate Foundation for 3D
**Objective:** Prepare math + data structures to support 3D movement and camera logic.

### Deliverables
- Define consistent world units and axes (forward/up/right conventions) in the [Phase 1 World/Coordinate Foundation](docs/PHASE1_WORLD_COORDINATE_FOUNDATION.md).
- Upgrade entity transforms to include 3D position + orientation.
- Keep physics/collision simple at first (capsule/box approximations are fine).
- Add debugging overlays (position, forward vector, camera target).

### Exit Criteria
- Player and environment positions are represented in 3D space.
- Core movement and collisions still deterministic and testable.

---

## Phase 2 — Third-Person Camera MVP
**Objective:** Introduce a playable chase camera.

### Deliverables
- Add camera rig with:
  - follow target (player anchor),
  - configurable distance/height,
  - yaw/pitch input,
  - basic smoothing.
- Add camera collision/obstruction handling (prevent clipping through walls).
- Add lock-on/recenter key for fast camera recovery.
- Keep original camera mode as fallback toggle.

### Exit Criteria
- Game is fully playable in third-person mode.
- Camera can orbit player and remains stable in confined spaces.

---

## Phase 3 — Third-Person Player Controller & Animation Hooks
**Objective:** Align movement with third-person expectations.

### Deliverables
- Movement relative to camera heading (WASD moves by camera forward/right).
- Separate facing direction from movement direction where needed.
- Add jump/fall states if verticality is planned.
- Introduce animation state hooks/events (idle/run/turn/jump placeholders).

### Exit Criteria
- Character control feels natural in third-person.
- Clear API exists for future animation/model integration.

---

## Phase 4 — Combat Option (Gun + Ammunition)
**Objective:** Provide an optional gameplay module with ranged combat.

### Deliverables
- Feature toggle: enable/disable combat mode.
- Weapon prototype:
  - fire input,
  - fire-rate cooldown,
  - hit detection (hitscan first).
- Ammunition system:
  - magazine size,
  - reserve ammo,
  - reload action + duration,
  - dry-fire feedback.
- HUD elements for ammo count and reload state.
- Optional pickups for ammo replenishment.

### Exit Criteria
- With combat enabled: player can shoot, reload, and run out of ammo.
- With combat disabled: base exploration gameplay remains unaffected.

---

## Phase 5 — Temporary 3D Assets (Simple Geometry Pass)
**Objective:** Stabilize full third-person + combat loop before final art.

### Deliverables
- Replace 2D/simple placeholders with temporary 3D primitives.
- Ensure rig/attachment points exist for weapon-in-hand presentation.
- Validate camera framing with temporary character/environment scale.
- Tune movement/combat feel while visuals are still low-cost to iterate.

### Exit Criteria
- Entire loop runs with temporary 3D geometry.
- No dependency on final production models yet.

---

## Phase 6 — Final Model Integration (Last Step)
**Objective:** Replace simple shapes with final 3D models and polish.

### Deliverables
- Integrate prepared character, weapon, and environment models.
- Hook final animations and retarget if needed.
- Update collision proxies independent from visual mesh complexity.
- Polish lighting/materials and final camera offsets for model proportions.

### Exit Criteria
- All temporary geometry replaced by final assets.
- Third-person + optional gun/ammo mode is production-ready.

---

## Suggested Milestone Sequence (Time-Box Friendly)
1. **M1:** Phases 0–1 (technical groundwork)
2. **M2:** Phase 2 (camera playable)
3. **M3:** Phase 3 (controller polish)
4. **M4:** Phase 4 (combat option)
5. **M5:** Phase 5 (temp 3D pass)
6. **M6:** Phase 6 (final model replacement + polish)

## Risk Controls
- Keep each phase behind toggles when possible.
- Avoid blocking on final art by using placeholders until Phase 6.
- Treat camera stability and controls as first-class quality gates.
- Keep combat optional so core migration can ship independently.
