# Task

Create a 3D Conway's Game of Life simulation with the following ordered implementation checklist:

it's the same as the classic 2D version, but this time it spreads in a 3D space with cubic cells.

## Detailed specifications

**Objective**: Develop a high-performance, 3D Volumetric Cellular Automata simulation (a 3D version of Conway's Game of Life) using Three.js.

**1. Simulation Logic (The Engine)**:
- **Grid Structure**: Implement a 3D voxel grid (X, Y, Z).
- **Neighborhood Logic**: Use the Moore neighborhood extended to 3D (counting the 26 surrounding neighbors).
- **Rule System**: Implement a dynamic rule engine where the user can define "Birth" and "Survival" thresholds (e.g., B5/S4,5 or the standard B3/S23 adapted for 3D).
- **State Management**: Use a double-buffering approach (two arrays/grids) to calculate the next generation without mutating the current state mid-calculation.
- **Performance**: Because the voxel count can grow quickly, use `THREE.InstancedMesh` to render all active cells in a single draw call.

**2. Visual Aesthetic (Retro-Neon/Synthwave)**:
- **Style**: A "Cyberpunk/Tron" aesthetic. Dark background (deep navy or black).
- **Cell Material**: Use `MeshStandardMaterial` with high `emissive` intensity and bright neon colors (Cyan, Magenta, Electric Blue).
- **Post-Processing**: Implement a heavy **Bloom Pass** (`UnrealBloomPass`) to create a glowing, light-bleeding effect around the active cells.
- **Environment**: A subtle, faint glowing wireframe grid should exist in the background to provide spatial orientation.

**3. User Interface & Controls (The Dashboard)**:
- **Initial State**: The simulation must start in a `PAUSED` state with a randomized seed of living cells.
- **Camera**: Implement `OrbitControls` allowing for full 360-degree rotation, panning, and zooming.
- **Control Panel (GUI)**: Use `lil-gui` or `Tweakpane` to provide real-time sliders for:
    * **Simulation Speed**: Step delay in milliseconds.
    * **Grid Dimensions**: X, Y, and Z bounds.
    * **Ruleset**: Numerical inputs for "Birth" neighbors and "Survival" neighbors.
    * **Cell Color/Glow**: Intensity of the bloom and color shifting based on cell age.
    * **Playback**: Play, Pause, Step-Forward, and Reset buttons.
- **Interaction**: Enable the ability to "paint" cells into the 3D space via mouse click/drag (Raycasting to find the voxel position).

**4. Technical Requirements**:
- **Language**: Modern ES6+ JavaScript.
- **Modular Architecture**: Separate the `AutomataEngine` (logic), the `Visualizer` (Three.js rendering), and the `UIManager` (controls).
- **Optimization**: Ensure the simulation uses `requestAnimationFrame` and handles window resizing gracefully. Include a FPS counter in the corner.

# Details

* The file produced should be name with the model name, you can find it in OpenRouter parameters : ```gemma-4-26B-A4B-it-UD-Q6_K_100k_[horodated_timestamp].html```
* commit and push at the end of implementation
* After each commit, read the result for finding bugs or mistakes. If some are found, fix them and commit again.
