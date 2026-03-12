# Phase 1 — World/Coordinate Foundation for 3D

This document is the implementation reference for **Phase 1** from `THIRD_PERSON_MIGRATION_PLAN.md`.

## 1) Coordinate System Contract

Adopt a single convention across gameplay, camera, and rendering code:

- **Handedness:** Right-handed.
- **Up axis:** `+Y`.
- **Forward axis:** `+Z`.
- **Right axis:** `+X`.
- **Ground plane:** `X/Z`.

### Units
- **Distance unit:** `1.0 = 1 meter` (world-space).
- **Velocity:** meters/second.
- **Acceleration:** meters/second².
- **Angles (public API):** degrees for config/UI, radians internally for trig.

## 2) Transform Model (Per-Entity)

Every dynamic entity should expose a transform object containing:

- `position: Vec3` (`x, y, z`)
- `rotation: Vec3` (`pitch, yaw, roll`) or quaternion equivalent
- `scale: Vec3` (default `1,1,1`)

### Migration Rule
When converting from the existing 2D map logic:

- old `x -> new x`
- old `y -> new z`
- default `new y = 0.0`

This keeps current gameplay on ground level while enabling vertical expansion later.

## 3) Gameplay-Safe Defaults

Until full 3D physics is introduced:

- Keep player movement constrained to `Y=0` (except future jump/fall states).
- Use simple collision proxies:
  - player/enemies: capsule/box approximation
  - static objects: AABB
- Preserve deterministic update order (input -> simulation -> collision -> render).

## 4) Debug Instrumentation (Required)

Add lightweight debug visibility while implementing Phase 1:

- On-screen player world position `(x, y, z)`.
- On-screen player forward vector.
- Optional marker for current camera target anchor.
- Toggle key for debug overlay on/off.

## 5) Acceptance Checklist (Phase 1 Exit Criteria)

- [ ] Player + environment coordinates are represented in 3D space.
- [ ] Existing movement still works in expected directions after axis remap.
- [ ] Collision behavior remains stable with temporary 3D proxies.
- [ ] Debug overlay shows valid position/vector data in runtime.
- [ ] Existing automated tests still pass.

## 6) Suggested Implementation Order

1. Add shared constants for axis/unit conventions.
2. Introduce `Vec3`-based transform structure and adapt player first.
3. Create 2D->3D coordinate adapter for map/entity loading.
4. Add temporary collision proxies in world space.
5. Add debug overlay hooks + toggle.
6. Validate with smoke tests and automated tests.

## 7) Out of Scope for Phase 1

- Final character controller feel tuning.
- Production animation graphs.
- Final art/model replacement.
- Full ballistic weapon systems.

These are handled in later phases of the migration plan.
