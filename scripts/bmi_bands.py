#!/usr/bin/env python3
"""CDC-rule BMI band generator. Rule: BMI = lb*703/in^2 rounded to 0.1 half-up; categorize with CDC ranges."""
from decimal import Decimal, ROUND_HALF_UP

def round_bmi(v):
    return float(Decimal(str(v)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))

def bmi(w_lb, h_in):
    return round_bmi(w_lb * 703 / (h_in * h_in))

def category(b):
    if b < 18.5: return "under"
    if b < 25:   return "healthy"
    if b < 30:   return "over"
    if b < 35:   return "ob1"
    if b < 40:   return "ob2"
    return "ob3"

def bands(h_in, wmin=50, wmax=400):
    grouped = {}
    for w in range(wmin, wmax + 1):
        grouped.setdefault(category(bmi(w, h_in)), []).append(w)
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
