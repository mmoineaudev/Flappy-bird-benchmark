# USE CASE UC-SF02-Apply Modifiers to Gameplay

**Context of use:** The Modifier Engine processes the active modifiers list and applies their effects to paddle behavior, ball physics, scoring rules, and special abilities during gameplay.

**Scope:** RogueBreaker — Subsystem scope (Modifier Engine)

**Level:** Subfunction

**Primary Actor:** Game Engine

**Stakeholders & Interests:**
- Player: Wants modifiers to work as described, stack predictably, and enhance gameplay without introducing unfair advantages or bugs.
- Game Engine: Needs a reliable system for composing modifier effects that may interact in complex ways.
- RogueBreaker System Owner: Wants the modifier system to be data-driven (configurable without code changes), balanced, and maintainable.
- Score Tracker (off-stage): Modifier-dependent scoring rules must produce consistent point values.

**Precondition:** One or more modifiers are registered in the activeModifiers[] array. The game is in Playing state or transitioning between levels.

**Minimal Guarantees:** Conflicting modifiers are resolved deterministically. No modifier application causes invalid game states (NaN values, infinite loops). All modifier effects are reversible for clean state resets.

**Success Guarantees:** All active modifiers are correctly applied to their respective gameplay systems. Effects compose without unintended interactions. The Player experiences the combined modifier behavior as intended.

**Trigger:** Modifier selection by Player (UC-03) or game loop iteration requiring modifier effect evaluation.

## Main Success Scenario

1. Game Engine: reads the activeModifiers[] array and identifies all currently active modifiers.
2. Game Engine: checks each new modifier against existing active modifiers for conflicts.
3. Game Engine: resolves conflicts using established rules (overwrite, reject, or merge).
4. Game Engine: applies the modifier's effect to the relevant gameplay system.
5. Game Engine: updates the game state flags that intercept collision and update loops.
6. Game Engine: logs the modifier application with timestamp for run history tracking.

## Extensions

2a. No conflicts detected:
    - Proceed directly to step 4.

2b. Conflict detected — Overwrite type (e.g., split vs widen):
    - Game Engine removes the conflicting active modifier, applies the new one, and updates affected systems.

2c. Conflict detected — Reject type (e.g., multiball conflicts with split):
    - Game Engine rejects the new modifier, notifies the Player that it cannot be applied due to an active conflict.

2d. Conflict detected — Stackable within cap (e.g., bounce_boost capped at 4):
    - If stack count is below cap: Game Engine increments the stack level and scales the effect proportionally; proceed to step 4.
    - If stack count equals cap: Game Engine rejects the modifier as maxed out.

4a. Modifier is Dual Paddle (split):
    - Game Engine creates a second paddle entity with independent controls and updates input handling for dual-key mapping.

4b. Modifier is Broad Sweep (widen):
    - Game Engine increases paddle width by 40% per stack level applied to the paddle mesh scale.

4c. Modifier is Upward Fire (projectile):
    - Game Engine registers an auto-fire timer (1.5s interval) and enables manual fire on Space key; creates projectile spawning logic.

4d. Modifier is Ball Pull (magnet):
    - Game Engine registers a proximity-based trajectory curve that activates when ball enters the magnet radius around paddle center.

4e. Modifier is Elasticity (bounce_boost):
    - Game Engine registers a velocity multiplier (+15% per stack) applied to all paddle-ball reflections.

4f. Modifier is Barrier Wall (shield):
    - Game Engine creates a temporary wall mesh above the paddle with charge count; shield absorbs one brick break or ball miss then deactivates.

4g. Modifier is Clone Strike (multiball):
    - Game Engine registers special brick type detection; destroying a designated brick spawns 2 clone balls.

4h. Modifier is Slow/Speed Toggle (timeshift):
    - Game Engine registers T key binding to toggle global time scale between 0.5x and 1.5x.

4i. Modifier is Chromatic Damage (color_sync):
    - Game Engine registers color matching logic: when paddle color equals brick color, apply +200% damage and bonus points.

4j. Modifier is Assist Guide (autoaim):
    - Game Engine registers a subtle paddle drift behavior that nudges the paddle toward predicted ball trajectory.

5a. Modifier effect requires visual feedback update:
    - Game Engine updates HUD icons, tooltips, and any visual indicators for the newly active modifier.

6a. Run history logging fails:
    - Game Engine continues with modifier application; logs a warning but does not abort the use case.

## Technology and Data Variations List

- Step 1: Modifiers stored as objects: {id, name, effectType, stackCount, conflictsWith[], appliedAt}.
- Step 4: Effect application uses state flags that collision/update loops check each frame (e.g., `if (activeModifiers.includes('bounce_boost')) velocity *= 1.15`).
- Step 6: Run history stored in memory array for end-of-run statistics display.

## Related Information

- **Priority:** 1 (highest — core roguelike mechanic)
- **Channels:** Internal subsystem
- **Frequency:** On modifier selection and every game loop iteration
- **Open Issues:** Complete conflict matrix between all modifiers? Should there be a modifier limit (max active)? How to handle modifier removal when conflicts resolve?