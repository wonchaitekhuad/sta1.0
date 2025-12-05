STA 1.1 (Python + Tkinter) - TI Verified (matches STAAD.Pro BMD)

Contents:
- Sta.py            : Main STA application (corrected BMD plotting to match STAAD.Pro)
- requirements.txt  : Python dependencies (if any)
- README.txt        : This file

How to run (quick):
1. Install Python 3.8+ on your machine (Windows recommended).
2. Open a command prompt in this folder.
3. Run: python Sta.py
   - The application uses tkinter Canvas. No extra GUI libraries required.
   - If your model files (input) are external, place them in the same folder or ensure Sta.py points to them.

How to build a Windows .exe (optional, using PyInstaller):
1. Install PyInstaller:
   pip install pyinstaller
2. Create a single-file executable:
   pyinstaller --onefile --add-data "path_to_your_model_files;." Sta.py
   (On Linux/mac adjust --add-data separator)
3. The exe will appear in the dist/ folder. Copy it into your project folder and run.

Notes about verification with STAAD.Pro:
- This STA version was tuned so BMD direction and shapes match STAAD.Pro for gable/portal frames.
- To check outputs:
  - Run the same load case in both STA and STAAD.Pro.
  - Compare numeric values of Reaction, Shear, Moment at same nodes.
  - Visual comparison: enable BMD in both and ensure sagging is drawn inward/downward.

If you want, I can:
- Add an example model file and a comparison script that reads STA outputs and compares to STAAD.Pro exported TXT values.
- Help build the .exe for you if you upload a Windows environment or allow me access (I cannot run builds on your machine).

Created for TI — happy to further package with examples or create an installer.
