# Task

Create a 3D Conway's Game of Life simulation with the following ordered implementation checklist:

**IMPLEMENTATION CHECKLIST:**

1. **Setup & Foundation**
   - Initialize Three.js scene with WebGL renderer
   - Set up camera with orbit controls
   - Create responsive window resize handling
   - Implement basic lighting system
   - Add retro UI framework with neon styling

2. **Core Simulation Engine**
   - Design 3D grid data structure (3D array or sparse representation)
   - Implement Conway's Game of Life rules engine
   - Create cell class with state management
   - Build grid update algorithm with proper boundary handling
   - Add initial pattern generation (random or predefined)

3. **3D Visualization**
   - Create 3D cell geometry (cubes/voxels)
   - Implement neon glow shader/materials
   - Add retro CRT scanline overlay effect
   - Create particle trail systems for active cells
   - Implement color cycling and pulsing effects

4. **User Controls & Interface**
   - Add camera controls (orbit, pan, zoom)
   - Implement play/pause/step functionality
   - Create dynamic configuration panel
   - Add rule configuration sliders/inputs
   - Build grid dimension controls
   - Add speed control slider

5. **Advanced Features**
   - Implement performance optimization (instanced rendering)
   - Add pattern presets and import/export functionality
   - Create real-time statistics display
   - Add sound effects for cell state changes
   - Implement evolution history visualization

6. **Testing & Optimization**
   - Verify rule engine correctness
   - Optimize performance for large grids
   - Verify camera controls and user interaction

**SUCCESS CRITERIA:**
- Simulation starts paused with visible 3D grid
- All camera controls work properly (rotate, zoom, pan)
- Grid updates correctly according to Conway's rules
- Neon glow visual effects render properly
- Dynamic configuration panel allows real-time rule adjustment
- Grid dimensions can be changed without crashing
- Simulation speed can be adjusted smoothly
- Performance remains acceptable for large grids (60+ FPS)
- UI is responsive and visually appealing with retro styling
- All controls are functional and intuitive

**FAILURE CRITERIA:**
- Grid crashes or freezes with large dimensions (>32x32x8)
- Camera controls become unresponsive or buggy
- Simulation doesn't update cells correctly according to rules
- Visual artifacts appear (glitching, incorrect rendering)
- Configuration panel doesn't update simulation in real-time
- Performance drops below 30 FPS with medium grid sizes
- UI elements don't respond to user input
- Memory leaks occur during extended simulation runs
- Shader effects cause WebGL errors or browser crashes
- Initial state doesn't start paused as required


# Details

* The file produced should be name with the model name, you can find it in openRouter parameters : ```[model_name]_timestamp.html```
* commit and push at the end of implementation
* After each commit, read the result for finding bugs or mistakes. If some are found, fix them and commit again.
