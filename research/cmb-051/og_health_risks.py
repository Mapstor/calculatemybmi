#!/usr/bin/env python3
"""CMB-051: /blog/bmi-and-health-risks/'s og image (assets/images/og/bmi-health-risks-death.png, 1200 x 630), in the
site's og look (dark cyan title bar, DejaVu fonts, light background): the Global BMI Mortality Collaboration's nine
hazard ratios (never-smokers without chronic disease, 1.00 = BMI 22.5 to 24.9) as horizontal bars on one scale, in the
calculator's category colours. It replaces bmi-health-risks-matrix.png, whose dot sizes ("qualitative association
strength") no source gave. usage: python3 research/cmb-051/og_health_risks.py [OUT]"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / 'assets/images/og/bmi-health-risks-death.png'
F = '/usr/share/fonts/truetype/dejavu/'
W, H = 1200, 630
BG, BAR, TRACK, INK, GREY, MARK = (248, 250, 252), (13, 85, 103), (241, 245, 249), (34, 34, 34), (99, 100, 101), (163, 175, 194)
COL = {'underweight': (59, 130, 246), 'normal': (34, 197, 94), 'overweight': (245, 158, 11), 'obese': (239, 68, 68)}
GBMC = [('15.0–18.4', 1.51, 'underweight'), ('18.5–19.9', 1.13, 'normal'), ('20.0–22.4', 1.00, 'normal'),
        ('22.5–24.9', 1.00, 'normal'), ('25.0–27.4', 1.07, 'overweight'), ('27.5–29.9', 1.20, 'overweight'),
        ('30.0–34.9', 1.45, 'obese'), ('35.0–39.9', 1.94, 'obese'), ('40.0–59.9', 2.76, 'obese')]


def main():
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    title = ImageFont.truetype(F + 'DejaVuSans-Bold.ttf', 30)
    label = ImageFont.truetype(F + 'DejaVuSans.ttf', 21)
    value = ImageFont.truetype(F + 'DejaVuSans-Bold.ttf', 21)
    small = ImageFont.truetype(F + 'DejaVuSans.ttf', 17)
    mark = ImageFont.truetype(F + 'DejaVuSans.ttf', 18)
    d.rectangle([0, 0, W, 90], fill=BAR)
    d.text((W / 2, 48), 'Risk of death by BMI (hazard ratio)', font=title, fill='white', anchor='mm')
    x_label, x0, x1, top, step, h = 110, 300, 1020, 122, 49, 32
    for k, (r, hr, c) in enumerate(GBMC):
        y = top + k * step
        d.text((x_label, y + h / 2), f'BMI {r}', font=label, fill=INK, anchor='lm')
        d.rounded_rectangle([x0, y, x1, y + h], radius=6, fill=TRACK)
        d.rounded_rectangle([x0, y, x0 + (x1 - x0) * hr / 2.76, y + h], radius=6, fill=COL[c])
        d.text((x1 + 18, y + h / 2), f'{hr:.2f}', font=value, fill=INK, anchor='lm')
    d.text((x_label, 578), '1.00 = BMI 22.5 to 24.9. Never-smokers without chronic disease; '
                           'Global BMI Mortality Collaboration, Lancet 2016.', font=small, fill=GREY, anchor='lm')
    d.text((W - 20, H - 22), 'CalculateMyBMI', font=mark, fill=MARK, anchor='rm')
    im.save(OUT, optimize=True)
    print(f'{OUT}: {im.size[0]} x {im.size[1]}')


if __name__ == '__main__':
    main()
