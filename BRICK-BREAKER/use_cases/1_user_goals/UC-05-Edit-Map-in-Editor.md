# USE CASE UC-05-Edit Map in Editor

**Context of use:** Player uses the built-in Map Editor to design a custom level layout with various brick types, spawners, and settings.

**Scope:** RogueBreaker — System scope, black box

**Level:** User-goal

**Primary Actor:** Player

**Stakeholders & Interests:**
- Player: Wants intuitive tools to create fun, balanced levels quickly.
- RogueBreaker System Owner: Wants editor-generated maps to be valid, playable, and compatible with the game engine.
- localStorage (off-stage): Maps must fit within storage quota limits.

**Precondition:** RogueBreaker is loaded and the Main Menu is displayed. Player has selected the Map Editor option.

**Minimal Guarantees:** Unsaved work is preserved during editing session. Validation errors are clearly communicated before any save attempt. The editor cannot produce data that crashes the game engine.

**Success Guarantees:** A valid map is created with correct JSON schema, passes all validation checks, and is ready to be saved or played.

**Trigger:** Player selects "Map Editor" from the Main Menu.

## Main Success Scenario

1. RogueBreaker: opens the Map Editor interface with a blank grid canvas and tool palette.
2. Player: selects an editing tool (Brush, Fill, Eraser, or Pattern Generator).
3. Player: places or modifies tiles on the grid using mouse or keyboard interactions.
4. Player: configures spawners (placement, fire rate, projectile type) if desired.
5. Player: sets map metadata (name, difficulty, layout seed).
6. RogueBreaker: validates the map — checks bounds, tile type validity, spawn limits, and overall playability.
7. RogueBreaker: confirms successful validation and offers to save or preview the map.

## Extensions

1a. Player chooses to edit an existing saved map instead of a blank grid:
    - RogueBreaker loads the selected map into the editor; proceed to step 2.

2a. Pattern Generator is selected:
    - RogueBreaker presents pattern options (Pyramid, Checkerboard, Spiral, Random, Custom).
    - Player selects a pattern and applies it to the grid.
    - Proceed to step 3 for any manual adjustments.

3a. Player places a tile outside valid grid bounds:
    - RogueBreaker rejects the placement and highlights the valid area.

3b. Player uses Fill tool:
    - RogueBreaker fills contiguous region of the same tile type from the clicked cell outward.

4a. Spawner count exceeds maximum limit:
    - RogueBreaker informs the Player of the limit and prevents additional spawners.

4b. Invalid projectile type selected for spawner:
    - RogueBreaker rejects the configuration and prompts reselection.

6a. Validation detects errors:
    - RogueBreaker lists specific validation failures (out-of-bounds tiles, invalid types, exceeding spawn limits).
    - Player returns to step 3 to fix errors, then re-validates at step 6.

7a. Preview mode selected:
    - RogueBreaker generates a live Three.js preview of the map for testing; Player can return to editing after preview.

## Technology and Data Variations List

- Step 1: Grid canvas is DOM-based overlay (e.g., 12x8 grid) with clickable cells rendered as styled divs.
- Step 3: Tile types include Normal, Hard (3HP), Fragile (1HP), Explosive, Shooter, Portal, Bonus — each with distinct visual representation.
- Step 6: Validation checks: grid bounds compliance, tile type enumeration, spawner count limits, portal pairing completeness.

## Related Information

- **Priority:** 2
- **Channels:** Web browser — Map Editor overlay
- **Frequency:** Occasional — Player creates new maps periodically
- **Open Issues:** What is the maximum grid size? Maximum spawners per map? Should there be a difficulty rating calculator? Is there an undo/redo system?