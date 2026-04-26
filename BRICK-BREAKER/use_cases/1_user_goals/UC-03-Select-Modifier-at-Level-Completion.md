# USE CASE UC-03-Select Modifier at Level Completion

**Context of use:** After clearing a level, the Player is presented with three random modifiers from the pool and chooses one to permanently alter gameplay for the remainder of the run.

**Scope:** RogueBreaker — System scope, black box

**Level:** User-goal

**Primary Actor:** Player

**Stakeholders & Interests:**
- Player: Wants meaningful choices that enhance strategy and fun; wants clear descriptions of what each modifier does.
- Game Engine: Needs to correctly apply modifiers without breaking existing mechanics or causing conflicts.
- RogueBreaker System Owner: Wants the modifier pool to provide replayability variety while maintaining balance.
- Score Tracker (off-stage): Modifier selections are logged for end-of-run statistics and potential leaderboard data.

**Precondition:** All destructible bricks in the current level are destroyed. The game is in Level Complete state.

**Minimal Guarantees:** The Player always sees three valid modifier options. If conflicts exist with active modifiers, the system clearly communicates the resolution behavior. Selection is logged regardless of outcome.

**Success Guarantees:** The chosen modifier is applied and registered in the active modifiers list. Conflicts are resolved per rules. The game advances to the next level with updated gameplay mechanics.

**Trigger:** Level completion detected (all bricks destroyed).

## Main Success Scenario

1. RogueBreaker: pauses gameplay and transitions to Modifier Selection screen.
2. RogueBreaker: selects three random modifiers from the available pool and displays them as cards with name, description, and visual preview.
3. Player: reviews the three modifier options.
4. Player: selects one modifier using keyboard input (1, 2, or 3).
5. RogueBreaker: validates the selection and resolves any conflicts with active modifiers.
6. RogueBreaker: applies the modifier, updates paddle/ball state, registers in activeModifiers[], and logs the choice.
7. RogueBreaker: advances to the next level and resumes gameplay.

## Extensions

2a. Fewer than three valid modifiers remain in the pool:
    - RogueBreaker presents all available options (1 or 2) and allows selection from reduced set.

2b. All offered modifiers conflict with active modifiers:
    - RogueBreaker regenerates the offer set until at least one non-conflicting option is available.

4a. Player selects a modifier that conflicts with an active modifier:
    - RogueBreaker informs the Player of the conflict and offers to overwrite the conflicting modifier or choose again.
    - If Player confirms overwrite: the conflicting modifier is removed and the new one is applied; proceed to step 5.
    - If Player chooses again: return to step 3.

4b. Player wants to decline all offered modifiers:
    - RogueBreaker allows skipping; advances to next level without a new modifier.

5a. Modifier stacking cap reached (e.g., bounce_boost capped at 4):
    - RogueBreaker informs the Player that this modifier is already at maximum stack and prompts reselection.

6a. Modifier application fails due to state inconsistency:
    - RogueBreaker rolls back the modification, logs the error, advances to next level without applying it.

7a. Next level data is invalid or unavailable:
    - RogueBreaker generates a fallback default level.

## Technology and Data Variations List

- Step 2: Modifier cards display icon, name, one-line description, stackability indicator, and conflict warnings.
- Step 6: Active modifiers stored as array of objects with id, effect type, stack count, and application timestamp.
- Step 7: Level advancement increments level counter; ball speed may increase per difficulty curve.

## Related Information

- **Priority:** 1 (highest)
- **Channels:** Web browser — Modifier Selection screen
- **Frequency:** Once per level in a run
- **Open Issues:** How many modifiers can be active simultaneously? Should there be a "reroll" option at a cost? What is the complete modifier pool and balance values?
