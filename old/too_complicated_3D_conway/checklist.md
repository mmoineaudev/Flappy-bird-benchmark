# Goal: Develop a 3D Volumetric Cellular Automata simulation using Three.js

## Architectural and Technical Guidelines
- **Language**: Modern ES6+ JavaScript.
- **Rendering**: Three.js with `THREE.InstancedMesh` for performance.
- **Aesthetic**: Retro-Neon/Synthwave (Cyberpunk/Tron style).
- **Architecture**: Modular (AutomataEngine, Visualizer, UIManager).
- **State Management**: Double-buffering approach.
- **Performance Optimization**: Use `requestAnimationFrame`, handle window resizing, and include an FPS counter.

## Scope Definition
A high-performance 3D Game of Life simulation with dynamic rules, visual effects (Bloom), and a user dashboard for real-time control.

## Cross-reference Matrix
- Simulation Logic (Grid, Neighborhood, Rules, State) -> Use Case 1: Simulation Engine
- Visual Aesthetic (Material, Bloom, Environment) -> Use Case 2: Visual Rendering & Aesthetic
- User Interface (Controls, Camera, Interaction) -> Use Case 3: Dashboard & Interaction
- Technical Requirements (Modular, Optimization) -> Covered across all use cases.

---

# Use Case: 1 Implement the Simulation Engine

* [ ] implementation: Define 3D voxel grid structure (X, Y, Z)
* [ ] implementation: Implement Moore neighborhood logic for 3D (26 neighbors)
* [ ] implementation: Create dynamic rule engine for Birth/Survival thresholds
* [ ] implementation: Implement double-buffering state management
* [ ] test: Verify cell state transitions against known 3D patterns

## CHARACTERISTIC INFORMATION

* Goal in Context: Core logic of the 3D Game of Life.
* Scope: Mathematical and logical processing of cell states.
* Level: Backend/Logic engine.
* Preconditions: None.
* Success End Condition: Correct state updates for any given configuration and rule set.
* Failed End Condition: Incorrect neighbor counts or state mutation during calculation.
* Primary Actor: AutomataEngine.
* Trigger: Simulation step update (tick).

### MAIN SUCCESS SCENARIO

<step 1> Initialize 3D grid with specified dimensions.
<step 2> Calculate neighbor counts for every cell using the 3D Moore neighborhood.
<step 3> Apply Birth/Survival rules to determine the next state.
<step 4> Swap buffers to finalize the new generation.

### EXTENSIONS

<step 2> Neighbor count exceeds bounds : Handle edge cases (toroidal or fixed boundaries).

---

# Use Case: 2 Implement Visual Rendering & Aesthetic

* [ ] implementation: Set up Three.js scene with dark background.
* [ ] implementation: Implement `THREE.InstancedMesh` for cell rendering.
* [ ] implementation: Apply `MeshStandardMaterial` with neon emissive colors.
* [ ] implementation: Add `UnrealBloomPass` for glowing effect.
* [ ] implementation: Add faint glowing wireframe grid background.
* [ ] test: Verify rendering performance with high voxel counts.

## CHARACTERISTIC INFORMATION

* Goal in Context: Visualizing the simulation states.
* Scope: Three.js rendering pipeline and post-processing.
* Level: Frontend/Visualizer.
* Preconditions: Simulation engine is running.
* Success End Condition: Visually appealing, glowing 3D simulation.
* Failed End Condition: Low FPS or lack of visual clarity/aesthetic.
* Primary Actor: Visualizer.
* Trigger: Each frame of the animation loop.

### MAIN SUCCESS SCENARIO

<step 1> Clear current frame (or update instance matrices).
<step 2> Update `InstancedMesh` matrices based on living cells from the engine.
<step 3> Apply post-processing (Bloom).
<step 4> Render scene to canvas.

---

# Use Case: 3 Implement Dashboard & Interaction

* [ ] implementation: Set up `OrbitControls` for camera movement.
* [ ] implementation: Integrate `lil-gui` or `Tweakpane` for real-time sliders (Speed, Grid, Rules, Color, Playback).
* [ ] implementation: Implement Raycasting for "painting" cells via mouse.
* [ ] implementation: Add FPS counter overlay.
* [ ] test: Verify all GUI controls correctly update engine/visualizer parameters.

## CHARACTERISTIC INFORMATION

* Goal in Context: Allowing user control and interaction.
* Scope: UI elements and user input handling.
* Level: Frontend/UIManager.
* Preconditions: Visualizer and Engine are active.
* Success End Condition: User can seamlessly manipulate simulation parameters and camera.
* Failed End Condition: Controls do not reflect changes or interaction is broken.
* Primary Actor: User / UIManager.
* Trigger: User input (mouse, keyboard, GUI change).

### MAIN SUCCESS SCENARIO

<step 1> User adjusts a slider in the GUI.
<step 2> UIManager updates the corresponding parameter in the Engine or Visualizer.
<step 3> User clicks on the grid to paint a cell.
<step 4> Raycaster identifies the voxel and updates its state in the engine.

