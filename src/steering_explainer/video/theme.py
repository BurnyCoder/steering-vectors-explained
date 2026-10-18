"""theme.py — colours, fonts and sizes shared by every chapter (3Blue1Brown-like dark style).

Global context: one place for the look so chapters stay consistent. The background equals the
dark chart surface of the study figure (plots.py THEMES["dark"]) so the embedded plot blends in.
Semantic colours: each mathematical role keeps one colour for the whole video (e.g. the steering
vector is always ORANGE, α always YELLOW), so viewers can track symbols by colour as well as shape.
"""

BG = "#1a1a19"  # background (dark surface)
FG = "#f0efec"  # primary text
FG2 = "#c3c2b7"  # secondary text (captions, citations)
MUTED = "#8a8984"  # tertiary (grid, footers)

# semantic colours (role -> colour, fixed across chapters)
VEC = "#58c4dd"  # generic vectors / residual stream h (Manim BLUE_C-like)
STEER = "#ff862f"  # steering vector v / h_A
ALPHA = "#ffd23f"  # scalar coefficient α and other scalars
PLUS = "#83c167"  # positive side: p⁺, c⁺, "Love"
MINUS = "#fc6255"  # negative side: p⁻, c⁻, "Hate"
SET = "#c39bd3"  # sets: ℝ, ℝ^d, D, V
TERM = "#ffd23f"  # newly defined term in definition cards

FONT = "Segoe UI"  # Windows system sans-serif used by Text()
SIZE_TITLE = 44
SIZE_BODY = 32
SIZE_SMALL = 26
SIZE_CITE = 18
