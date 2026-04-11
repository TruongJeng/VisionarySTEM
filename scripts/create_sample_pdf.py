"""
Create a simple STEM sample PDF for testing.
Tao file PDF STEM mau de test.
"""
import sys
sys.path.insert(0, ".")

import fitz  # PyMuPDF

doc = fitz.open()
page = doc.new_page(width=595, height=842)  # A4

# Title
page.insert_text(
    fitz.Point(150, 60),
    "Dinh luat II Newton",
    fontsize=22,
    fontname="helv",
    color=(0, 0, 0.6),
)

# Subtitle
page.insert_text(
    fitz.Point(120, 90),
    "Newton's Second Law of Motion",
    fontsize=14,
    fontname="helv",
    color=(0.3, 0.3, 0.3),
)

# Description text
page.insert_text(
    fitz.Point(50, 140),
    "Gia toc cua mot vat ti le thuan voi luc tac dung len no",
    fontsize=12,
    fontname="helv",
)
page.insert_text(
    fitz.Point(50, 160),
    "va ti le nghich voi khoi luong cua no.",
    fontsize=12,
    fontname="helv",
)

# Math formula - F = ma
page.insert_text(
    fitz.Point(220, 230),
    "F = m x a",
    fontsize=28,
    fontname="helv",
    color=(0.8, 0, 0),
)

# Second formula
page.insert_text(
    fitz.Point(200, 290),
    "a = F / m",
    fontsize=24,
    fontname="helv",
    color=(0, 0.5, 0),
)

# Third formula
page.insert_text(
    fitz.Point(180, 340),
    "E = m x c^2",
    fontsize=24,
    fontname="helv",
    color=(0, 0, 0.8),
)

# Draw a simple chart area
rect = fitz.Rect(100, 420, 500, 680)
page.draw_rect(rect, color=(0, 0, 0), width=1)

# Chart title
page.insert_text(
    fitz.Point(180, 415),
    "Bieu do Luc - Gia toc (F vs a)",
    fontsize=12,
    fontname="helv",
)

# Y-axis label
page.insert_text(fitz.Point(60, 550), "Luc (N)", fontsize=10, fontname="helv")

# X-axis label
page.insert_text(fitz.Point(260, 700), "Gia toc (m/s2)", fontsize=10, fontname="helv")

# Draw axes
page.draw_line(fitz.Point(130, 650), fitz.Point(480, 650), color=(0, 0, 0), width=1.5)  # X
page.draw_line(fitz.Point(130, 650), fitz.Point(130, 440), color=(0, 0, 0), width=1.5)  # Y

# Draw a simple line (linear relationship F = ma)
points = [
    fitz.Point(130, 650),
    fitz.Point(200, 600),
    fitz.Point(270, 550),
    fitz.Point(340, 500),
    fitz.Point(410, 450),
    fitz.Point(470, 440),
]
for i in range(len(points) - 1):
    page.draw_line(points[i], points[i + 1], color=(1, 0, 0), width=2)

# Data points
for p in points:
    page.draw_circle(p, 3, color=(0, 0, 1), fill=(0, 0, 1))

# Note at bottom
page.insert_text(
    fitz.Point(50, 760),
    "Trang 1/1 - Tai lieu mau VisionarySTEM",
    fontsize=9,
    fontname="helv",
    color=(0.5, 0.5, 0.5),
)

output_path = "tests/sample_data/sample_physics.pdf"
doc.save(output_path)
doc.close()
print(f"Sample PDF created: {output_path}")
