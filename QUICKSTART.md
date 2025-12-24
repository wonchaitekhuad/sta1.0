# Quick Start Guide - STA 1.0

## Installation (5 minutes)

### Step 1: Check Python
```bash
python --version
# or
python3 --version
```
You need Python 3.x or higher.

### Step 2: Install Dependencies
```bash
pip install numpy
```

### Step 3: Run the Program
```bash
python MAIN.py
# or
python3 MAIN.py
```

## Your First Analysis (10 minutes)

### Example 1: Simple Beam

1. **Start the program**
   ```bash
   python MAIN.py
   ```

2. **Create nodes:**
   - Click on canvas at position (0, 0) - left end
   - Click on canvas at position (500, 0) - right end
   - Or use menu: Insert → Node and enter coordinates

3. **Create beam:**
   - Select "Draw Member" tool
   - Click first node (left)
   - Click second node (right)
   - A beam is created connecting the two nodes

4. **Add supports:**
   - Select left node
   - Apply "Fixed Support" (fully restrained)
   - Select right node  
   - Apply "Roller Support" (allows horizontal movement)

5. **Add load:**
   - Select the beam member
   - Apply distributed load: 10 kN/m downward
   - Or apply point load at center node

6. **Run analysis:**
   - Click "Analyze" button
   - Wait for calculations to complete

7. **View results:**
   - Select "Bending Moment Diagram" - see the moment distribution
   - Select "Shear Force Diagram" - see shear forces
   - Select "Deflected Shape" - see beam deformation

### Example 2: Portal Frame (Column + Beam)

1. **Create 4 nodes:**
   - Bottom left: (0, 400)
   - Bottom right: (500, 400)
   - Top left: (0, 0)
   - Top right: (500, 0)

2. **Create members:**
   - **Left column**: Connect bottom-left to top-left
   - **Right column**: Connect bottom-right to top-right
   - **Beam**: Connect top-left to top-right
   
   **Important**: You can draw columns in ANY direction!
   - Bottom-to-top ✓ Works!
   - Top-to-bottom ✓ Works!

3. **Add supports:**
   - Bottom-left node: Fixed support
   - Bottom-right node: Pinned support

4. **Add loads:**
   - On beam: 15 kN/m distributed load (downward)
   - On top-left node: 20 kN horizontal load (pushing right)

5. **Analyze and view results:**
   - Click "Analyze"
   - Check all diagrams (BMD, SFD, NFD, Deflection)
   - View support reactions

## Common Workflows

### Workflow 1: Modify Existing Structure

1. Select member to modify
2. Change properties (material, section)
3. Re-run analysis
4. Compare results

### Workflow 2: Multiple Load Cases

1. Create load case 1: "Dead Load"
   - Add permanent loads

2. Create load case 2: "Live Load"
   - Add variable loads

3. Create load case 3: "Wind Load"
   - Add wind forces

4. Create combinations:
   - 1.2 × Dead + 1.6 × Live
   - 1.2 × Dead + 0.5 × Live + 1.3 × Wind

5. Analyze each case/combination
6. Check governing (maximum) values

### Workflow 3: Save and Load

1. **Save project:**
   - File → Save
   - Choose location and filename
   - File extension: .sta

2. **Load project:**
   - File → Open
   - Browse to your .sta file
   - Continue working

## Keyboard Shortcuts

- **Ctrl+N**: New project
- **Ctrl+O**: Open project
- **Ctrl+S**: Save project
- **Delete**: Delete selected element
- **Esc**: Cancel current operation

## Tips for Success

### 1. Drawing Direction ✓ Fixed in v1.0
- **Old problem**: Columns had to be drawn top-to-bottom only
- **Now**: Draw in ANY direction - software handles it automatically!
- Bottom-to-top ✓
- Top-to-bottom ✓
- Left-to-right ✓
- Right-to-left ✓

### 2. Unit Consistency
- Stick to one unit system
- Common: kN, cm, kN/cm²
- Or: N, mm, N/mm²

### 3. Model Validation
- Check supports: structure must be stable
- Check loads: values and directions
- Check member properties: realistic values

### 4. Result Verification
- Do hand calculations for simple cases
- Check equilibrium: reactions = loads
- Verify moment diagram closes properly

### 5. Troubleshooting
- Structure unstable → Add/fix supports
- No results → Check if analysis completed
- Wrong results → Check units and inputs
- Graphs look wrong → Ensure latest version (v1.0)

## Example Problems

### Problem 1: Simply Supported Beam
**Given:**
- Length: 6 m = 600 cm
- Load: 10 kN/m uniformly distributed
- Material: Steel
- Section: I-beam 200x100

**Expected Results:**
- Max moment: 45 kN·m (at center)
- Max shear: 30 kN (at supports)
- Max deflection: ~1.5 cm (at center)

**Setup in Software:**
1. Two nodes: (0,0) and (600,0)
2. One beam connecting them
3. Left support: Pinned
4. Right support: Roller
5. Load: 10 kN/m on beam
6. Analyze

### Problem 2: Cantilever Beam
**Given:**
- Length: 3 m = 300 cm
- Point load: 50 kN at free end
- Fixed at left end

**Expected Results:**
- Max moment: 150 kN·m (at fixed end)
- Max shear: 50 kN (constant)
- Max deflection: at free end

**Setup in Software:**
1. Two nodes: (0,0) and (300,0)
2. One beam
3. Left node: Fixed support
4. Right node: 50 kN downward force
5. Analyze

### Problem 3: Portal Frame
**Given:**
- Width: 8 m
- Height: 4 m
- Horizontal load: 30 kN at top-left

**Setup:**
1. Four nodes forming rectangle
2. Two columns + one beam
3. Fixed supports at base
4. Horizontal load on column
5. Analyze for BMD, SFD, Deflection

## Next Steps

1. **Practice**: Try the examples above
2. **Experiment**: Modify values and see effects
3. **Learn**: Study result diagrams
4. **Verify**: Compare with hand calculations
5. **Apply**: Use for real projects

## Getting Help

- Read README.md for detailed information
- Check common issues in Troubleshooting section
- Open GitHub issue for bugs or questions
- Review code comments for technical details

## Quick Reference

| Action | Menu/Button |
|--------|-------------|
| New project | File → New |
| Open project | File → Open |
| Save project | File → Save |
| Add node | Insert → Node |
| Add member | Draw Member tool |
| Add support | Supports menu |
| Add load | Loads menu |
| Run analysis | Analyze button |
| View BMD | Results → Bending Moment |
| View SFD | Results → Shear Force |
| View deflection | Results → Displacement |

---

**Remember**: This software now handles drawing direction automatically. Draw your structure naturally - the visualization will be correct!

Happy analyzing! 🏗️
