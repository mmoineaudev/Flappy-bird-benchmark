# Cosmic Flap - Three Iterations

## Overview
Three progressively enhanced versions of a Flappy Bird-style game, each building on the last with new features, mechanics, and visual polish.

---

## Version 1: `Qwen3.5-27B-Q4_K_S_50k2.1-first-output.html`
**Theme:** Classic Flappy Bird with clean aesthetics

### Features
- Basic bird physics (gravity, jump, rotation)
- Pipe obstacles with random heights
- Score tracking with local storage best score
- Animated clouds background
- Ground scroll effect
- Collision detection
- Start and game-over screens

### Visual Style
- Sky blue gradient background
- Simple cartoon bird with eye, wing, and beak
- Green pipes with caps
- Clean UI with blue/white color scheme

---

## Version 2: `Qwen3.5-27B-Q4_K_S_50k2.2-variation.html`
**Theme:** Neon Flap - Cyberpunk Edition

### New Features Over V1
- **Particle System:** Jump trails, score bursts, collision effects
- **Combo System:** Consecutive scores build multiplier (up to 5x bonus)
- **Power-ups:** Three types - Shield, Slow Motion, 2x Score
- **Dynamic Difficulty:** Pipe speed increases with score
- **Sound Effects:** Web Audio API - jump, score, powerup, crash sounds
- **Neon Visuals:** Glowing effects, cyan/magenta color palette
- **Bird Trail:** Visual trail following the bird
- **Diamond Power-ups:** Collectible items between pipes

### Visual Style
- Dark background with neon cyan/magenta accents
- Glowing pipes and bird with shadow effects
- Cyberpunk grid floor
- Pulsing animations on UI elements

---

## Version 3: `Qwen3.5-27B-Q4_K_S_50k2.3-variation.html`
**Theme:** Cosmic Flap - Space Adventure

### New Features Over V2
- **Unlockable Skins:** 5 ship skins (Classic, Golden, Crystal, Plasma, Void)
- **Boss Pipes:** Every 10 points - slower, worth 5x points, hazard stripes
- **Day/Night Cycle:** Dynamic background gradient that cycles through sunset/night
- **Starfield Background:** 100 twinkling stars
- **Turbo Mode:** Hold space to fall faster (with flame effect)
- **Screen Shake:** Impact feedback on collision
- **Floating Score Text:** Animated +1, +2 popups
- **Multiplier Display:** Visual score multiplier tracking
- **Menu System:** Skin selection screen with unlock requirements

### Visual Style
- Space theme with gradient skyboxes
- Starfield with parallax twinkling
- Rocket ship bird with engine flame
- Boss pipes with animated red/black hazard stripes
- More varied particle effects (sparkles, explosions)

---

## Key Differences Summary

| Feature | V1 | V2 | V3 |
|---------|----|----|----|
| Theme | Classic | Cyberpunk | Space |
| Particles | No | Yes | Advanced |
| Sound | No | Yes | Yes |
| Power-ups | No | Yes (3 types) | Yes (3 types) |
| Combo System | No | Yes | Yes |
| Difficulty Scaling | No | Yes | Yes |
| Boss Pipes | No | No | Yes |
| Skins | No | No | 5 unlockable |
| Day/Night Cycle | No | No | Yes |
| Turbo Mode | No | No | Yes |
| Screen Shake | No | No | Yes |
| Starfield | No | No | Yes |

---

## How to Play
1. Open any HTML file in a browser
2. Press SPACE or click to jump
3. Avoid pipes by timing your jumps
4. Collect power-ups for bonuses
5. In V3: Hold SPACE for turbo fall, unlock skins by scoring high

---

## Files Created
- `Qwen3.5-27B-Q4_K_S_50k2.1-first-output.html` - Base version
- `Qwen3.5-27B-Q4_K_S_50k2.2-variation.html` - Cyberpunk variation
- `Qwen3.5-27B-Q4_K_S_50k2.3-variation.html` - Space adventure variation
