# USE CASE UC-SF03-Manage Game State Transitions

**Context of use:** The game state machine manages transitions between discrete states (Main Menu, Playing, Level Complete, Game Over, Victory, Editor) ensuring clean handoff of data and UI at each boundary.

**Scope:** RogueBreaker — Subsystem scope (State Machine)

**Level:** Subfunction

**Primary Actor:** Game Engine

**Stakeholders & Interests:**
- Player: Expects smooth, predictable transitions without jarring visual glitches or lost progress.
- Game Engine: Needs deterministic state transitions with proper cleanup and initialization at each boundary.
- RogueBreaker System Owner: Wants a maintainable state machine that prevents invalid transitions and dangling references.
- Score Tracker (off-stage): State transitions trigger data capture points for statistics logging.

**Precondition:** The game is in a valid current state. A transition trigger has been detected.

**Minimal Guarantees:** No transition leaves orphaned objects, event listeners, or timers in memory. The Three.js scene and DOM UI are always synchronized with the current state. Invalid transitions are rejected.

**Success Guarantees:** The game enters the target state with all systems properly initialized. UI reflects the new state. Gameplay resumes or displays appropriately.

**Trigger:** Actor action (Player input), time event, or state change detection from other subsystems.

## Main Success Scenario

1. Game Engine: detects a transition trigger (level complete, ball loss, Player menu selection).
2. Game Engine: validates that the requested transition is allowed from the current state.
3. Game Engine: performs exit actions for the current state (stop timers, dispose scene objects, clear event listeners).
4. Game Engine: updates the state variable to the target state.
5. Game Engine: performs entry actions for the target state (initialize systems, render UI, start timers).
6. Game Engine: notifies all subsystems of the state change so they can adjust behavior.

## Extensions

2a. Transition is not allowed from current state:
    - Game Engine rejects the transition and logs the invalid attempt.
    - If triggered by Player input: Game Engine provides feedback explaining why the action is unavailable.

3a. Current state has active animations or transitions in progress:
    - Game Engine waits for completion before proceeding to step 3.

3b. Cleanup fails to dispose all resources:
    - Game Engine logs a warning about potential memory leak but proceeds with transition.

4a. Target state is Playing:
    - Game Engine initializes physics, spawns ball and paddle, loads level data, starts game loop.

4b. Target state is Level Complete:
    - Game Engine pauses the game loop, freezes scene rendering, prepares modifier selection UI.

4c. Target state is Game Over:
    - Game Engine halts all gameplay systems, compiles final statistics, displays Game Over screen.

4d. Target state is Victory:
    - Game Engine halts gameplay, displays Victory screen with complete run statistics and celebration effects.

4e. Target state is Main Menu:
    - Game Engine clears all gameplay state, disposes scene objects, resets to default configuration, displays Main Menu UI.

4f. Target state is Editor:
    - Game Engine switches from Three.js gameplay rendering to DOM-based Map Editor grid canvas.

5a. Entry actions fail (e.g., level data unavailable for Playing state):
    - Game Engine falls back to a safe default state (Main Menu) and reports the failure.

6a. Subsystem fails to respond to state change notification:
    - Game Engine logs the unresponsive subsystem but continues; degraded functionality may occur in the target state.

1a. Trigger is time-based (e.g., projectile timer, shield duration):
    - Game Engine evaluates whether the timed event causes a state transition or only a gameplay update.

## Technology and Data Variations List

- Step 4: State machine uses an enum or string-based state variable: MENU, PLAYING, LEVEL_COMPLETE, GAME_OVER, VICTORY, EDITOR.
- Step 6: Subsystem notifications via callback registration pattern; each subsystem registers handlers for relevant state transitions.
- Scene management: Three.js scene objects are grouped by state; groups are shown/hidden or disposed/recreated on transition.

## Related Information

- **Priority:** 1 (highest — foundational architecture)
- **Channels:** Internal subsystem
- **Frequency:** Once per state change (multiple times per game session)
- **Open Issues:** Should there be a visual transition effect between states? How to handle rapid Player input during transitions (input buffering)? Maximum acceptable transition time before timeout?