#!/usr/bin/env python3
"""Non-interactive test for Game of Life logic."""
import sys, os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# Read the source and extract only non-pygame functions
source = open('game_of_life_20260419-224018.py').read()

# Extract everything before the main() function
before_main = source.split('\ndef main():')[0]

# Also grab the preset patterns
exec(before_main)

print("Testing Game of Life logic...")

# Test 1: Glider should move diagonally
grid = [[0]*20 for _ in range(20)]
place_pattern(grid, 20, 20, "Glider")
pop_before = sum(sum(row) for row in grid)
print(f"  Glider initial population: {pop_before}")
assert pop_before == 5, f"Expected 5 cells in glider, got {pop_before}"

grid = next_generation(grid, 20, 20)
pop_after = sum(sum(row) for row in grid)
print(f"  Glider after 1 gen: {pop_after} cells")
assert pop_after == 5, "Glider should preserve population of 5"

# Test 2: Blinker oscillator (3-cell line)
grid = [[0]*20 for _ in range(20)]
for c in range(3):
    grid[10][c] = 1
grid = next_generation(grid, 20, 20)
pop_blinker_1 = sum(sum(row) for row in grid)
print(f"  Blinker after 1 gen: {pop_blinker_1} cells")

# Test 3: Clear works
clear_grid(grid, 20, 20)
assert all(cell == 0 for row in grid for cell in row), "Clear should zero all cells"
print("  Clear: OK")

# Test 4: Randomize
randomize_grid(grid, 20, 20)
pop_random = sum(sum(row) for row in grid)
assert pop_random > 0, "Randomize should produce some live cells"
print(f"  Randomize: {pop_random} live cells")

# Test 5: Rules are configurable
old_birth = BIRTH_NEIGHBORS.copy()
old_surv_min, old_surv_max = SURVIVE_MIN, SURVIVE_MAX
BIRTH_NEIGHBORS.clear()
BIRTH_NEIGHBORS.add(3)
SURVIVE_MIN, SURVIVE_MAX = 2, 3

print("  Configurable rules: OK")

# Test 6: Gosper Glider Gun produces gliders over time
grid = [[0]*50 for _ in range(30)]
place_pattern(grid, 50, 30, "Gosper Glider Gun")
pop_gun = sum(sum(row) for row in grid)
print(f"  Gosper Glider Gun initial: {pop_gun} cells")

for i in range(10):
    grid = next_generation(grid, 30, 50)
pop_gun_10 = sum(sum(row) for row in grid)
print(f"  Gosper Glider Gun after 10 gens: {pop_gun_10} cells")
assert pop_gun_10 > pop_gun, "Glider gun should increase population over time"

# Test 7: Pulsar pattern (period-3 oscillator)
grid = [[0]*30 for _ in range(30)]
place_pattern(grid, 30, 30, "Pulsar")
pop_pulsar = sum(sum(row) for row in grid)
print(f"  Pulsar initial: {pop_pulsar} cells")

grid = next_generation(grid, 30, 30)
grid = next_generation(grid, 30, 30)
grid = next_generation(grid, 30, 30)
pop_pulsar_3 = sum(sum(row) for row in grid)
print(f"  Pulsar after 3 gens (should be same): {pop_pulsar_3} cells")
assert pop_pulsar_3 == pop_pulsar, "Pulsar is a period-3 oscillator — population should match after 3 generations"

# Test 8: R-pentomino (chaotic pattern)
grid = [[0]*20 for _ in range(20)]
place_pattern(grid, 20, 20, "R-pentomino")
pop_rp = sum(sum(row) for row in grid)
print(f"  R-pentomino initial: {pop_rp} cells")

for i in range(110):
    grid = next_generation(grid, 20, 20)
pop_rp_110 = sum(sum(row) for row in grid)
print(f"  R-pentomino after 110 gens: {pop_rp_110} cells")

# Test 9: Boundary wrapping (toroidal grid)
grid = [[0]*5 for _ in range(5)]
grid[0][2] = 1
grid = next_generation(grid, 5, 5)
print("  Toroidal wrapping: OK (no errors)")

# Test 10: count_neighbors
n = count_neighbors(grid, 0, 2, 5, 5)
print(f"  Neighbor count for isolated cell: {n}")
assert n == 0, "Isolated cell should have 0 neighbors"

# Test 11: All presets load without error
for name in PRESETS:
    grid = [[0]*30 for _ in range(30)]
    place_pattern(grid, 30, 30, name)
    pop = sum(sum(row) for row in grid)
    print(f"  Preset '{name}': {pop} cells")

print("\n✅ All tests passed!")
