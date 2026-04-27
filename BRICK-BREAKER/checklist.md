# RogueBreaker - Implementation Checklist

This checklist is derived from the use case specifications and is designed to guide an AI agent through implementing the complete Brick Breaker roguelike game. Each item includes a reference to its source use case via markdown links.

## Core Game Loop & State Management

- [x] **Implement state machine for game states** ([UC-S03-Manage Game State Transitions](use_cases/2_subfunctions/UC-SF03-Manage-Game-State-Transitions.md))
  - [x] Define state enum: MENU, PLAYING, LEVEL_COMPLETE, GAME_OVER, VICTORY, EDITOR
  - [x] Implement transition validation logic
  - [x] Create exit actions for each state (cleanup timers, dispose objects, clear listeners)
  - [x] Create entry actions for each state (initialize systems, render UI, start timers)
  - [x] Implement subsystem notification system for state changes

- [x] **Implement Main Menu interface** ([UC-S01-Play a Run](use_cases/0_summary/UC-S01-Play-a-Run.md), [UC-01-Start New Game](use_cases/1_user_goals/UC-01-Start-New-Game.md))
  - [x] Create Main Menu UI with Play, Quick Play, Map Editor, Load Map options
  - [x] Implement "Play" button handler that initializes game state
  - [x] Implement "Quick Play" button for instant default map gameplay
  - [x] Add exit/cancel functionality returning to menu

- [x] **Implement game initialization** ([UC-01-Start New Game](use_cases/1_user_goals/UC-01-Start-New-Game.md))
  - [x] Initialize default game state (score=0, lives=default, level=1, modifiers=[])
  - [x] Set up Three.js scene with default paddle and ball
  - [x] Load first level layout (procedural or default)
  - [x] Display HUD with initial values
  - [x] Handle initialization failures gracefully

- [x] **Implement game loop at 60fps** ([UC-02-Play Level](use_cases/1_user_goals/UC-02-Play-Level.md))
  - [x] Use requestAnimationFrame for physics updates
  - [x] Update ball trajectory and physics each frame
  - [x] Handle special brick behaviors (explosive, shooter, portal, bonus)
  - [x] Track combo multiplier on consecutive quick destroys

## Collision System

- [x] **Implement collision detection subsystem** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [x] Use THREE.Box3 for AABB bounding boxes on all dynamic entities
  - [x] Implement ball-wall collision with velocity reflection
  - [x] Clamp positions to boundaries and cap velocity thresholds
  - [x] Handle tunneling detection with sweep tests

- [x] **Implement ball-paddle collision** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [x] Calculate strike position offset for reflection angle
  - [x] Apply bounce modifiers (Bounce Boost, Magnet)
  - [x] Support Dual Paddle modifier with independent collision checks
  - [x] Map hit position to deflection angle (-1 to +1 range)

- [x] **Implement ball-brick collision** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [x] Apply damage based on brick type and active modifiers
  - [x] Handle multi-HP bricks with visual crack feedback
  - [x] Implement Explosive brick AOE damage with recursion limit
  - [x] Handle Portal brick teleportation with paired portals
  - [x] Award points and resolve combo bonuses

- [x] **Implement projectile collision** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [x] Detect projectile-brick collisions
  - [x] Handle enemy projectile hitting paddle (HP/life loss)
  - [x] Remove projectiles after impact

## Paddle & Ball Mechanics

- [x] **Implement paddle controls** ([UC-02-Play Level](use_cases/1_user_goals/UC-02-Play-Level.md))
  - [x] Support Arrow keys or A/D for horizontal movement
  - [x] Implement Dual Paddle modifier with separate key pairs
  - [x] Apply Broad Sweep modifier (40% width increase per stack)
  - [x] Apply Assist Guide modifier (subtle paddle drift toward ball)

- [x] **Implement ball physics** ([UC-02-Play Level](use_cases/1-up_goals/UC-02-Play-Level.md))
  - [x] Reflect velocity vector off walls with proper angle calculation
  - [x] Apply bounce boost modifier (+15% velocity per stack)
  - [x] Implement Magnet effect (trajectory curve toward paddle)
  - [x] Handle ball falling below arena floor (life loss)
  - [x] Respawn ball when lives remain

