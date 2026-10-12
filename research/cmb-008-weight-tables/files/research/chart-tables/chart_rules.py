#!/usr/bin/env python3
"""BMI chart cell rules shared by the CMB-008 audit and generator.
A weight belongs to a category when its BMI, rounded half-up to 0.1 (calculator.js round1), falls in the band:
Underweight < 18.5 · Healthy 18.5–24.9 · Overweight 25.0–29.9 · Obesity 1 30.0–34.9 · Obesity 2 35.0–39.9 · Obesity 3 ≥ 40.0.
Bounds are whole units (lb or kg) for the exact row height, computed independently per unit."""
import math

BANDS = [(None, 18.4), (18.5, 24.9), (25.0, 29.9), (30.0, 34.9), (35.0, 39.9), (40.0, None)]
NAMES = ['Underweight', 'Healthy weight', 'Overweight', 'Obesity class 1', 'Obesity class 2', 'Obesity class 3']
CM_PER_IN = 2.54
LB_PER_KG = 2.20462

def round1(x):
    return math.floor(x * 10 + 0.5 + 1e-9) / 10

def bmi_lb(lb, inches):
    return 703.0 * lb / (inches * inches)

def bmi_kg(kg, cm):
    m = cm / 100.0
    return kg / (m * m)

def category(bmi):
    r = round1(bmi)
    for i, (lo, hi) in enumerate(BANDS):
        if (lo is None or r >= lo) and (hi is None or r <= hi):
            return i
    raise ValueError(bmi)

def bounds(unit, height, band):
    """Whole-unit (min, max) inside band at this height; None for an open end. unit 'lb' (height in inches) or 'kg' (height in cm)."""
    lo, hi = BANDS[band]
    f = (lambda w: bmi_lb(w, height)) if unit == 'lb' else (lambda w: bmi_kg(w, height))
    scale = (height * height / 703.0) if unit == 'lb' else ((height / 100.0) ** 2)
    wmin = wmax = None
    if lo is not None:
        wmin = math.ceil((lo - 0.05) * scale - 1e-9)
        while category(f(wmin)) < band: wmin += 1          # guard the analytic estimate
        while wmin > 1 and category(f(wmin - 1)) >= band: wmin -= 1
    if hi is not None:
        wmax = math.ceil((hi + 0.05) * scale - 1e-9) - 1
        while category(f(wmax)) > band: wmax -= 1
        while category(f(wmax + 1)) <= band: wmax += 1
    return wmin, wmax

if __name__ == '__main__':
    # spot checks: 5'10" healthy 129-173 lb; 4'10" healthy kg at 147.32 cm
    assert bounds('lb', 70, 1) == (129, 173), bounds('lb', 70, 1)
    print("5'10\" healthy lb", bounds('lb', 70, 1), "| 4'10\" healthy kg", bounds('kg', 58 * CM_PER_IN, 1),
          "| 145 cm healthy kg", bounds('kg', 145, 1), "lb", bounds('lb', 145 / CM_PER_IN, 1))
