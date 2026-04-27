# RogueBreaker - Implementation Checklist

This checklist is derived from the use case specifications and is designed to guide an AI agent through implementing the complete Brick Breaker roguelike game. Each item includes a reference to its source use case via markdown links.

## Core Game Loop & State Management

- [ ] **Implement state machine for game states** ([UC-S03-Manage Game State Transitions](use_cases/2_subfunctions/UC-SF03-Manage-Game-State-Transitions.md))
  - [ ] Define state enum: MENU, PLAYING, LEVEL_COMPLETE, GAME_OVER, VICTORY, EDITOR
  - [ ] Implement transition validation logic
  - [ ] Create exit actions for each state (cleanup timers, dispose objects, clear listeners)
  - [ ] Create entry actions for each state (initialize systems, render UI, start timers)
  - [ ] Implement subsystem notification system for state changes

- [ ] **Implement Main Menu interface** ([UC-S01-Play a Run](use_cases/0_summary/UC-S01-Play-a-Run.md), [UC-01-Start New Game](use_cases/1_user_goals/UC-01-Start-New-Game.md))
  - [ ] Create Main Menu UI with Play, Map Editor, Load Map options
  - [ ] Implement "Play" button handler that initializes game state
  - [ ] Add exit/cancel functionality returning to menu

- [ ] **Implement game initialization** ([UC-01-Start New Game](use_cases/1_user_goals/UC-01-Start-New-Game.md))
  - [ ] Initialize default game state (score=0, lives=default, level=1, modifiers=[])
  - [ ] Set up Three.js scene with default paddle and ball
  - [ ] Load first level layout (procedural or default)
  - [ ] Display HUD with initial values
  - [ ] Handle initialization failures gracefully

- [ ] **Implement game loop at 60fps** ([UC-02-Play Level](use_cases/1_user_goals/UC-02-Play-Level.md))
  - [ ] Use requestAnimationFrame for physics updates
  - [ ] Update ball trajectory and physics each frame
  - [ ] Handle special brick behaviors (explosive, shooter, portal, bonus)
  - [ ] Track combo multiplier on consecutive quick destroys

## Collision System

- [ ] **Implement collision detection subsystem** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [ ] Use THREE.Box3 for AABB bounding boxes on all dynamic entities
  - [ ] Implement ball-wall collision with velocity reflection
  - [ ] Clamp positions to boundaries and cap velocity thresholds
  - [ ] Handle tunneling detection with sweep tests

- [ ] **Implement ball-paddle collision** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [ ] Calculate strike position offset for reflection angle
  - [ ] Apply bounce modifiers (Bounce Boost, Magnet)
  - [ ] Support Dual Paddle modifier with independent collision checks
  - [ ] Map hit position to deflection angle (-1 to +1 range)

- [ ] **Implement ball-brick collision** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [ ] Apply damage based on brick type and active modifiers
  - [ ] Handle multi-HP bricks with visual crack feedback
  - [ ] Implement Explosive brick AOE damage with recursion limit
  - [ ] Handle Portal brick teleportation with paired portals
  - [ ] Award points and resolve combo bonuses

- [ ] **Implement projectile collision** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [ ] Detect projectile-brick collisions
  - [ ] Handle enemy projectile hitting paddle (HP/life loss)
  - [ ] Remove projectiles after impact

## Paddle & Ball Mechanics

- [ ] **Implement paddle controls** ([UC-02-Play Level](use_cases/1_user_goals/UC-02-Play-Level.md))
  - [ ] Support Arrow keys or A/D for horizontal movement
  - [ ] Implement Dual Paddle modifier with separate key pairs
  - [ ] Apply Broad Sweep modifier (40% width increase per stack)
  - [ ] Apply Assist Guide modifier (subtle paddle drift toward ball)

