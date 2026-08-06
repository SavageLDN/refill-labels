# Agents context for Copilot

This repository contains scripts and assets to generate printable product labels (PDFs) from a Python generator.

Purpose
- Generate individual label PDFs at specific physical sizes and a set of A4 print sheets (plain + with cutting guides).

Architecture
- build_laundry_label.py: Main generator. Uses Pillow and ReportLab to compose labels.
- label_text.py: Helper functions for text layout and shadows.
- assets/: Backdrop images and logo assets used by the generator.
- output/pdf/: Generated PDFs for preview and printing.

Coding standards and patterns
- Prefer clear, small utility functions for layout and drawing (draw_single_label, draw_flavour_artwork, wrap_and_draw_centred).
- Use mm units for all physical sizes to ensure proper print scaling.
- Avoid embedding large generated binaries in commits where possible; prefer storing generated PDFs as release artifacts or using CI to regenerate.

Preferred workflows for Copilot-assisted contributions
- For UI/visual adjustments provide exact numeric nudges in millimetres.
- Use the GitHub Actions workflow `.github/workflows/regenerate-pdfs.yml` to validate changes and produce preview artifacts.

Secrets and environment
- The generator requires no secret keys. If using private registries or APIs add secrets in the repository settings and reference ENV variables in workflows.

Project maintainers
- Primary: ssavage1983

Co-authored-by: Copilot App <223556219+Copilot@users.noreply.github.com>
