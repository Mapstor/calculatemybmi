#!/usr/bin/env python3
"""CMB-006: healthy min/max tiles put the converted unit on its own line (no mid-unit wrap at 390 px)."""
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8', newline='').read()
old = """  if (healthyMinEl) healthyMinEl.textContent = fmtBound(healthyRange, 'min') + ' (' + fmtBound(healthyRange, 'min', true) + ')';
  if (healthyMaxEl) healthyMaxEl.textContent = fmtBound(healthyRange, 'max') + ' (' + fmtBound(healthyRange, 'max', true) + ')';"""
new = """  if (healthyMinEl) healthyMinEl.innerHTML = fmtBound(healthyRange, 'min') + ' <span class="result-item-alt">(' + fmtBound(healthyRange, 'min', true) + ')</span>';
  if (healthyMaxEl) healthyMaxEl.innerHTML = fmtBound(healthyRange, 'max') + ' <span class="result-item-alt">(' + fmtBound(healthyRange, 'max', true) + ')</span>';"""
assert s.count(old) == 2, s.count(old)
s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('calculator.js: healthy tiles split')