- [ ] **Implement ball physics** ([UC-02-Play Level](use_cases/1-up_goals/UC-02-Play-Level.md))
  - [ ] Reflect velocity vector off walls with proper angle calculation
  - [ ] Apply bounce boost modifier (+15% velocity per stack)
  - [ ] Implement Magnet effect (trajectory curve toward paddle)
  - [ ] Handle ball falling below arena floor (life loss)
  - [ ] Respawn ball when lives remain

- [ ] **Implement Multiball mechanic** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [ ] Spawn clone balls from destroyed special bricks
  - [ ] Assign randomized velocities to cloned balls
  - [ ] Handle multiball collision with appropriate modifiers

## Level System

- [ ] **Implement level progression** ([UC-S01-Play a Run](use_cases/0_summary/UC-S01-Play-a-Run.md), [UC-02-Play Level](use_cases/1_user_goals/UC-02-Play-Level.md))
  - [ ] Track current level number and increment on completion
  - [ ] Detect when all destructible bricks are destroyed
  - [ ] Transition to Level Complete state on victory
  - [ ] Handle level generation failures with fallback defaults
  - [ ] Support both procedural and saved map levels

- [ ] **Implement brick types** ([UC-02-Play Level](use_cases/1_user_goals/UC-02-Play-Level.md))
  - [ ] Normal brick (1 HP)
  - [ ] Hard brick (3 HP)
  - [ ] Fragile brick (breaks easily)
  - [ ] Explosive brick (AOE damage on destruction)
  - [ ] Shooter brick (fires projectiles)
  - [ ] Portal brick (teleports ball to paired portal)
  - [ ] Bonus brick (drops collectible items)

- [ ] **Implement spawner system** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [ ] Configure spawner placement and fire rate
  - [ ] Support different projectile types
  - [ ] Enforce maximum spawner count per map
  - [ ] Validate spawner configuration on load

## Modifier System

- [ ] **Implement modifier selection interface** ([UC-03-Select Modifier at Level Completion](use_cases/1_user_goals/UC-03-Select-Modifier-at-Level-Completion.md))
  - [ ] Pause gameplay and transition to Modifier Selection screen
  - [ ] Select three random modifiers from available pool
  - [ ] Display modifier cards with icon, name, description, stackability
  - [ ] Show conflict warnings for incompatible modifiers
  - [ ] Allow keyboard selection (1, 2, or 3 keys)

- [ ] **Implement modifier application logic** ([UC-SF02-Apply Modifiers to Gameplay](use_cases/2_subfunctions/UC-SF02-Apply-Modifiers-to-Gameplay.md))
  - [ ] Read activeModifiers[] array each frame
  - [ ] Check for conflicts between new and existing modifiers
  - [ ] Resolve conflicts: overwrite, reject, or stack
  - [ ] Apply modifier effects to relevant gameplay systems
  - [ ] Update state flags intercepted by collision/update loops
  - [ ] Log modifier application with timestamp for run history

- [ ] **Implement conflict resolution rules** ([UC-SF02-Apply Modifiers to Gameplay](use_cases/2_subfunctions/UC-SF02-Apply-Modifiers-to-Gameplay.md))
  - [ ] Define overwrite conflicts (e.g., split vs widen)
  - [ ] Define reject conflicts (e.g., multiball vs split)
  - [ ] Define stackable modifiers with caps (e.g., bounce_boost max 4)
  - [ ] Handle conflict warnings to Player before selection

- [ ] **Implement individual modifiers** ([UC-SF02-Apply Modifiers to Gameplay](use_cases/2_subfunctions/UC-SF02-Apply-Modifiers-to-Gameplay.md))
  - [ ] Dual Paddle (split) - creates second paddle with independent controls
  - [ ] Broad Sweep (widen) - increases paddle width by 40% per stack
  - [ ] Upward Fire (projectile) - auto-fire timer and manual fire on Space
  - [ ] Ball Pull (magnet) - proximity-based trajectory curve
  - [ ] Elasticity (bounce_boost) - +15% velocity multiplier per stack
  - [ ] Barrier Wall (shield) - temporary wall with charge count
  - [ ] Clone Strike (multiball) - spawns clone balls on special brick destroy
  - [ ] Slow/Speed Toggle (timeshift) - toggle time scale 0.5x-1.5x
  - [ ] Chromatic Damage (color_sync) - +200% damage when colors match
  - [ ] Assist Guide (autoaim) - subtle paddle drift toward ball trajectory

