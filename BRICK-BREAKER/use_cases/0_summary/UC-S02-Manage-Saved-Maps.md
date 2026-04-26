# USE CASE UC-S02-Manage Saved Maps

**Context of use:** The Player creates, saves, loads, and organizes custom game maps using the built-in Map Editor and localStorage persistence.

**Scope:** RogueBreaker — System scope, black box

**Level:** Summary

**Primary Actor:** Player

**Stakeholders & Interests:**
- Player: Wants to design custom levels and reuse them across multiple play sessions.
- RogueBreaker System Owner: Wants map data stored in a portable, validated format that won't corrupt the game.
- localStorage: Has limited storage capacity — maps must be reasonably sized.

**Precondition:** RogueBreaker is loaded in a web browser.

**Minimal Guarantees:** All map data is validated before saving to prevent corruption. Failed saves do not lose unsaved work. Storage limits are communicated to the Player.

**Success Guarantees:** Maps are persistently stored and can be reliably loaded for gameplay across browser sessions.

**Trigger:** Player selects "Map Editor" or "Load Map" from the Main Menu.

## Main Success Scenario

1. Player: opens the Map Editor from the Main Menu.
2. RogueBreaker: presents the grid canvas with tool palette.
3. Player: designs a map layout using editing tools and tile types.
4. RogueBreaker: validates the map data for correctness.
5. RogueBreaker: saves the validated map to localStorage.
6. Player: loads a saved map from the Main Menu or Editor.
7. RogueBreaker: auto-generates the Three.js scene from the loaded JSON and enters gameplay.

## Extensions

2a. Map Editor fails to load:
    - RogueBreaker reports the error and returns to the Main Menu.

3a. Player abandons editing without saving:
    - RogueBreaker prompts to save or discard; returns to Main Menu on discard.

4a. Validation detects invalid map data:
    - RogueBreaker reports specific validation errors to the Player and returns to editing step 3.

5a. localStorage is full or unavailable:
    - RogueBreaker notifies the Player to delete existing maps or clear browser data before saving.

6a. Saved map JSON is corrupted or incompatible:
    - RogueBreaker detects invalid format, reports to Player, offers deletion of the corrupt map.

7a. Loaded map produces an unplayable layout:
    - RogueBreaker falls back to a default level and reports the issue.

## Technology and Data Variations List

- Step 5: Storage uses `localStorage.setItem('roguebreaker_maps', JSON.stringify(mapArray))`.
- Step 6: Map selection via dropdown in Main Menu or within Editor interface.
- Step 7: Three.js scene generation maps JSON tile data to InstancedMesh objects.

## Related Information

- **Priority:** 2
- **Channels:** Web browser
- **Frequency:** Occasional — Player creates new maps periodically, loads saved maps regularly
- **Open Issues:** What is the maximum number of maps? Should there be a map rating/difficulty system? How to handle localStorage quota limits (typically 5-10MB)?