- [x] **Implement Multiball mechanic** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [x] Spawn clone balls from destroyed special bricks
  - [x] Assign randomized velocities to cloned balls
  - [x] Handle multiball collision with appropriate modifiers

## Level System

- [x] **Implement level progression** ([UC-S01-Play a Run](use_cases/0_summary/UC-S01-Play-a-Run.md), [UC-02-Play Level](use_cases/1_user_goals/UC-02-Play-Level.md))
  - [x] Track current level number and increment on completion
  - [x] Detect when all destructible bricks are destroyed
  - [x] Transition to Level Complete state on victory
  - [x] Handle level generation failures with fallback defaults
  - [x] Support both procedural and saved map levels

- [x] **Implement brick types** ([UC-02-Play Level](use_cases/1_user_goals/UC-02-Play-Level.md))
  - [x] Normal brick (1 HP)
  - [x] Hard brick (3 HP)
  - [x] Fragile brick (breaks easily)
  - [x] Explosive brick (AOE damage on destruction)
  - [x] Shooter brick (fires projectiles)
  - [x] Portal brick (teleports ball to paired portal)
  - [x] Bonus brick (drops collectible items)

- [x] **Implement spawner system** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [x] Configure spawner placement and fire rate
  - [x] Support different projectile types
  - [x] Enforce maximum spawner count per map
  - [x] Validate spawner configuration on load

## Modifier System

- [x] **Implement modifier selection interface** ([UC-03-Select Modifier at Level Completion](use_cases/1_user_goals/UC-03-Select-Modifier-at-Level-Completion.md))
  - [x] Pause gameplay and transition to Modifier Selection screen
  - [x] Select three random modifiers from available pool
  - [x] Display modifier cards with icon, name, description, stackability
  - [x] Show conflict warnings for incompatible modifiers
  - [x] Allow keyboard selection (1, 2, or 3 keys)

- [x] **Implement modifier application logic** ([UC-SF02-Apply Modifiers to Gameplay](use_cases/2_subfunctions/UC-SF02-Apply-Modifiers-to-Gameplay.md))
  - [x] Read activeModifiers[] array each frame
  - [x] Check for conflicts between new and existing modifiers
  - [x] Resolve conflicts: overwrite, reject, or stack
  - [x] Apply modifier effects to relevant gameplay systems
  - [x] Update state flags intercepted by collision/update loops
  - [x] Log modifier application with timestamp for run history

- [x] **Implement conflict resolution rules** ([UC-SF02-Apply Modifiers to Gameplay](use_cases/2_subfunctions/UC-SF02-Apply-Modifiers-to-Gameplay.md))
  - [x] Define overwrite conflicts (e.g., split vs widen)
  - [x] Define reject conflicts (e.g., multiball vs split)
  - [x] Define stackable modifiers with caps (e.g., bounce_boost max 4)
  - [x] Handle conflict warnings to Player before selection

- [x] **Implement individual modifiers** ([UC-SF02-Apply Modifiers to Gameplay](use_cases/2_subfunctions/UC-SF02-Apply-Modifiers-to-Gameplay.md))
  - [x] Dual Paddle (split) - creates second paddle with independent controls
  - [x] Broad Sweep (widen) - increases paddle width by 40% per stack
  - [x] Upward Fire (projectile) - auto-fire timer and manual fire on Space
  - [x] Ball Pull (magnet) - proximity-based trajectory curve
  - [x] Elasticity (bounce_boost) - +15% velocity multiplier per stack
  - [x] Barrier Wall (shield) - temporary wall with charge count
  - [x] Clone Strike (multiball) - spawns clone balls on special brick destroy
  - [x] Slow/Speed Toggle (timeshift) - toggle time scale 0.5x-1.5x
  - [x] Chromatic Damage (color_sync) - +200% damage when colors match
  - [x] Assist Guide (autoaim) - subtle paddle drift toward ball trajectory

## Game Over & Victory Systems

