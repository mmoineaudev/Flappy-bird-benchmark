# USE CASE UC-06-Save Map to localStorage

**Context of use:** Player saves a designed map from the Map Editor to browser localStorage for future use.

**Scope:** RogueBreaker — System scope, black box

**Level:** User-goal

**Primary Actor:** Player

**Stakeholders & Interests:**
- Player: Wants their custom map saved reliably and retrievable later.
- RogueBreaker System Owner: Wants stored maps in a consistent, validated JSON format that won't corrupt the game.
- localStorage (off-stage): Has browser-imposed storage limits; old or unused maps may need pruning.

**Precondition:** A map has been designed in the Map Editor and passed validation checks. The editor is offering to save.

**Minimal Guarantees:** If saving fails, the unsaved work remains available in the editor session. No partial or corrupt data is written to localStorage.

**Success Guarantees:** Map is persisted to localStorage with a unique ID, valid JSON schema, and metadata. The Player receives confirmation of successful save.

**Trigger:** Player selects "Save" from the Map Editor after designing a map.

## Main Success Scenario

1. Player: confirms the save action in the Map Editor.
2. RogueBreaker: serializes the map data into the canonical JSON schema (id, name, gridWidth, gridHeight, tiles array, spawners array, layoutSeed, difficulty).
3. RogueBreaker: assigns a unique map ID if none exists.
4. RogueBreaker: appends the serialized map to the existing maps array in localStorage.
5. RogueBreaker: confirms successful save to the Player with the assigned map ID and name.

## Extensions

2a. Map data fails final serialization check:
    - RogueBreaker reports the specific error and returns to editing; save is aborted.

3a. Map ID conflicts with an existing saved map:
    - RogueBreaker generates a new unique ID (e.g., appends timestamp or increments counter).

3b. Player wants to overwrite an existing map:
    - RogueBreaker prompts for confirmation, replaces the existing map entry, and proceeds to step 4.

4a. localStorage quota exceeded:
    - RogueBreaker notifies the Player that storage is full and offers to delete one of the oldest maps or cancel the save.

4b. localStorage is unavailable (private browsing mode, browser restrictions):
    - RogueBreaker reports that saving is unavailable and suggests using a standard browser session.

## Technology and Data Variations List

- Step 2: JSON schema follows the format defined in the specification with required fields: id, name, gridWidth, gridHeight, tiles[], spawners[].
- Step 4: Storage call uses `localStorage.setItem('roguebreaker_maps', JSON.stringify(mapArray))`.

## Related Information

- **Priority:** 3
- **Channels:** Web browser — Map Editor
- **Frequency:** Once per map creation session
- **Open Issues:** Maximum number of stored maps? Should there be a map management screen (rename, delete, duplicate)? Export/import functionality for sharing maps?