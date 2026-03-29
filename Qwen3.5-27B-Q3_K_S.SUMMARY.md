# Flappy Bird Game - Version Comparison

## Overview
Two versions of a flappy bird-like game created in single HTML files with embedded JavaScript.

---

## Version 1: Classic Flappy Bird (`.1-first-output.html`)

### Visual Style
- Traditional sky-blue gradient background
- Simple cloud decorations
- Green pipes with brown caps
- Yellow bird with orange wing and red beak
- Brown ground with grass top

### Gameplay
- Standard gravity and flap mechanics
- Fixed pipe spawn spacing (300px)
- Fixed pipe speed (3px/frame)
- Simple collision detection
- Score increments by 1 per pipe

### Features
- High score saved to localStorage
- Bird rotation based on velocity
- Clean, minimal UI

---

## Version 2: Neon Flap Cyberpunk Edition (`.2-variation.html`)

### Visual Style
- Dark cyberpunk aesthetic with neon glow effects
- Cyan (#00ffff), magenta (#ff00ff), yellow (#ffff00) color scheme
- Moving grid background with perspective lines
- Pulsing neon animations on UI elements
- Screen shake on collisions

### Gameplay Enhancements

#### Combo System
- Score multiplier increases with consecutive pipes (2x at 3, 3x at 6, 5x at 10)
- Combo resets after 10 pipes or 60 frames of inactivity
- Visual combo display with multiplier indicator

#### Power-ups (10% spawn chance)
- **Slow Motion (⚡)**: Reduces game speed for 200 frames
- **Shield (🛡️)**: One-time collision protection for 300 frames
- **Score Boost (✨)**: Doubles points earned for 300 frames

#### Dynamic Difficulty
- Pipe speed increases with score (difficultyMultiplier = 1 + score * 0.02)
- Pipe spawn frequency increases with difficulty
- Creates progressive challenge curve

#### Particle Effects
- Trail particles on flap
- Explosion particles on shield break/collision
- Celebration particles on score/powerup collection
- Shield aura particles

### Technical Improvements
- Canvas shadowBlur for glow effects
- Dynamic scaling and rotation transforms
- CSS animations for UI pulse effects
- Hue rotation filter for slow motion mode

---

## Key Differences Summary

| Aspect | Version 1 | Version 2 |
|--------|-----------|-----------|
| Theme | Classic/Sky | Cyberpunk/Neon |
| Colors | Natural | Neon glow |
| Difficulty | Static | Progressive |
| Scoring | Fixed +1 | Multiplier-based |
| Power-ups | None | 3 types |
| Particles | None | Full particle system |
| Screen shake | No | Yes |
| Combo system | No | Yes |
| Visual effects | Minimal | Extensive |

---

## Files Produced
- `Qwen3.5-27B-Q3_K_S.1-first-output.html` - Classic version (12.5KB)
- `Qwen3.5-27B-Q3_K_S.2-variation.html` - Cyberpunk version (26.3KB)
- `Qwen3.5-27B-Q3_K_S.SUMMARY.md` - This document

Both files are self-contained HTML files requiring no external dependencies. Open in any modern browser to play.
