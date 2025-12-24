# STA 1.0 - Structural Analysis Tool

A plane framed structures analysis tool based on the direct stiffness method, built with Python and Tkinter.

## Version
1.0

## Description

This software performs structural analysis on 2D frame structures, calculating:
- Bending moment diagrams
- Shear force diagrams
- Normal (axial) force diagrams
- Displacement/deflection diagrams
- Support reactions

The tool supports various structural configurations including beams, columns, and frame structures with different support conditions and loading scenarios.

## Recent Improvements (v1.0)

### Fixed Direction-Dependent Graph Rendering
- **Issue**: Graphs rendered incorrectly when structural members (beams/columns) were drawn bottom-to-top or right-to-left
- **Solution**: Implemented direction normalization in visualization functions
- **Impact**: Members now render correctly regardless of drawing direction

The fix includes:
- `drawBendingMoment()` - Direction-independent moment diagrams
- `drawShearForce()` - Direction-independent shear force diagrams
- `drawNormalForce()` - Direction-independent axial force diagrams
- `drawDisplacement()` - Direction-independent deflection visualization

## System Requirements

- Python 3.x
- tkinter (usually included with Python)
- numpy

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wonchaitekhuad/sta1.0.git
   cd sta1.0
   ```

2. **Install dependencies:**
   ```bash
   pip install numpy
   ```

3. **Run the application:**
   ```bash
   python MAIN.py
   ```

   Or on some systems:
   ```bash
   python3 MAIN.py
   ```

## Usage

### Getting Started

1. **Launch the program:**
   ```bash
   python MAIN.py
   ```

2. **Create nodes:**
   - Click on the canvas to place nodes
   - Enter node coordinates manually if needed
   - Nodes represent connection points in your structure

3. **Draw members:**
   - Connect nodes to create beams and columns
   - Members can be drawn in any direction (the software handles this automatically)
   - Assign material and section properties

4. **Apply supports:**
   - Select nodes and apply support conditions
   - Options: fixed, pinned, roller supports
   - Specify support orientation

5. **Add loads:**
   - Apply point loads at nodes
   - Apply distributed loads on members
   - Create multiple load cases

6. **Run analysis:**
   - Click "Analyze" to perform structural calculation
   - View results in various diagram formats

7. **View results:**
   - Bending moment diagrams (BMD)
   - Shear force diagrams (SFD)
   - Normal force diagrams (NFD)
   - Deflected shape
   - Support reactions

### Key Features

- **Direction-Independent Drawing**: Draw structural members in any direction without affecting result accuracy
- **Multiple Load Cases**: Analyze different loading scenarios
- **Load Combinations**: Combine multiple load cases with factors
- **Material Library**: Pre-defined materials and sections
- **Save/Load Projects**: Save your work and continue later
- **Export Results**: Export analysis results and diagrams

### Tips

- **Drawing Columns**: You can now draw columns from bottom-to-top OR top-to-bottom - both work correctly!
- **Drawing Beams**: Draw beams from left-to-right OR right-to-left - the software handles both directions
- **Units**: Pay attention to unit consistency in your model
- **Validation**: The software validates your model before analysis

## Project Structure

```
sta1.0/
├── MAIN.py           # Main application entry point and GUI
├── draw.py           # Visualization and drawing functions
├── canvas.py         # Canvas management
├── classes.py        # Core data structures
├── functions.py      # Utility functions
├── action.py         # User interaction handlers
├── run.py            # Analysis engine
├── loadsave.py       # File I/O operations
└── Sta_ok/           # Reference implementation
```

## File Descriptions

- **MAIN.py**: Contains the GUI mainloop and window definitions
- **draw.py**: All drawing functions for structural elements and results visualization
- **canvas.py**: Drawing canvas management and viewport operations
- **classes.py**: Material, Section, Node, and Member class definitions
- **functions.py**: Mathematical and geometric utility functions
- **action.py**: Handles user actions and interactions
- **run.py**: Structural analysis computation engine
- **loadsave.py**: Project file save/load functionality

## Technical Details

### Analysis Method
- **Direct Stiffness Method**: Industry-standard finite element approach
- **Plane Frame Elements**: 3 DOF per node (x, y, rotation)
- **Matrix Assembly**: Global stiffness matrix construction
- **Solver**: Linear system solver for displacements
- **Post-processing**: Force recovery and diagram generation

### Coordinate System
- **X-axis**: Horizontal, positive to the right
- **Y-axis**: Vertical, positive downward (screen coordinates)
- **Rotation**: Counter-clockwise positive

### Direction Normalization
The software automatically normalizes member direction for visualization:
```python
# Detects if member drawn backwards
reverse = p2[0] < p1[0] or (p2[0] == p1[0] and p2[1] < p1[1])

# Normalizes data for consistent plotting
if reverse:
    p1, p2 = p2, p1
    M = list(reversed(M))
    X = [L - x for x in reversed(X)]
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'tkinter'**
   - Install tkinter: `sudo apt-get install python3-tk` (Linux)
   - Tkinter usually comes with Python on Windows/Mac

2. **ImportError: No module named 'numpy'**
   - Install numpy: `pip install numpy`

3. **Graphs not displaying correctly**
   - This issue has been fixed in v1.0
   - Update to the latest version

4. **Program won't start**
   - Check Python version: `python --version` (needs 3.x)
   - Verify all dependencies are installed

## Development

### Code Style
- Follow PEP 8 guidelines
- Use descriptive variable names
- Comment complex algorithms
- Maintain consistency with existing code

### Testing
```bash
# Syntax check
python -m py_compile MAIN.py

# Run the application
python MAIN.py
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Please check the repository for license information.

## Credits

Developed by wonchaitekhuad

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Refer to this README for common problems

## Version History

### v1.0 (Current)
- Fixed direction-dependent graph rendering
- Added direction normalization for all visualization functions
- Improved code documentation
- Added .gitignore for Python artifacts
- Enhanced stability and reliability

---

**Note**: This software is for educational and professional structural analysis purposes. Always verify results with hand calculations or other software for critical applications.
