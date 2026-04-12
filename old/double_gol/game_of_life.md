# Game of Life Benchmark Prompt

## Overview
Create an interactive Conway's Game of Life simulation with two implementations: a Python version using Pygame and a web version using Three.js. The aesthetic should feature retro styling with neon wave visuals (dark background, glowing cyan/magenta/purple elements, scanlines, CRT effects).

---

## Phase 1: Python/Pygame Implementation

### File Creation
Create the file at: `Flappy-bird-benchmark/game_of_life_YYYYMMDDHHMMSS.py`

### Requirements

#### Core Game Rules (Parametrizable)
- Implement Conway's Game of Life with user-configurable rules:
  - Grid dimensions (default: 80x40 cells)
  - Birth rule: number of live neighbors required to spawn a new cell
  - Survival rule: minimum and maximum live neighbors for a cell to survive
  - Cell size in pixels (default: 15px)
  - Initial pattern or random generation option
  - Animation speed (frames per second)

#### Game Features
- **Rendering**: 
  - Dark background (#0a0a0f or similar)
  - Neon-colored cells with glow effect (cyan #00ffff, magenta #ff00ff, or purple #9d4edd)
  - Subtle grid lines visible but not distracting
  - Optional scanline/CRT overlay effect for retro feel

- **Controls**:
  - `Spacebar`: Pause/Resume game
  - `R`: Randomize grid
  - `C`: Clear grid
  - `+` / `-`: Adjust animation speed
  - Mouse click: Toggle cell state at cursor position

- **UI Elements** (rendered on-screen):
  - Current frame counter
  - Population count (live cells)
  - Rule parameters display
  - Control hints in corner

#### Code Quality
- Use `pygame` for rendering and input handling
- Implement clean, modular code structure
- Include inline comments explaining rule configuration
- Add error handling for edge cases

### Verification
After creating the file, run it to verify:
```bash
python3 game_of_life_YYYYMMDDHHMMSS.py
```
The application should launch without errors and respond to keyboard input.

---

## Phase 2: Three.js HTML Implementation

### File Creation
Create the file at: `Flappy-bird-benchmark/game_of_life_YYYYMMDDHHMMSS.html`

### Requirements

#### Technical Setup
- Single self-contained HTML file (all CSS and JavaScript inline)
- Use Three.js via CDN (import map or direct script tag)
- Responsive canvas that fits browser window

#### Visual Enhancements (Improved Cosmetics)
- **3D Perspective**: Render the grid in 3D space with slight perspective angle
- **Neon Glow Effects**: 
  - Cells should emit light using `THREE.PointLight` or emissive materials
  - Dynamic color cycling between cyan, magenta, and purple
  - Bloom/glow post-processing if possible (via EffectComposer)

- **Retro Aesthetic Details**:
  - Dark gradient background
  - Animated grid lines with fading effect
  - Optional particle effects when cells are born/die
  - Subtle screen distortion or chromatic aberration for retro feel
  - Scanline overlay using CSS or canvas

#### Interactive Features
- **Controls** (keyboard + UI):
  - `Spacebar`: Pause/Resume
  - `R`: Randomize
  - `C`: Clear
  - Mouse drag: Draw cells on grid
  - Scroll wheel: Zoom in/out (camera control)

- **On-screen GUI**:
  - Control panel with sliders for:
    - Grid size
    - Birth/survival rules
    - Simulation speed
  - Real-time statistics display
  - Toggle buttons for visual effects (glow, scanlines, particles)

#### Performance Considerations
- Efficient rendering using instanced meshes or geometry merging
- Optimize for smooth animation at 60fps
- Handle grid resizing without performance degradation

### Verification
After creating the file, open it in Chromium browser:
```bash
chromium-browser Flappy-bird-benchmark/game_of_life_YYYYMMDDHHMMSS.html
```
The simulation should render smoothly with interactive controls working properly.

---

## Phase 3: Git Commit and Push

### Final Steps
1. Stage both created files:
   ```bash
   git add game_of_life_*.py game_of_life_*.html
   ```

2. Commit with the message (replace [MODEL_NAME] with your model name):
   ```bash
   git commit -m "made by [MODEL_NAME]"
   ```

3. Push to remote repository:
   ```bash
   git push origin main
   ```
   *(or appropriate branch name)*

---

## Success Criteria

- ✅ Python version runs without errors and all controls work
- ✅ HTML version opens in browser with smooth 60fps rendering
- ✅ Both versions feature neon wave/retro aesthetics
- ✅ Game rules are fully parametrizable in both implementations
- ✅ Spacebar pauses/resumes game in both versions
- ✅ Code is clean, well-documented, and follows best practices
- ✅ Final commit is pushed with correct message format

---

## Notes for the Agent
- Choose visually appealing default rule sets that produce interesting patterns
- Consider including classic Game of Life patterns (gliders, pulsars) as preset options
- Ensure the retro aesthetic is cohesive across both implementations
- Test thoroughly before committing