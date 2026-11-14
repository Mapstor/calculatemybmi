#!/usr/bin/env python3
"""CMB-049: redraw /blog/underweight-bmi-risks/'s og image (assets/images/og/underweight-cause-tree.png, 1200 x 630) in
its original look, with labels the page now sources: causes from NCHS Health E-Stat 119 ("poor nutrition and
underlying health conditions") and MedlinePlus (digestive problems, medicines and drugs, eating disorders);
consequences from the Global BMI Mortality Collaboration 2016 (higher risk of death), NIAMS (slender, thin-boned
people at greater risk of osteoporosis) and the HHS Office on Women's Health (being underweight among the things that
change a woman's ability to have a baby). The old labels "High metabolism", "Weakened immunity" and "Fatigue" had no
source. usage: python3 research/cmb-049/og_underweight.py [OUT]"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / 'assets/images/og/underweight-cause-tree.png'
F = '/usr/share/fonts/truetype/dejavu/'
W, H = 1200, 630
BG, BAR, RED, RED_BG, RED_TXT = (248, 250, 252), (13, 85, 103), (239, 68, 68), (254, 226, 226), (127, 29, 29)
INK, GREY, LINE, MARK = (34, 34, 34), (99, 100, 101), (176, 176, 176), (163, 175, 194)
CAUSES = ['Poor nutrition', 'Underlying illness', 'Digestive problems', 'Medicines and drugs', 'Eating disorders']
EFFECTS = ['Higher risk of death', 'Osteoporosis risk', 'Fertility problems']


def main():
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    title = ImageFont.truetype(F + 'DejaVuSans-Bold.ttf', 30)
    label = ImageFont.truetype(F + 'DejaVuSerif.ttf', 22)
    centre = ImageFont.truetype(F + 'DejaVuSerif-Bold.ttf', 22)
    small = ImageFont.truetype(F + 'DejaVuSerif.ttf', 18)
    head = ImageFont.truetype(F + 'DejaVuSerif-Bold.ttf', 18)
    mark = ImageFont.truetype(F + 'DejaVuSans.ttf', 18)
    d.rectangle([0, 0, W, 90], fill=BAR)
    d.text((W / 2, 48), 'Underweight — causes and consequences', font=title, fill='white', anchor='mm')
    box = (480, 330, 720, 390)
    ys_l = [172, 252, 352, 452, 532]
    for y, t in zip(ys_l, CAUSES):                      # each line starts 14 px after its label
        x0 = d.textbbox((140, y), t, font=label, anchor='lm')[2] + 14
        d.line([(x0, y + 2), (box[0], 360 + (y - 352) * 0.1)], fill=LINE, width=2)
        d.text((140, y), t, font=label, fill=INK, anchor='lm')
    ys_r = [252, 352, 452]
    for y, t in zip(ys_r, EFFECTS):                     # each line ends 14 px before its label
        x1 = d.textbbox((1060, y), t, font=label, anchor='rm')[0] - 14
        d.line([(x1, y + 2), (box[2], 360 + (y - 352) * 0.1)], fill=LINE, width=2)
        d.text((1060, y), t, font=label, fill=INK, anchor='rm')
    d.rounded_rectangle(box, radius=12, fill=RED_BG, outline=RED, width=3)
    d.text((600, 360), 'Underweight', font=centre, fill=RED_TXT, anchor='mm')
    d.text((600, 405), 'BMI < 18.5', font=small, fill=GREY, anchor='mm')
    d.text((260, 583), 'CAUSES', font=head, fill=GREY, anchor='mm')
    d.text((940, 583), 'CONSEQUENCES', font=head, fill=GREY, anchor='mm')
    d.text((1180, 608), 'CalculateMyBMI', font=mark, fill=MARK, anchor='rm')
    im.save(OUT, optimize=True)
    print(OUT, im.size)


if __name__ == '__main__':
    main()
