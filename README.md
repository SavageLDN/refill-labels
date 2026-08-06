Miniml label generator

This repository contains a Python script and assets used to generate printable product labels (individual PDFs and A4 print sheets).

Quick start (Windows):
- Install Python 3.10+ and required libraries (Pillow, reportlab)
- From the project folder run:
  python "build_laundry_label.py"

Outputs:
- Generated PDFs are saved in: output\pdf

Notes:
- Fonts are registered from Windows system fonts; if a font is missing the script falls back to built-ins.
- The script selects the best backdrop image from the assets folder and scales proportionally (no stretching).

Co-authored-by: Copilot App <223556219+Copilot@users.noreply.github.com>
