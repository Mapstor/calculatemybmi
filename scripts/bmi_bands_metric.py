#!/usr/bin/env python3
"""CDC-rule metric BMI band generator. Rule: BMI = kg/m^2 rounded to 0.1 half-up; categorize with CDC ranges."""
from decimal import Decimal, ROUND_HALF_UP

def round_bmi(v):
    return float(Decimal(str(v)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))

def bmi_kg(kg, cm):
    m = cm / 100.0
    return round_bmi(kg / (m * m))

def category_kg(kg, cm):
    b = bmi_kg(kg, cm)
    if b < 18.5: return "under"
    if b < 25:   return "healthy"
    if b < 30:   return "over"
    if b < 35:   return "ob1"
    if b < 40:   return "ob2"
    return "ob3"

def metric_bands(cm, kg_range=(20, 400)):
    grouped = {}
    for kg in range(kg_range[0], kg_range[1] + 1):
        grouped.setdefault(category_kg(kg, cm), []).append(kg)
    out = {}
    for c in ("under", "healthy", "over", "ob1", "ob2", "ob3"):
        if c in grouped:
            lo, hi = grouped[c][0], grouped[c][-1]
        else:
            lo = hi = None
        if c == "under": lo = None
        if c == "ob3":   hi = None
        out[c] = (lo, hi)
    return out
