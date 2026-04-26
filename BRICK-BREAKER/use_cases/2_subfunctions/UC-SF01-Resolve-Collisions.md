# USE CASE UC-SF01-Resolve Collisions

**Context of use:** The Collision System detects and resolves interactions between the ball, paddle, bricks, walls, and projectiles every frame during gameplay.

**Scope:** RogueBreaker — Subsystem scope (Collision System)

**Level:** Subfunction

**Primary Actor:** Game Engine

**Stakeholders & Interests:**
- Player: Expects smooth, predictable physics where collisions feel fair and responsive.
- Game Engine: Needs deterministic collision results every frame to maintain gameplay integrity.
- RogueBreaker System Owner: Wants collision logic that is performant (60fps) and correct under all modifier combinations.
- Score Tracker (off-stage): Collision outcomes determine point awards that must be accurately recorded.

**Precondition:** The game is in Playing state. Ball, paddle, bricks, and arena boundaries are rendered in the Three.js scene. Active modifiers are registered.

**Minimal Guarantees:** Every collision event is detected and resolved without tunneling (ball passing through objects between frames). No collision result causes NaN or infinite values in velocity vectors.

**Success Guarantees:** All active collisions for the current frame are correctly resolved. Velocity vectors, HP values, and game state are updated consistently. The scene remains stable.

**Trigger:** Game loop iteration requests collision update.

## Main Success Scenario

1. Game Engine: collects bounding boxes (THREE.Box3) for all dynamic entities (ball, paddle, projectiles).
2. Game Engine: detects ball-wall collisions using arena boundary checks.
3. Game Engine: resolves wall collisions by reflecting the velocity vector off the struck surface.
4. Game Engine: detects ball-paddle collisions and calculates strike position offset.
5. Game Engine: computes new ball trajectory based on paddle hit position, applying active bounce modifiers.
6. Game Engine: detects ball-brick collisions using AABB overlap tests.
7. Game Engine: applies damage to collided bricks, resolves special behaviors, and awards points.

## Extensions

2a. Ball exceeds arena boundary on one axis:
    - Game Engine clamps position to boundary and reflects the corresponding velocity component.

3a. Ball velocity exceeds maximum threshold after reflection:
    - Game Engine caps velocity to prevent tunneling in the next frame.

4a. Dual Paddle modifier is active:
    - Game Engine checks ball collision against both paddle bounding boxes independently.

5a. Bounce Boost modifier is active:
    - Game Engine applies +15% velocity increase per stack level to the reflected vector.

5b. Color Sync modifier is active and paddle color matches brick color:
    - Game Engine applies +200% damage multiplier and bonus points on this collision.

5c. Magnet modifier is active and ball is within proximity threshold:
    - Game Engine subtly curves the ball trajectory toward paddle center before reflection.

6a. Brick has remaining HP after damage:
    - Game Engine reduces brick HP, updates visual state (crack effect), and does not destroy it.

6b. Explosive brick reaches zero HP:
    - Game Engine triggers AOE damage to all bricks within blast radius; processes secondary destructions recursively up to a depth limit.

6c. Portal brick is hit:
    - Game Engine teleports the ball to the paired portal position, preserving velocity direction relative to the new position.

6d. Multiball modifier is active and a special brick is destroyed:
    - Game Engine spawns 2 clone balls from the destroyed brick position with randomized velocities.

7a. Projectile-brick collision detected:
    - Game Engine applies projectile damage to the brick; removes projectile after impact.

7b. Enemy projectile hits paddle:
    - Game Engine reduces Player HP/lives and removes the projectile.

1a. Ball tunneling detected (ball passed through object between frames):
    - Game Engine performs a sweep test along the velocity vector to detect missed collisions and retroactively resolves them.

## Technology and Data Variations List

- Step 1: THREE.Box3 for AABB bounding boxes; updated each frame from mesh positions.
- Step 5: Paddle hit position maps to reflection angle using normalized offset (-1 to +1) scaled by maximum deflection angle.
- Step 6: Brick types determine damage response — Normal (1 dmg), Hard (requires multiple hits), Fragile (breaks on any contact).

## Related Information

- **Priority:** 1 (highest — core gameplay mechanic)
- **Channels:** Internal subsystem
- **Frequency:** Every frame (~60fps during gameplay)
- **Open Issues:** What is the maximum deflection angle from paddle hits? AOE blast radius for explosive bricks? Depth limit for recursive destruction?