## Game Over & Victory Systems

- [ ] **Implement life and death tracking** ([UC-02-Play Level](use_cases/1_user_goals/UC-02-Play-Level.md), [UC-04-Handle Game Over](use_cases/1_user_goals/UC-04-Handle-Game-Over.md))
  - [ ] Decrement lives when ball is lost
  - [ ] Detect when lives reach zero
  - [ ] Respawn ball when lives remain
  - [ ] Handle difficulty-based default lives (Easy=5, Normal=3, Hard=1)

- [ ] **Implement Game Over screen** ([UC-04-Handle Game Over](use_cases/1_user_goals/UC-04-Handle-Game-Over.md))
  - [ ] Detect lives reaching zero and halt gameplay
  - [ ] Compile run statistics (score, levels, modifiers, combo record)
  - [ ] Display Game Over screen with statistics overlay
  - [ ] Provide action options: Retry Run, Return to Main Menu, View Replay
  - [ ] Handle edge case of immediate death (score=0, no modifiers)

- [ ] **Implement retry mechanics** ([UC-04-Handle Game Over](use_cases/1_user_goals/UC-04-Handle-Game-Over.md))
  - [ ] Reset game state (score=0, lives=default, level=1)
  - [ ] Decide whether to preserve or reset active modifiers on retry
  - [ ] Transition back to Playing state with first level

- [ ] **Implement Victory condition** ([UC-S01-Play a Run](use_cases/0_summary/UC-S01-Play-a-Run.md))
  - [ ] Detect completion of all planned levels
  - [ ] Display Victory screen with run statistics
  - [ ] Show celebration effects and final summary

## Map Editor & Save System

- [ ] **Implement Map Editor interface** ([UC-05-Edit Map in Editor](use_cases/1_user_goals/UC-05-Edit-Map-in-Editor.md))
  - [ ] Create grid canvas (DOM-based, e.g., 12x8) with clickable cells
  - [ ] Implement tool palette: Brush, Fill, Eraser, Pattern Generator
  - [ ] Display tile types with distinct visual representation
  - [ ] Support editing existing saved maps

- [ ] **Implement map editing tools** ([UC-05-Edit Map in Editor](use_cases/1_user_goals/UC-05-Edit-Map-in-Editor.md))
  - [ ] Brush tool for placing individual tiles
  - [ ] Fill tool for contiguous region filling
  - [ ] Pattern Generator with options: Pyramid, Checkerboard, Spiral, Random, Custom
  - [ ] Validate placements against grid bounds

- [ ] **Implement spawner configuration in editor** ([UC-05-Edit Map in Editor](use_cases/1_user_goals/UC-05-Edit-Map-in-Editor.md))
  - [ ] Configure spawner placement and fire rate
  - [ ] Select projectile type for spawners
  - [ ] Enforce maximum spawner count limit

- [ ] **Implement map metadata** ([UC-05-Edit Map in Editor](use_cases/1_user_goals/UC-05-Edit-Map-in-Editor.md))
  - [ ] Set map name
  - [ ] Set difficulty level
  - [ ] Set layout seed for procedural generation

- [ ] **Implement validation system** ([UC-05-Edit Map in Editor](use_cases/1_user_goals/UC-05-Edit-Map-in-Editor.md), [UC-06-Save Map to localStorage](use_cases/1_user_goals/UC-06-Save-Map-to-LocalStorage.md))
  - [ ] Check grid bounds compliance
  - [ ] Validate tile type enumeration
  - [ ] Enforce spawner count limits
  - [ ] Verify portal pairing completeness
  - [ ] List specific validation errors to Player
  - [ ] Confirm successful validation before save