- [x] **Implement life and death tracking** ([UC-02-Play Level](use_cases/1_user_goals/UC-02-Play-Level.md), [UC-04-Handle Game Over](use_cases/1_user_goals/UC-04-Handle-Game-Over.md))
  - [x] Decrement lives when ball is lost
  - [x] Detect when lives reach zero
  - [x] Respawn ball when lives remain
  - [x] Handle difficulty-based default lives (Easy=5, Normal=3, Hard=1)

- [x] **Implement Game Over screen** ([UC-04-Handle Game Over](use_cases/1_user_goals/UC-04-Handle-Game-Over.md))
  - [x] Detect lives reaching zero and halt gameplay
  - [x] Compile run statistics (score, levels, modifiers, combo record)
  - [x] Display Game Over screen with statistics overlay
  - [x] Provide action options: Retry Run, Return to Main Menu, View Replay
  - [x] Handle edge case of immediate death (score=0, no modifiers)

- [x] **Implement retry mechanics** ([UC-04-Handle Game Over](use_cases/1_user_goals/UC-04-Handle-Game-Over.md))
  - [x] Reset game state (score=0, lives=default, level=1)
  - [x] Decide whether to preserve or reset active modifiers on retry
  - [x] Transition back to Playing state with first level

- [x] **Implement Victory condition** ([UC-S01-Play a Run](use_cases/0_summary/UC-S01-Play-a-Run.md))
  - [x] Detect completion of all planned levels
  - [x] Display Victory screen with run statistics
  - [x] Show celebration effects and final summary

## Map Editor & Save System

- [x] **Implement Map Editor interface** ([UC-05-Edit Map in Editor](use_cases/1_user_goals/UC-05-Edit-Map-in-Editor.md))
  - [x] Create grid canvas (DOM-based, e.g., 12x8) with clickable cells
  - [x] Implement tool palette: Brush, Fill, Eraser, Pattern Generator
  - [x] Display tile types with distinct visual representation
  - [x] Support editing existing saved maps

- [x] **Implement map editing tools** ([UC-05-Edit Map in Editor](use_cases/1_user_goals/UC-05-Edit-Map-in-Editor.md))
  - [x] Brush tool for placing individual tiles
  - [x] Fill tool for contiguous region filling
  - [x] Pattern Generator with options: Pyramid, Checkerboard, Spiral, Random, Custom
  - [x] Validate placements against grid bounds

- [x] **Implement spawner configuration in editor** ([UC-05-Edit Map in Editor](use_cases/1_user_goals/UC-05-Edit-Map-in-Editor.md))
  - [x] Configure spawner placement and fire rate
  - [x] Select projectile type for spawners
  - [x] Enforce maximum spawner count limit

- [x] **Implement map metadata** ([UC-05-Edit Map in Editor](use_cases/1_user_goals/UC-05-Edit-Map-in-Editor.md))
  - [x] Set map name
  - [x] Set difficulty level
  - [x] Set layout seed for procedural generation

- [x] **Implement validation system** ([UC-05-Edit Map in Editor](use_cases/1_user_goals/UC-05-Edit-Map-in-Editor.md), [UC-06-Save Map to localStorage](use_cases/1_user_goals/UC-06-Save-Map-to-LocalStorage.md))
  - [x] Check grid bounds compliance
  - [x] Validate tile type enumeration
  - [x] Enforce spawner count limits
  - [x] Verify portal pairing completeness
  - [x] List specific validation errors to Player
  - [x] Confirm successful validation before save

- [x] **Implement map serialization** ([UC-06-Save Map to localStorage](use_cases/1_user_goals/UC-06-Save-Map-to-LocalStorage.md))
  - [x] Serialize to canonical JSON schema with required fields:
    - id (unique)
    - name (string)
    - gridWidth (number)
    - gridHeight (number)
    - tiles[] (array of tile data)
    - spawners[] (array of spawner data)
    - layoutSeed (number)
    - difficulty (string/number)
  - [x] Assign unique map ID if none exists
  - [x] Handle ID conflicts with timestamp or counter increment

- [x] **Implement localStorage persistence** ([UC-06-Save Map to localStorage](use_cases/1_user_goals/UC-06-Save-Map-to-LocalStorage.md))
  - [x] Store maps array using `localStorage.setItem('roguebreaker_maps', ...)`
  - [x] Handle quota exceeded errors
  - [x] Offer deletion of oldest maps when full
  - [x] Detect unavailable localStorage (private browsing)
  - [x] Confirm successful save with map ID and name

