# Game of Life Benchmark Prompt

## Overview
Create an interactive Conway's Game of Life simulation.

The aesthetic should feature retro styling with neon wave visuals (dark background, glowing cyan/magenta/purple elements, scanlines, CRT effects).

---

## Python/Pygame Implementation

### File Creation
Create the file at: `Flappy-bird-benchmark/game_of_life_[YYYYMMDD-HHMMSS].py`

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
  - There are clickabe buttons that clear then display classic Game of Life patterns (gliders, pulsars) as preset options

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

- Test thoroughly before committing


### Final Steps


1. Stage the created file:
   ```bash
   git add game_of_life_*.py
   ```

2. Commit with the message (replace [MODEL_NAME] with your model name):
   ```bash
   git commit -m "made by [MODEL_NAME]"
   ```

3. Push to remote repository:
   ```bash
   git push origin master
   ```

---

## Success Criteria

- ✅ Python version runs without errors and all controls work
- ✅ Game rules are fully parametrizable
- ✅ Spacebar pauses/resumes game in both versions
- ✅ Code is clean, well-documented, and follows best practices
- ✅ Final commit is pushed with correct message format

---
