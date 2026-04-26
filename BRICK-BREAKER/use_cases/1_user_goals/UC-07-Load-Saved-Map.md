# USE CASE UC-07-Load Saved Map

**Context of use:** Player selects a previously saved map from localStorage to play or edit.

**Scope:** RogueBreaker — System scope, black box

**Level:** User-goal

**Primary Actor:** Player

**Stakeholders & Interests:**
- Player: Wants to quickly find and load a desired saved map for gameplay or editing.
- Game Engine: Needs valid map data to generate a playable Three.js scene without errors.
- RogueBreaker System Owner: Wants the loading process to handle corrupted or outdated maps gracefully.

**Precondition:** At least one map is saved in localStorage. The Main Menu or Map Editor is displayed.

**Minimal Guarantees:** If no maps exist, the Player is informed. Corrupted maps are detected and reported without crashing the game. The Player can always fall back to default levels.

**Success Guarantees:** The selected map is loaded, validated, and converted into a playable Three.js scene or editable grid. Game state is properly initialized for the loaded level.

**Trigger:** Player selects "Load Map" from the Main Menu or selects a saved map within the Map Editor.

## Main Success Scenario

1. RogueBreaker: retrieves the maps array from localStorage and presents available maps in a selection list.
2. Player: selects a map from the list.
3. RogueBreaker: validates the selected map JSON for schema compliance and data integrity.
4. RogueBreaker: converts the map data into Three.js scene objects (instanced meshes for bricks, spawner entities).
5. RogueBreaker: initializes game state with the loaded level and enters Playing or Editing state as appropriate.

## Extensions

1a. No maps are saved in localStorage:
    - RogueBreaker informs the Player that no saved maps exist and offers to go to the Map Editor or play default levels.

2a. Player cancels map selection:
    - RogueBreaker returns to the previous screen (Main Menu or Editor).

3a. Map JSON is corrupted or schema-incompatible:
    - RogueBreaker detects the error, reports it to the Player, and offers to delete the corrupt map or try another.

3b. Validation reveals missing required fields:
    - RogueBreaker lists specific missing fields and asks whether to attempt loading with defaults or choose a different map.

4a. Map dimensions exceed supported grid size:
    - RogueBreaker warns about oversized map, offers to load with clipping or choose another.

4b. Map contains unsupported tile types (from a newer version):
    - RogueBreaker replaces unsupported types with Normal tiles and notifies the Player.

5a. Scene generation fails due to invalid spawner configuration:
    - RogueBreaker skips invalid spawners, loads remaining data, and issues a warning to the Player.

## Technology and Data Variations List

- Step 1: Map selection via dropdown (Main Menu) or grid thumbnail preview (Editor).
- Step 4: Three.js scene uses InstancedMesh for static bricks; dynamic entities (spawners, portals) use individual meshes.
- Step 5: Game state initialization resets score and lives to defaults unless continuing a run.

## Related Information

- **Priority:** 2
- **Channels:** Web browser — Main Menu or Map Editor
- **Frequency:** Regularly by players who create custom maps
- **Open Issues:** Should there be map preview/thumbnail generation? How to handle version migration when game schema changes? Search/filter saved maps by name or difficulty?