- [ ] **Implement map serialization** ([UC-06-Save Map to localStorage](use_cases/1_user_goals/UC-06-Save-Map-to-LocalStorage.md))
  - [ ] Serialize to canonical JSON schema with required fields:
    - id (unique)
    - name (string)
    - gridWidth (number)
    - gridHeight (number)
    - tiles[] (array of tile data)
    - spawners[] (array of spawner data)
    - layoutSeed (number)
    - difficulty (string/number)
  - [ ] Assign unique map ID if none exists
  - [ ] Handle ID conflicts with timestamp or counter increment

- [ ] **Implement localStorage persistence** ([UC-06-Save Map to localStorage](use_cases/1_user_goals/UC-06-Save-Map-to-LocalStorage.md))
  - [ ] Store maps array using `localStorage.setItem('roguebreaker_maps', ...)`
  - [ ] Handle quota exceeded errors
  - [ ] Offer deletion of oldest maps when full
  - [ ] Detect unavailable localStorage (private browsing)
  - [ ] Confirm successful save with map ID and name

- [ ] **Implement map loading** ([UC-07-Load Saved Map](use_cases/1_user_goals/UC-07-Load-Saved-Map.md))
  - [ ] Retrieve maps array from localStorage
  - [ ] Present available maps in selection list (dropdown or grid preview)
  - [ ] Validate selected map JSON for schema compliance
  - [ ] Convert map data to Three.js scene objects (InstancedMesh for bricks)
  - [ ] Initialize game state with loaded level

- [ ] **Implement error handling for corrupted maps** ([UC-07-Load Saved Map](use_cases/1_user_goals/UC-07-Load-Saved-Map.md))
  - [ ] Detect corrupted or schema-incompatible JSON
  - [ ] Report missing required fields
  - [ ] Handle oversized maps (offer clipping)
  - [ ] Replace unsupported tile types with Normal tiles
  - [ ] Skip invalid spawners with warning

## HUD & User Feedback

- [ ] **Implement Heads-Up Display** ([UC-01-Start New Game](use_cases/1_user_goals/UC-01-Start-New-Game.md), [UC-02-Play Level](use_cases/1_user_goals/UC-02-Play-Level.md))
  - [ ] Display score counter
  - [ ] Display lives counter
  - [ ] Display current level number
  - [ ] Display combo multiplier
  - [ ] Show active modifier icons and stack counts

- [ ] **Implement visual feedback** ([UC-SF02-Apply Modifiers to Gameplay](use_cases/2_subfunctions/UC-SF02-Apply-Modifiers-to-Gameplay.md))
  - [ ] Update HUD icons for newly active modifiers
  - [ ] Show brick crack effects on damage
  - [ ] Display AOE blast visual for explosive bricks
  - [ ] Show shield charge count visually

## Three.js Integration

- [ ] **Set up Three.js scene** ([UC-01-Start New Game](use_cases/1_user_goals/UC-01-Start-New-Game.md))
  - [ ] Initialize WebGL context with error handling
  - [ ] Create camera, renderer, scene
  - [ ] Handle CDN unavailable or WebGL not supported cases

- [ ] **Implement InstancedMesh for bricks** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md), [UC-07-Load Saved Map](use_cases/1_user_goals/UC-07-Load-Saved-Map.md))
  - [ ] Use InstancedMesh for static brick rendering
  - [ ] Create individual meshes for dynamic entities (spawners, portals)
  - [ ] Update instance matrices on brick state changes

- [ ] **Implement scene management across states** ([UC-SF03-Manage Game State Transitions](use_cases/2_subfunctions/UC-SF03-Manage-Game-State-Transitions.md))
  - [ ] Group scene objects by state
  - [ ] Show/hide or dispose/recreate groups on transition
  - [ ] Clean up orphaned objects during state exit

## Data Tracking & Statistics

