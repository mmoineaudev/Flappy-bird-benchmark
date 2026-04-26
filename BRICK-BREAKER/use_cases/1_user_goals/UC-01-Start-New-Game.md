# USE CASE UC-01-Start New Game

**Context of use:** Player begins a fresh game run from the Main Menu with default settings and no active modifiers.

**Scope:** RogueBreaker — System scope, black box

**Level:** User-goal

**Primary Actor:** Player

**Stakeholders & Interests:**
- Player: Wants to start playing immediately with a fair, consistent starting state.
- Game Engine: Needs clean initial state — default paddle, single ball, first level loaded.
- RogueBreaker System Owner: Wants every run begin identically so scores are comparable.

**Precondition:** RogueBreaker is loaded and the Main Menu is displayed.

**Minimal Guarantees:** If initialization fails, the Player is returned to the Main Menu with an error message. No partial state is left behind.

**Success Guarantees:** Game enters Playing state with default paddle, one ball, first level rendered, HUD visible, and no modifiers active.

**Trigger:** Player selects "Play" from the Main Menu.

## Main Success Scenario

1. Player: selects Play from the Main Menu.
2. RogueBreaker: initializes game state (score=0, lives=default, level=1, modifiers=[]).
3. RogueBreaker: sets up the Three.js scene with default paddle and ball.
4. RogueBreaker: loads the first level layout and renders bricks.
5. RogueBreaker: displays the HUD with initial values and transitions to Playing state.

## Extensions

2a. Game state initialization fails:
    - RogueBreaker reports the error to Player and returns to the Main Menu.

3a. Three.js scene setup fails (CDN unavailable, WebGL not supported):
    - RogueBreaker reports the failure to Player and returns to the Main Menu.

4a. First level data is missing or invalid:
    - RogueBreaker falls back to a built-in default layout.

## Technology and Data Variations List

- Step 2: Default lives may vary by difficulty setting (e.g., Easy=5, Normal=3, Hard=1).
- Step 4: Level source may be procedurally generated or loaded from a saved map.

## Related Information

- **Priority:** 1 (highest)
- **Channels:** Web browser — Main Menu
- **Frequency:** Once per game session
- **Open Issues:** Should difficulty selection happen before or after pressing Play? What are the default lives values?