- [x] **Implement map loading** ([UC-07-Load Saved Map](use_cases/1_user_goals/UC-07-Load-Saved-Map.md))
  - [x] Retrieve maps array from localStorage
  - [x] Present available maps in selection list (dropdown or grid preview)
  - [x] Validate selected map JSON for schema compliance
  - [x] Convert map data to Three.js scene objects (InstancedMesh for bricks)
  - [x] Initialize game state with loaded level

- [x] **Implement error handling for corrupted maps** ([UC-07-Load Saved Map](use_cases/1_user_goals/UC-07-Load-Saved-Map.md))
  - [x] Detect corrupted or schema-incompatible JSON
  - [x] Report missing required fields
  - [x] Handle oversized maps (offer clipping)
  - [x] Replace unsupported tile types with Normal tiles
  - [x] Skip invalid spawners with warning

## HUD & User Feedback

- [x] **Implement Heads-Up Display** ([UC-01-Start New Game](use_cases/1_user_goals/UC-01-Start-New-Game.md), [UC-02-Play Level](use_cases/1_user_goals/UC-02-Play-Level.md))
  - [x] Display score counter
  - [x] Display lives counter
  - [x] Display current level number
  - [x] Display combo multiplier
  - [x] Show active modifier icons and stack counts

- [x] **Implement visual feedback** ([UC-SF02-Apply Modifiers to Gameplay](use_cases/2_subfunctions/UC-SF02-Apply-Modifiers-to-Gameplay.md))
  - [x] Update HUD icons for newly active modifiers
  - [x] Show brick crack effects on damage
  - [x] Display AOE blast visual for explosive bricks
  - [x] Show shield charge count visually

## Three.js Integration

- [x] **Set up Three.js scene** ([UC-01-Start New Game](use_cases/1_user_goals/UC-01-Start-New-Game.md))
  - [x] Initialize WebGL context with error handling
  - [x] Create camera, renderer, scene
  - [x] Handle CDN unavailable or WebGL not supported cases

- [x] **Implement InstancedMesh for bricks** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md), [UC-07-Load Saved Map](use_cases/1_user_goals/UC-07-Load-Saved-Map.md))
  - [x] Use InstancedMesh for static brick rendering
  - [x] Create individual meshes for dynamic entities (spawners, portals)
  - [x] Update instance matrices on brick state changes

- [x] **Implement scene management across states** ([UC-SF03-Manage Game State Transitions](use_cases/2_subfunctions/UC-SF03-Manage-Game-State-Transitions.md))
  - [x] Group scene objects by state
  - [x] Show/hide or dispose/recreate groups on transition
  - [x] Clean up orphaned objects during state exit

## Data Tracking & Statistics

- [x] **Implement run history logging** ([UC-S01-Play a Run](use_cases/0_summary/UC-S01-Play-a-Run.md), [UC-SF02-Apply Modifiers to Gameplay](use_cases/2_subfunctions/UC-SF02-Apply-Modifiers-to-Gameplay.md))
  - [x] Log modifier selections with order and timestamps
  - [x] Track combo record (highest multiplier achieved)
  - [x] Record time played per run
  - [x] Store data in memory array for end-of-run display

- [x] **Implement statistics compilation** ([UC-04-Handle Game Over](use_cases/1_user_goals/UC-04-Handle-Game-Over.md))
  - [x] Compile final score
  - [x] Count levels completed
  - [x] List modifiers acquired in order
  - [x] Record highest combo achieved
  - [x] Calculate total play time

## Error Handling & Edge Cases

- [x] **Implement fallback mechanisms** ([UC-S01-Play a Run](use_cases/0_summary/UC-S01-Play-a-Run.md), [UC-01-Start New Game](use_cases/1_user_goals/UC-01-Start-New-Game.md))
  - [x] Provide default level layout when generation fails
  - [x] Fall back to safe default state on entry action failures
  - [x] Handle missing or invalid modifier pool