- [ ] **Implement run history logging** ([UC-S01-Play a Run](use_cases/0_summary/UC-S01-Play-a-Run.md), [UC-SF02-Apply Modifiers to Gameplay](use_cases/2_subfunctions/UC-SF02-Apply-Modifiers-to-Gameplay.md))
  - [ ] Log modifier selections with order and timestamps
  - [ ] Track combo record (highest multiplier achieved)
  - [ ] Record time played per run
  - [ ] Store data in memory array for end-of-run display

- [ ] **Implement statistics compilation** ([UC-04-Handle Game Over](use_cases/1_user_goals/UC-04-Handle-Game-Over.md))
  - [ ] Compile final score
  - [ ] Count levels completed
  - [ ] List modifiers acquired in order
  - [ ] Record highest combo achieved
  - [ ] Calculate total play time

## Error Handling & Edge Cases

- [ ] **Implement fallback mechanisms** ([UC-S01-Play a Run](use_cases/0_summary/UC-S01-Play-a-Run.md), [UC-01-Start New Game](use_cases/1_user_goals/UC-01-Start-New-Game.md))
  - [ ] Provide default level layout when generation fails
  - [ ] Fall back to safe default state on entry action failures
  - [ ] Handle missing or invalid modifier pool

- [ ] **Implement error reporting** ([UC-S02-Manage Saved Maps](use_cases/0_summary/UC-S02-Manage-Saved-Maps.md))
  - [ ] Report specific validation errors to Player
  - [ ] Communicate localStorage quota issues
  - [ ] Display incomplete statistics notices when data is corrupted

## Testing & Validation Items

- [ ] **Verify collision accuracy** ([UC-SF01-Resolve Collisions](use_cases/2_subfunctions/UC-SF01-Resolve-Collisions.md))
  - [ ] Test all brick types with and without modifiers
  - [ ] Verify no tunneling occurs at maximum velocities
  - [ ] Confirm AOE damage recursion depth limit

- [ ] **Verify modifier stacking** ([UC-SF02-Apply Modifiers to Gameplay](use_cases/2_subfunctions/UC-SF02-Apply-Modifiers-to-Gameplay.md))
  - [ ] Test stack caps (e.g., bounce_boost max 4)
  - [ ] Verify conflict resolution behavior
  - [ ] Confirm all modifier effects are reversible

- [ ] **Verify state transitions** ([UC-SF03-Manage Game State Transitions](use_cases/2_subfunctions/UC-SF03-Manage-Game-State-Transitions.md))
  - [ ] Test all valid transitions between states
  - [ ] Verify invalid transitions are rejected
  - [ ] Confirm no memory leaks from orphaned objects

- [ ] **Verify save/load integrity** ([UC-S02-Manage Saved Maps](use_cases/0_summary/UC-S02-Manage-Saved-Maps.md), [UC-07-Load Saved Map](use_cases/1_user_goals/UC-07-Load-Saved-Map.md))
  - [ ] Test saving maps of various sizes
  - [ ] Verify corrupted map detection and handling
  - [ ] Confirm localStorage quota handling

---

## Implementation Notes

- **Priority**: Items marked as "highest priority" in their source use cases should be implemented first
- **Dependencies**: Some items depend on others (e.g., collision system before modifier system that affects collisions)
- **Three.js Version**: Use Three.js r150+ for InstancedMesh performance
- **Performance Target**: Maintain 60fps during gameplay with up to 10 active modifiers
- **Browser Support**: Chrome, Firefox, Safari (latest two versions)

## Open Issues from Specifications

These items require additional specification before implementation:

1. How many levels constitute a full run? What is the exact victory condition?
2. Default lives values per difficulty level
3. Combo time window duration and point multipliers
4. Brick point values per type
5. Ball speed increase curve per level (if any)
6. Maximum grid size for custom maps
7. Maximum spawners per map
8. Complete conflict matrix between all modifiers
9. Should there be a modifier limit (max active count)?
10. Maximum number of stored maps in localStorage
