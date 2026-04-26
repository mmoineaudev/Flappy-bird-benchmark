# USE CASE UC-S01-Play a Run

**Context of use:** The Player engages in an extended roguelike Brick Breaker session, playing through multiple levels and choosing modifiers between them, until either achieving Victory or reaching Game Over.

**Scope:** RogueBreaker — System scope, black box

**Level:** Summary

**Primary Actor:** Player

**Stakeholders & Interests:**
- Player: Wants an engaging, replayable experience with meaningful choices and escalating challenge.
- Game Engine: Needs to maintain consistent state across level transitions and modifier applications.
- RogueBreaker System Owner: Wants the game to be fun, fair, and performant so players keep coming back.

**Precondition:** RogueBreaker is loaded in a web browser and the Main Menu is displayed.

**Minimal Guarantees:** The Player can always exit to the Main Menu. All progress up to the current level is logged for potential replay review. Game state is never corrupted across transitions.

**Success Guarantees:** The Player completes all levels or achieves the defined victory condition. A summary of the run (score, modifiers chosen, levels completed) is displayed.

**Trigger:** Player selects "Play" from the Main Menu.

## Main Success Scenario

1. Player: initiates a new game run.
2. RogueBreaker: presents the first level and begins gameplay.
3. Player: plays through levels, destroying bricks and surviving ball mechanics.
4. RogueBreaker: upon completing each level, offers three random modifiers for selection.
5. Player: selects one modifier from the offered choices.
6. RogueBreaker: applies the selected modifier and advances to the next level.
7. RogueBreaker: presents the final victory screen with run statistics when all levels are completed.

## Extensions

1a. Player cancels before starting:
    - RogueBreaker returns to the Main Menu.

2a. Ball is lost during gameplay:
    - (See UC-04-Handle Game Over)

3a. Player achieves Victory before completing all planned levels:
    - RogueBreaker presents the victory screen early with run statistics.

4a. No valid modifiers remain to offer:
    - RogueBreaker advances to the next level without offering a choice.

5a. Selected modifier conflicts with an active modifier:
    - (See UC-SF02-Apply Modifiers to Gameplay, Extension handling for conflict resolution)

6a. Level generation fails or produces an unplayable layout:
    - RogueBreaker retries level generation; if retry fails, returns to Main Menu.

7a. Player exits run voluntarily:
    - RogueBreaker confirms and returns to the Main Menu with partial run statistics.

## Technology and Data Variations List

- Step 2: Level layouts may be procedurally generated or loaded from saved maps.
- Step 4: Modifier pool composition varies based on game mode and difficulty settings.
- Step 7: Statistics displayed depend on which modifiers were active and levels completed.

## Related Information

- **Priority:** 1 (highest)
- **Channels:** Web browser
- **Frequency:** Core gameplay loop — primary reason the system exists
- **Open Issues:** How many levels constitute a full run? What is the victory condition exactly? Should runs be savable and resumable?
