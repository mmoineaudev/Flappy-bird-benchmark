# USE CASE UC-04-Handle Game Over

**Context of use:** The Player loses all lives and the game ends. Statistics are displayed and the Player is given options to continue.

**Scope:** RogueBreaker — System scope, black box

**Level:** User-goal

**Primary Actor:** Player

**Stakeholders & Interests:**
- Player: Wants to see a summary of their run (score, levels completed, modifiers used) and have clear options for what to do next.
- Score Tracker (off-stage): Needs final score recorded accurately for potential leaderboard submission.
- RogueBreaker System Owner: Wants the Game Over screen to encourage replay by showing progress and offering accessible retry options.

**Precondition:** The ball was lost and lives reached zero during gameplay. The game is in Playing state.

**Minimal Guarantees:** All run data (score, modifiers chosen, levels completed) is preserved and displayed. No data is lost. Player can always return to the Main Menu.

**Success Guarantees:** Game Over screen displays complete run statistics. Player chooses a follow-up action (retry, return to menu). Game state is cleanly reset if retrying.

**Trigger:** Lives counter reaches zero after ball loss.

## Main Success Scenario

1. RogueBreaker: detects lives reaching zero and halts gameplay.
2. RogueBreaker: compiles run statistics (final score, levels completed, modifiers active, combo record).
3. RogueBreaker: displays the Game Over screen with statistics and action options.
4. Player: selects an action (Retry Run or Return to Main Menu).
5. RogueBreaker: executes the selected action.

## Extensions

2a. No game data was accumulated (Player died on first ball):
    - RogueBreaker shows minimal statistics (score=0, level=1, no modifiers) and proceeds to step 3.

4a. Player selects Retry Run:
    - RogueBreaker resets game state (score=0, lives=default, level=1) but preserves active modifiers from the previous run.
    - RogueBreaker transitions back to Playing state with the first level.

4b. Player selects Return to Main Menu:
    - RogueBreaker clears all game state and returns to the Main Menu.

4c. Player selects View Replay:
    - RogueBreaker replays a summary of key moments from the run (if replay data was logged).

3a. Statistics compilation fails due to corrupted state:
    - RogueBreaker displays available data with a notice about incomplete statistics and proceeds to step 4.

## Technology and Data Variations List

- Step 2: Statistics include final score, highest combo, modifiers acquired in order, levels completed, time played.
- Step 3: Game Over screen uses DOM overlay with Three.js scene paused behind it.

## Related Information

- **Priority:** 2
- **Channels:** Web browser — Game Over screen
- **Frequency:** Once per failed run
- **Open Issues:** Should retry preserve modifiers or reset to clean state? Is there a high score system? Should runs be shareable (e.g., encoded URL)?