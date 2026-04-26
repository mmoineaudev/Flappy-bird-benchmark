# USE CASE UC-02-Play Level

**Context of use:** Player controls the paddle to bounce a ball and destroy all bricks in the current level while keeping the ball in play.

**Scope:** RogueBreaker — System scope, black box

**Level:** User-goal

**Primary Actor:** Player

**Stakeholders & Interests:**
- Player: Wants to clear the level efficiently, earn points, and keep the ball alive.
- Game Engine: Needs accurate collision detection and physics updates every frame.
- RogueBreaker System Owner: Wants fair gameplay where skill determines success, not randomness or bugs.
- Score Tracker (off-stage): Needs accurate point tallies for end-of-run statistics.

**Precondition:** A level is loaded and rendered. The game is in Playing state. Ball and paddle are active.

**Minimal Guarantees:** If the ball is lost, lives are decremented and the Player is given a chance to continue or face Game Over. Score changes are always logged regardless of outcome.

**Success Guarantees:** All destructible bricks are destroyed. The game transitions to Level Complete state with updated score and an offer to choose a modifier.

**Trigger:** Level begins (either first level or after modifier selection).

## Main Success Scenario

1. Player: moves the paddle horizontally using keyboard controls.
2. RogueBreaker: renders ball trajectory and updates physics each frame.
3. RogueBreaker: detects ball-brick collisions and applies damage based on brick type and active modifiers.
4. RogueBreaker: destroys bricks that reach zero HP, awards points to Player, and resolves combo bonuses.
5. RogueBreaker: handles special brick behaviors (explosive AOE, shooter projectiles, portal teleportation).
6. RogueBreaker: detects when all destructible bricks are destroyed.
7. RogueBreaker: transitions to Level Complete state and presents the modifier selection screen.

## Extensions

1a. Active modifiers alter paddle behavior:
    - RogueBreaker applies active modifier effects (e.g., Dual Paddle, Broad Sweep) to movement handling.

2a. Ball strikes a wall:
    - RogueBreaker reflects the velocity vector off the wall boundary.

2b. Ball strikes the paddle:
    - RogueBreaker reflects the ball upward and adjusts angle based on strike position; applies bounce boost modifier if active.

3a. Brick has multiple HP:
    - RogueBreaker reduces brick HP, updates visual feedback (crack effect), and continues without destruction.

3b. Color Sync modifier is active and paddle color matches brick:
    - RogueBreaker applies +200% damage and bonus points on this collision.

3c. Explosive brick is destroyed:
    - RogueBreaker triggers AOE damage to adjacent bricks within blast radius.

3d. Shooter brick fires a projectile:
    - RogueBreaker spawns enemy projectile; if it hits the paddle, Player loses HP or life.

4a. Combo multiplier applies:
    - RogueBreaker increments combo counter on consecutive quick destroys and awards multiplied points.

5a. Portal brick is hit:
    - RogueBreaker teleports the ball to a paired portal brick's position with preserved velocity direction.

5b. Bonus brick drops an item:
    - RogueBreaker spawns a collectible item; Player must move paddle under it to collect.

2c. Ball falls below the arena floor:
    - RogueBreaker decrements lives, removes the ball from play.
    - If lives remain: RogueBreaker respawns the ball and returns to step 1.
    - If lives reach zero: (See UC-04-Handle Game Over)

3e. Timeshift modifier is active and Player toggles time scale:
    - RogueBreaker adjusts global time scale between 0.5x and 1.5x.

## Technology and Data Variations List

- Step 1: Paddle movement uses Arrow keys or A/D keys; Dual Paddle modifier uses separate key pairs.
- Step 2: Physics updates run at 60fps using requestAnimationFrame.
- Step 3: Collision detection uses THREE.Box3 AABB checks with custom velocity reflection logic.
- Step 4: Brick types include Normal (1HP), Hard (3HP), Fragile (1HP, breaks easily), Explosive, Shooter, Portal, Bonus.

## Related Information

- **Priority:** 1 (highest)
- **Channels:** Web browser — Playing state
- **Frequency:** Once per level in a run
- **Open Issues:** What is the combo time window? How many points per brick type? Should ball speed increase per level?
