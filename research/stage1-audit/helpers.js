() => {
  /* CMB-029: B checks run in the audited page with calculator.js's own functions (injected when the page
     doesn't load it). Each helper returns the unrounded value unless its name says otherwise; the audit
     rounds once, half up, to the precision the page prints. */
  const us = f => { const keep = CMB_METRIC; CMB_METRIC = false; try { return f(); } finally { CMB_METRIC = keep; } };
  const metric = f => { const keep = CMB_METRIC; CMB_METRIC = true; try { return f(); } finally { CMB_METRIC = keep; } };
  const A = {
    // BMI with the calculator's formulas: US units use lb x 703 / in^2, metric kg / m^2 (calculateBMI).
    bmi: (lb, inch) => us(() => calculateBMI(lb, inch)),
    bmiM: (kg, cm) => metric(() => calculateBMI(kgToLbs(kg), cm / 2.54)),
    r1: x => round1(x),
    // category as calculator.js names it (getBMICategory works on the BMI rounded once to 0.1)
    cat: b => getBMICategory(b).category,
    catLo: name => ({ 'Severe thinness': -Infinity, 'Moderate thinness': 16, 'Underweight': 17, 'Healthy weight': 18.5, 'Overweight': 25, 'Class 1 obesity': 30, 'Class 2 obesity': 35, 'Class 3 obesity': 40 })[name],
    // whole-unit limits of a BMI band at a height (weightBounds: lb by 703, kg by kg/m^2, each on its own)
    wb: (inch, lo, hi) => weightBounds(inch, lo, hi),
    minLb: (inch, lo, hi) => weightBounds(inch, lo, hi).minLb,
    maxLb: (inch, lo, hi) => weightBounds(inch, lo, hi).maxLb,
    minKg: (inch, lo, hi) => weightBounds(inch, lo, hi).minKg,
    maxKg: (inch, lo, hi) => weightBounds(inch, lo, hi).maxKg,
    // the weight at a BMI for a height: calculateBMI is linear in weight, so w = bmi / calculateBMI(1, h)
    wAt: (b, inch) => us(() => b / calculateBMI(1, inch)),
    kgAt: (b, cm) => metric(() => b / calculateBMI(kgToLbs(1), cm / 2.54)),
    lb2kg: x => lbsToKg(x), kg2lb: x => kgToLbs(x), in2cm: x => inchesToCm(x), cm2in: x => x / 2.54,
    in2m: x => inchesToCm(x) / 100, m2in: x => x * 100 / 2.54,
    ftin: (f, i) => f * 12 + i,
    // nearest whole inch of a metric height, as heightToFtIn rounds it
    cmToFtIn: cm => heightToFtIn(cm / 2.54),
    // New BMI as calculateNewBMI computes it: 1.3 x kg / m^2.5 with the calculator's conversions
    newbmi: (lb, inch) => 1.3 * lbsToKg(lb) / Math.pow(inchesToCm(inch) / 100, 2.5),
    newbmiM: (kg, m) => 1.3 * kg / Math.pow(m, 2.5),
    // CDC LMS (cdc-bmi-lms.js, loaded on the kids page): BMI at a percentile, the median, P95, and the category
    kidsAt: (sex, agemos, p) => { const r = getLMSRow(sex, agemos); const z = stdNormalInv(p / 100); return r.M * Math.pow(1 + r.L * r.S * z, 1 / r.L); },
    kidsM: (sex, agemos) => getLMSRow(sex, agemos).M,
    kidsP95: (sex, agemos) => getLMSRow(sex, agemos).P95,
    kidsPct: (bmi, agemos, sex) => computeKidsPercentile(bmi, agemos, sex).percentile,
    kidsCat: (bmi, agemos, sex) => { const r = computeKidsPercentile(bmi, agemos, sex); return categorizeChildBMI(bmi, r.percentile, r.pctP95).category; },
    // the child category categorizeChildBMI gives a percentile, a share of the 95th percentile and a BMI
    kcat: (pct, pctP95, bmi) => categorizeChildBMI(bmi, pct, pctP95).category,
    // lean body mass: calculateLBM itself, fed through its own panel (metric), its displayLBMResults arguments captured
    lbm: (sex, kg, cm) => {
      const panel = document.getElementById('panel-lbm');
      if (!panel) throw new Error('no LBM panel on this page');
      panel.querySelector('.unit-btn[data-unit="metric"]').click();
      panel.querySelector('.height-cm').value = String(cm);
      panel.querySelector('.weight-kg').value = String(kg);
      panel.querySelector('.sex-select').value = sex;
      let got = null;
      const orig = window.displayLBMResults;
      window.displayLBMResults = function () { got = [...arguments]; return orig.apply(this, arguments); };
      try { calculateLBM(); } finally { window.displayLBMResults = orig; }
      const f = got[1];
      return { boer: f.boer, james: f.james, hume: f.hume, fat: got[2], bf: got[3], kg: got[4] };
    },
    // constants as calculator.js uses them
    k703: () => us(() => calculateBMI(1, 1)),
    kLb: () => kgToLbs(1),
    kIn: () => inchesToCm(1),
    scaleMin: () => { for (let b = 0; b <= 40; b += 0.5) if (getScalePosition(b) > 0) return b - 0.5; return null; },
    scaleMax: () => { for (let b = 60; b >= 0; b -= 0.5) if (getScalePosition(b) < 100) return b + 0.5; return null; },
  };
  // the dataset a registry row serves (set by the audit on the state page): CDC BRFSS state prevalence by year
  A.brfss = (state, year) => { const d = window.__D && window.__D.brfss[state]; if (!d || d[year] === undefined) throw new Error('no BRFSS value for ' + state + ' ' + year); return d[year]; };
  A.brfssAge = (state, grp) => { const d = window.__D && window.__D.age[state]; if (!d || d[grp] === undefined) throw new Error('no BRFSS age value for ' + state + ' ' + grp); return d[grp]; };
  A.brfssCount = (year, thr) => Object.entries(window.__D.brfss).filter(([st, ys]) => window.__D.states.includes(st) && ys[year] !== undefined && ys[year] >= thr).length;
  A.brfssStates = year => Object.entries(window.__D.brfss).filter(([st, ys]) => window.__D.states.includes(st) && ys[year] !== undefined).length;
  // the page's own tables, for checks on what the prose says about them: rows of cell texts
  A.tbl = re => { const t = [...document.querySelectorAll('main table')].find(x => re.test(x.innerText)); if (!t) throw new Error('no table matches ' + re); return [...t.rows].map(r => [...r.cells].map(c => c.innerText.replace(/\s+/g, ' ').trim())); };
  A.ftin = (f, i) => f * 12 + i;
  A.inchesOf = txt => { const m = String(txt).match(/(\d)\s*['\u2032]\s*(\d+)/); if (!m) throw new Error('no height in ' + txt); return +m[1] * 12 + +m[2]; };
  window.__A = A;
  return Object.keys(A).length;
}