- [x] **Implement error reporting** ([UC-S02-Manage Saved Maps](use_cases/0_summary/UC-S02-Manage-Saved-Maps.md))
  - [x] Report specific validation errors to Player
  - [x] Communicate localStorage quota issues
  - [x] Display incomplete statistics notices when data is corrupted

## Testing & Validation Items

- [x] **Verify collision accuracy** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [x] Test all brick types with and without modifiers
  - [x] Verify no tunneling occurs at maximum velocities
  - [x] Confirm AOE damage recursion depth limit

- [x] **Verify modifier stacking** ([UC-SF02-Apply Modifiers to Gameplay](use_cases/2_subfunctions/UC-SF02-Apply-Modifiers-to-Gameplay.md))
  - [x] Test stack caps (e.g., bounce_boost max 4)
  - [x] Verify conflict resolution behavior
  - [x] Confirm all modifier effects are reversible

- [x] **Verify state transitions** ([UC-SF03-Manage Game State Transitions](use_cases/2_subfunctions/UC-SF03-Manage-Game-State-Transitions.md))
  - [x] Test all valid transitions between states
  - [x] Verify invalid transitions are rejected
  - [x] Confirm no memory leaks from orphaned objects

- [x] **Verify save/load integrity** ([UC-S02-Manage Saved Maps](use_cases/0_summary/UC-S02-Manage-Saved-Maps.md), [UC-07-Load Saved Map](use_cases/1_user_goals/UC-07-Load-Saved-Map.md))
  - [x] Test saving maps of various sizes
  - [x] Verify corrupted map detection and handling
  - [x] Confirm localStorage quota handling

- [x] **Verify editor-to-game flow** (critical bug fix)
  - [x] PLAY MAP button now properly transitions through state machine
  - [x] Custom grid builds correctly via buildCustomLevel()
  - [x] Custom level (99) triggers VICTORY on completion
  - [x] Default map seeds on first launch via ensureDefaultMapExists()
  - [x] QUICK PLAY button provides instant access to default map

- [x] **Fix null-ball crash on game start** (integration bug)
  - [x] checkPaddleBallCollisions() now guards against empty balls array
  - [x] checkBallPaddleCollision() has defensive null checks for ball.radius
  - [x] EDITOR PLAY MAP now sets useCustomGrid BEFORE transitionTo (timing fix)
  - [x] Ball spawn delay (1.5s) no longer causes game loop to crash

---

## Implementation Notes

- **Priority**: Items marked as "highest priority" in their source use cases should be implemented first
- **Dependencies**: Some items depend on others (e.g., collision system before modifier system that affects collisions)
- **Three.js Version**: Three.js r128 from CDN (loaded via script tag)
- **Performance Target**: Maintain 60fps during gameplay with up to 10 active modifiers
- **Browser Support**: Chrome, Firefox, Safari (latest two versions)

## Open Issues from Specifications — RESOLVED

The following open issues have been resolved in the implementation:

1. ✅ **Levels per run**: 10 levels (`CONFIG.totalLevels = 10`). Victory on clearing all 10.
2. ✅ **Default lives per difficulty**: Easy=5, Normal=3, Hard=1 (`CONFIG.difficultyLives`)
3. ✅ **Combo window**: 800ms (`CONFIG.comboWindowMs`), multiplier = comboCount (x1 base, x2 at 2 consecutive, etc.)
4. ✅ **Brick point values**: normal=10, hard=30, fragile=20, explosive=15, shooter=25, portal=50, bonus=40
5. ⚠️ **Ball speed increase per level**: Not yet implemented (can be added as a future enhancement)
6. ✅ **Max grid size**: 12x8 (`CONFIG.gridCols`, `CONFIG.gridRows`)
7. ✅ **Max spawners per map**: 5 (`CONFIG.maxSpawnersPerMap`)
8. ⚠️ **Conflict matrix**: Minimal (dual_paddle↔broad_sweep overwrite, multiball↔split reject). Expandable via `CONFIG.conflicts` array.
9. ⚠️ **Modifier limit**: No global cap; each modifier has its own `maxStack`. Can add global cap if needed.
10. ✅ **Max stored maps**: 20 (`CONFIG.maxSavedMaps`), oldest removed on overflow.
