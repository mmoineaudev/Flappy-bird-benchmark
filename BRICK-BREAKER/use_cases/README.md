# RogueBreaker — Use Case Library

## Scope Statement

**System:** RogueBreaker (single-file web application)

**Scope:** System scope — black box. The system is the RogueBreaker game application running in a web browser using Three.js and Vanilla JavaScript.

### In Scope

- Paddle movement and ball physics
- Brick destruction with HP, types, and special behaviors
- Roguelike modifier progression (selection, stacking, conflict resolution)
- Level-based gameplay loop (play level -> choose modifier -> next level)
- Scoring system and lives tracking
- Map Editor (DOM-based grid canvas for creating custom levels)
- Map storage (localStorage JSON persistence)
- HUD display (score, lives, level, active modifiers)
- Game states: Main Menu, Playing, Level Complete, Game Over, Victory, Editor

### Out of Scope

- Multiplayer / networked play
- Account system or user authentication
- Server-side leaderboard
- Sound engine or audio processing
- Mobile touch controls
- Asset pipeline or build tools

## Actors

| Actor | Type | Description |
|-------|------|-------------|
| Player | Primary | Human who plays the game, makes decisions, selects modifiers |
| Game Engine | Supporting | Core application logic — physics, rendering, state machine |
| Map Editor | Supporting | DOM-based interface for designing custom levels |
| localStorage | Supporting | Browser storage backend for persisting maps and settings |

## Actor-Goal List

### Primary Actor: Player

| Goal | Priority | Level | Use Case ID |
|------|----------|-------|-------------|
| Play a Run (multi-level with modifiers) | 1 | Summary | UC-S01 |
| Manage Saved Maps | 2 | Summary | UC-S02 |
| Start New Game | 1 | User-goal | UC-01 |
| Play Level | 1 | User-goal | UC-02 |
| Select Modifier at Level Completion | 1 | User-goal | UC-03 |
| Handle Game Over | 2 | User-goal | UC-04 |
| Edit Map in Editor | 2 | User-goal | UC-05 |
| Save Map to localStorage | 3 | User-goal | UC-06 |
| Load Saved Map | 2 | User-goal | UC-07 |

### Supporting Actor: Game Engine

| Goal | Priority | Level | Use Case ID |
|------|----------|-------|-------------|
| Resolve Collisions | 1 | Subfunction | UC-SF01 |
| Apply Modifiers to Gameplay | 1 | Subfunction | UC-SF02 |
| Manage Game State Transitions | 1 | Subfunction | UC-SF03 |

## Design Scope Boundary

```
+--------------------------------------------------+
|                    Web Browser                     |
| +------------------------------------------------+|
| |              RogueBreaker (System)              ||
| | +-------------+  +-----------+  +------------+ ||
| | |   Three.js   |  |   DOM UI   |  | localStorage||
| | |  Renderer    |  |  (HUD,     |  |  (maps,     ||
| | |              |  |   Editor)  |  |   config)   ||
| | +-------------+  +-----------+  +------------+ ||
| |                                                     |
| |  +-------+    +----------+      +--------------+   |
| |  |Paddle |    |   Ball   |      |    Bricks    |   |
| |  +-------+    +----------+      +--------------+   |
| |                                                     |
| |  +------------------------+                        |
| |  |  Modifier Engine       |                        |
| |  +------------------------+                        |
| |  +------------------------+                        |
| |  |  Collision System      |                        |
| |  +------------------------+                        |
| |  +------------------------+                        |
| |  |  Map Loader/Editor     |                        |
| |  +------------------------+                        |
| +------------------------------------------------+|
|                                                     |
+--------------------------------------------------+

Outside: Player (human), Sound Engine, Multiplayer Network, Account System
```

## Use Case Directory Structure

- `0_summary/` — Summary-level use cases (span multiple sessions)
- `1_user_goals/` — User-goal-level use cases (completed in one sitting)
- `2_subfunctions/` — Subfunction-level use cases (partial goals, internal system behavior)
