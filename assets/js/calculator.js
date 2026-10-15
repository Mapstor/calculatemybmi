/* BMI CALCULATOR - ENHANCED JAVASCRIPT */

document.addEventListener('DOMContentLoaded', init);

function init() {
  setupTabs();
  setupCalculateButtons();
  setupUnitToggles();
  // FAQ accordions and the mobile menu are wired by each page's inline script; binding them here too made one tap open and close them.
}

function setupTabs() {
  document.querySelectorAll('.calc-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const tabId = tab.dataset.tab;
      document.querySelectorAll('.calc-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      document.querySelectorAll('.calc-panel').forEach(p => p.classList.remove('active'));
      document.getElementById('panel-' + tabId).classList.add('active');
    });
  });
}

function setupCalculateButtons() {
  document.getElementById('calc-standard-btn')?.addEventListener('click', calculateStandard);
  document.getElementById('calc-women-btn')?.addEventListener('click', calculateWomen);
  document.getElementById('calc-men-btn')?.addEventListener('click', calculateMen);
  document.getElementById('calc-age-btn')?.addEventListener('click', calculateByAge);
  document.getElementById('calc-kids-btn')?.addEventListener('click', calculateKids);
  document.getElementById('calc-ideal-btn')?.addEventListener('click', calculateIdealWeight);
  document.getElementById('calc-lbm-btn')?.addEventListener('click', calculateLBM);
  document.getElementById('calc-newbmi-btn')?.addEventListener('click', calculateNewBMI);
}

function setupUnitToggles() {
  document.querySelectorAll('.unit-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const toggle = btn.closest('.unit-toggle');
      toggle.querySelectorAll('.unit-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const panel = btn.closest('.calc-panel');
      const isMetric = btn.dataset.unit === 'metric';
      panel.querySelectorAll('.imperial-inputs').forEach(el => el.style.display = isMetric ? 'none' : 'grid');
      panel.querySelectorAll('.metric-inputs').forEach(el => el.style.display = isMetric ? 'grid' : 'none');
    });
  });
}

/* ===== UTILITY FUNCTIONS ===== */

function getHeightInches(panel) {
  const isMetric = panel.querySelector('.unit-btn.active')?.dataset.unit === 'metric';
  CMB_METRIC = isMetric;
  if (isMetric) {
    const cm = parseFloat(panel.querySelector('.height-cm')?.value) || 0;
    return cm / 2.54;
  } else {
    const feet = parseFloat(panel.querySelector('.height-ft')?.value) || 0;
    const inches = parseFloat(panel.querySelector('.height-in')?.value) || 0;
    return feet * 12 + inches;
  }
}

function getWeightPounds(panel) {
  const isMetric = panel.querySelector('.unit-btn.active')?.dataset.unit === 'metric';
  if (isMetric) {
    const kg = parseFloat(panel.querySelector('.weight-kg')?.value) || 0;
    return kg * 2.20462;
  } else {
    return parseFloat(panel.querySelector('.weight-lbs')?.value) || 0;
  }
}

function calculateBMI(weightLbs, heightInches) {
  if (heightInches <= 0 || weightLbs <= 0) return 0;
  if (CMB_METRIC) {                                    // metric input: kg/m², exactly as entered (CMB-011)
    const m = heightInches * 0.0254;
    return (weightLbs / 2.20462) / (m * m);
  }
  return (weightLbs / (heightInches * heightInches)) * 703;   // US units: the CDC formula
}

// BMI is shown to one decimal; categories, ranges and tables all use that same rounded value.
function round1(x) { return Math.round(x * 10 + 1e-9) / 10; }
function bmiPrime(bmi) { const r = round1(bmi); return (r < 25 ? Math.min(Math.round(r * 4) / 100, 0.99) : Math.round(r * 4) / 100).toFixed(2); }

function getBMICategory(bmi) {
  bmi = round1(bmi);
  if (bmi < 16) return { category: 'Severe thinness', class: 'underweight', range: 'Below 16', risk: 'Very High' };
  if (bmi < 17) return { category: 'Moderate thinness', class: 'underweight', range: '16–16.9', risk: 'High' };
  if (bmi < 18.5) return { category: 'Underweight', class: 'underweight', range: '17–18.4', risk: 'Moderate' };
  if (bmi < 25) return { category: 'Healthy weight', class: 'normal', range: '18.5–24.9', risk: 'Low' };
  if (bmi < 30) return { category: 'Overweight', class: 'overweight', range: '25–29.9', risk: 'Moderate' };
  if (bmi < 35) return { category: 'Class 1 obesity', class: 'obese', range: '30–34.9', risk: 'High' };
  if (bmi < 40) return { category: 'Class 2 obesity', class: 'obese', range: '35–39.9', risk: 'Very High' };
  return { category: 'Class 3 obesity', class: 'obese-severe', range: '40 or higher', risk: 'Extremely High' };
}

// Whole-unit weights whose BMI, rounded to one decimal, sits inside a band (the rule the BMI charts use).
// BMI 18.45 rounds up to 18.5 and 24.95 rounds up to 25.0, so the exact limits are cut-off -0.05 and +0.05.
// Pounds follow the CDC 703 formula; kilograms follow kg/m², as the metric charts do (CMB-011).
function weightBounds(heightInches, bmiLo, bmiHi) {
  const k = heightInches * heightInches / 703, m2 = Math.pow(heightInches * 0.0254, 2);
  const lo = (bmiLo - 0.05) * k, hi = (bmiHi + 0.05) * k;
  const loKg = (bmiLo - 0.05) * m2, hiKg = (bmiHi + 0.05) * m2;
  return {
    loLb: lo, hiLb: hi, loKg: loKg, hiKg: hiKg,
    minLb: Math.ceil(lo - 1e-9), maxLb: Math.ceil(hi - 1e-9) - 1,
    minKg: Math.ceil(loKg - 1e-9), maxKg: Math.ceil(hiKg - 1e-9) - 1
  };
}

function getHealthyWeightRange(heightInches) {
  const b = weightBounds(heightInches, 18.5, 24.9);
  b.min = b.minLb; b.max = b.maxLb;
  return b;
}

// Healthy-range limit or band in the user's units (alt = the other unit), and the distance from it.
// Limits are whole numbers in the user's unit; the bracketed value converts that same number to one decimal, either way,
// so a converted limit can't round across the category line (72 kg at 170 cm is 158.7 lbs, not 159; CMB-012).
function fmtBound(b, which, alt) {
  const lb = which === 'min' ? b.minLb : b.maxLb, kg = which === 'min' ? b.minKg : b.maxKg;
  if (!alt) return CMB_METRIC ? kg + ' kg' : lb + ' lbs';
  return CMB_METRIC ? (kg * 2.20462).toFixed(1) + ' lbs' : (lb / 2.20462).toFixed(1) + ' kg';
}
function fmtBand(b, alt) {
  if (!alt) return CMB_METRIC ? b.minKg + '–' + b.maxKg + ' kg' : b.minLb + '–' + b.maxLb + ' lbs';
  return CMB_METRIC ? (b.minKg * 2.20462).toFixed(1) + '–' + (b.maxKg * 2.20462).toFixed(1) + ' lbs' : (b.minLb / 2.20462).toFixed(1) + '–' + (b.maxLb / 2.20462).toFixed(1) + ' kg';
}
function bandGap(b, weightLbs) {
  if (CMB_METRIC) {
    const kg = lbsToKg(weightLbs);
    if (kg < b.loKg) return { dir: 'below', lbs: (b.minKg - kg) * 2.20462 };
    if (kg >= b.hiKg) return { dir: 'above', lbs: (kg - b.maxKg) * 2.20462 };
    return { dir: 'inside', lbs: 0 };
  }
  if (weightLbs < b.loLb) return { dir: 'below', lbs: b.minLb - weightLbs };
  if (weightLbs >= b.hiLb) return { dir: 'above', lbs: weightLbs - b.maxLb };
  return { dir: 'inside', lbs: 0 };
}
function healthyRangeText(b, weightLbs) {
  const g = bandGap(b, weightLbs);
  if (g.dir === 'inside') return 'Within the healthy weight range for your height';
  return fmtD(g.lbs) + ' (' + fmtDalt(g.lbs) + ') ' + g.dir + ' the healthy range for your height';
}

function getScalePosition(bmi) {
  const minBMI = 15, maxBMI = 40;
  const clamped = Math.min(Math.max(bmi, minBMI), maxBMI);
  return ((clamped - minBMI) / (maxBMI - minBMI)) * 100;
}

function lbsToKg(lbs) { return lbs / 2.20462; }
function kgToLbs(kg) { return kg * 2.20462; }
function inchesToCm(i) { return i * 2.54; }
function heightToFtIn(inches) {
  const total = Math.round(inches);           // round first so 71.7 in becomes 6'0", not 5'12"
  return Math.floor(total / 12) + "'" + (total % 12) + '"';
}
var CMB_METRIC = false;                         // set from the unit toggle each time heights are read
function fmtW(lbs) { return CMB_METRIC ? lbsToKg(lbs).toFixed(1) + ' kg' : Math.round(lbs) + ' lbs'; }
function fmtWalt(lbs) { return CMB_METRIC ? lbs.toFixed(1) + ' lbs' : lbsToKg(lbs).toFixed(1) + ' kg'; }
function kgD(kg) { return (kg < 10 ? kg.toFixed(1) : String(Math.round(kg))) + ' kg'; }          // small differences keep a decimal: 0.5 kg, not 0 kg
function lbD(lbs) { const r = Math.round(lbs); return r + (r === 1 ? ' lb' : ' lbs'); }
function fmtD(lbs) { return CMB_METRIC ? kgD(lbsToKg(lbs)) : lbD(lbs); }
function fmtDalt(lbs) { return CMB_METRIC ? lbD(lbs) : kgD(lbsToKg(lbs)); }
function fmtH(inches) { return CMB_METRIC ? Math.round(inchesToCm(inches)) + ' cm' : heightToFtIn(inches); }
function fmtHalt(inches) { return CMB_METRIC ? heightToFtIn(inches) : Math.round(inchesToCm(inches)) + ' cm'; }
function getExtendedContainer(type) {
  const section = document.getElementById(type + '-results');
  if (!section) return null;
  let ext = section.querySelector('.er');
  if (!ext) {
    ext = document.createElement('div');
    ext.className = 'er';
    section.appendChild(ext);
  }
  return ext;
}

// Category colours for text and dots: the strong shades, readable on white and on the light tints (CMB-011).
function catColor(cls) {
  const m = { underweight: '#1d4ed8', normal: '#15803d', overweight: '#b45309', obese: '#b91c1c', 'obese-severe': '#991b1b' };
  return m[cls] || '#4b5563';
}
// A weight given in kilograms, in the user's unit and in the other one (ideal weight and lean mass).
// dec = decimals for pounds: whole pounds for the ideal-weight formulas, one decimal for lean mass.
function cmbFmtKg(kg, dec) { return CMB_METRIC ? kg.toFixed(1) + ' kg' : kgToLbs(kg).toFixed(dec || 0) + ' lbs'; }
function cmbFmtKgAlt(kg, dec) { return CMB_METRIC ? kgToLbs(kg).toFixed(dec || 0) + ' lbs' : kg.toFixed(1) + ' kg'; }
function ordinal(n) { const s = ['th', 'st', 'nd', 'rd'], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); }

/* ===== CALCULATOR FUNCTIONS ===== */

function calculateStandard() {
  const panel = document.getElementById('panel-standard');
  const heightInches = getHeightInches(panel);
  const weightLbs = getWeightPounds(panel);
  const bmi = calculateBMI(weightLbs, heightInches);
  if (bmi <= 0) return;
  const category = getBMICategory(bmi);
  const healthyRange = getHealthyWeightRange(heightInches);
  displayBMIResults('standard', bmi, category, healthyRange, heightInches, weightLbs, {});
}

function calculateWomen() {
  const panel = document.getElementById('panel-women');
  const heightInches = getHeightInches(panel);
  const weightLbs = getWeightPounds(panel);
  const bmi = calculateBMI(weightLbs, heightInches);
  if (bmi <= 0) return;
  const category = getBMICategory(bmi);
  const healthyRange = getHealthyWeightRange(heightInches);
  displayBMIResults('women', bmi, category, healthyRange, heightInches, weightLbs, { sex: 'female' });
}

function calculateMen() {
  const panel = document.getElementById('panel-men');
  const heightInches = getHeightInches(panel);
  const weightLbs = getWeightPounds(panel);
  const bmi = calculateBMI(weightLbs, heightInches);
  if (bmi <= 0) return;
  const category = getBMICategory(bmi);
  const healthyRange = getHealthyWeightRange(heightInches);
  displayBMIResults('men', bmi, category, healthyRange, heightInches, weightLbs, { sex: 'male' });
}

function calculateByAge() {
  const panel = document.getElementById('panel-age');
  const heightInches = getHeightInches(panel);
  const weightLbs = getWeightPounds(panel);
  const age = parseInt(panel.querySelector('.age-input')?.value) || 30;
  const bmi = calculateBMI(weightLbs, heightInches);
  if (bmi <= 0) return;
  let adjustedRange;
  if (age < 65) adjustedRange = '18.5–24.9 (WHO adult range)';
  else adjustedRange = '18.5–24.9 (WHO adult range) · lowest mortality observed across BMI 23–33 in adults 65+ (Winter 2014); observational, not a target';
  const category = getBMICategory(bmi);
  const healthyRange = getHealthyWeightRange(heightInches);
  displayBMIResults('age', bmi, category, healthyRange, heightInches, weightLbs, { adjustedRange, age });
}

function calculateKids() {
  var panel = document.getElementById('panel-kids');
  if (!panel) return;
  var heightInches = getHeightInches(panel);
  var weightLbs = getWeightPounds(panel);
  var years = parseInt(panel.querySelector('.age-input')?.value, 10);
  var months = parseInt(panel.querySelector('.months-input')?.value, 10);
  if (isNaN(years)) years = 10;
  if (isNaN(months)) months = 0;
  var agemos = years * 12 + months;
  var sex = panel.querySelector('.sex-select')?.value || 'female';
  // Domain check: CDC extended BMI-for-age covers 24 to <240 months.
  if (agemos < 24 || agemos >= 240) {
    var err = document.getElementById('kids-percentile-note');
    if (err) err.textContent = 'This calculator uses CDC BMI-for-age percentiles for ages 2 to 19 years, 11 months (24 to 239 months). Please enter an age in that range.';
    var section = document.getElementById('kids-results');
    if (section) section.classList.add('visible');
    return;
  }
  var bmi = calculateBMI(weightLbs, heightInches);
  if (bmi <= 0) return;
  var result = computeKidsPercentile(bmi, agemos, sex);
  var percentileCategory = categorizeChildBMI(bmi, result.percentile, result.pctP95);
  displayKidsResults('kids', bmi, percentileCategory, years, months, sex, heightInches, weightLbs, result);
}

function getLMSRow(sex, agemos) {
  // Half-month labels: for agemos m in [24, 240), the CDC row is at floor(m) + 0.5,
  // except the 24.0 boundary row is used exactly for agemos = 24.
  var data = (sex === 'male' || sex === 'boys' || sex === 'boy') ? window.CDC_BMI_LMS.boys : window.CDC_BMI_LMS.girls;
  var target = (agemos === 24) ? 24 : Math.floor(agemos) + 0.5;
  var idx = data.agemos.indexOf(target);
  if (idx === -1) {
    // Nearest fallback
    var best = 0, bestDist = Infinity;
    for (var i = 0; i < data.agemos.length; i++) {
      var d = Math.abs(data.agemos[i] - target);
      if (d < bestDist) { bestDist = d; best = i; }
    }
    idx = best;
  }
  return { L: data.L[idx], M: data.M[idx], S: data.S[idx], sigma: data.sigma[idx], P95: data.P95[idx] };
}

function stdNormalCdf(z) {
  // Abramowitz & Stegun 26.2.17 approximation, |error| < 7.5e-8
  var b1 = 0.319381530, b2 = -0.356563782, b3 = 1.781477937, b4 = -1.821255978, b5 = 1.330274429, p = 0.2316419;
  var absZ = Math.abs(z);
  var t = 1 / (1 + p * absZ);
  var pdf = Math.exp(-absZ * absZ / 2) / Math.sqrt(2 * Math.PI);
  var val = 1 - pdf * (b1*t + b2*t*t + b3*t*t*t + b4*Math.pow(t,4) + b5*Math.pow(t,5));
  return z < 0 ? 1 - val : val;
}

function stdNormalInv(p) {
  // Beasley-Springer-Moro approximation for the inverse normal CDF
  if (p <= 0 || p >= 1) return NaN;
  var a=[-39.6968302866538,220.946098424521,-275.928510446969,138.357751867269,-30.6647980661472,2.50662827745924];
  var b=[-54.4760987982241,161.585836858041,-155.698979859887,66.8013118877197,-13.2806815528857];
  var c=[-0.00778489400243029,-0.322396458041136,-2.40075827716184,-2.54973253934373,4.37466414146497,2.93816398269878];
  var d=[0.00778469570904146,0.32246712907004,2.445134137143,3.75440866190742];
  var pLow = 0.02425, pHigh = 1 - pLow;
  var q, r, x;
  if (p < pLow) {
    q = Math.sqrt(-2*Math.log(p));
    x = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);
  } else if (p <= pHigh) {
    q = p - 0.5;
    r = q*q;
    x = (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1);
  } else {
    q = Math.sqrt(-2*Math.log(1-p));
    x = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);
  }
  return x;
}

function computeKidsPercentile(bmi, agemos, sex) {
  var row = getLMSRow(sex, agemos);
  var z, percentile;
  if (bmi <= row.P95) {
    z = (Math.pow(bmi / row.M, row.L) - 1) / (row.L * row.S);
    percentile = stdNormalCdf(z) * 100;
  } else {
    percentile = 90 + 10 * stdNormalCdf((bmi - row.P95) / row.sigma);
    if (percentile >= 100) percentile = 99.99;
    z = stdNormalInv(percentile / 100);
  }
  var pctP95 = 100 * bmi / row.P95;
  return { percentile: percentile, z: z, pctP95: pctP95, row: row };
}

function categorizeChildBMI(bmi, percentile, pctP95) {
  // CDC child-teen categories: <5 under; 5–<85 healthy; 85–<95 overweight; ≥95 obese; severe: ≥120% P95 or BMI ≥35
  if (pctP95 >= 120 || bmi >= 35) return { category: 'Severe obesity', class: 'obese', note: 'At or above 120% of the 95th percentile' };
  if (percentile >= 95) return { category: 'Obesity', class: 'obese', note: '95th percentile or above' };
  if (percentile >= 85) return { category: 'Overweight', class: 'overweight', note: '85th to below 95th percentile' };
  if (percentile >= 5)  return { category: 'Healthy weight', class: 'normal', note: '5th to below 85th percentile' };
  return { category: 'Underweight', class: 'underweight', note: 'Below the 5th percentile' };
}


function calculateIdealWeight() {
  const panel = document.getElementById('panel-ideal');
  const heightInches = getHeightInches(panel);
  const sex = panel.querySelector('.sex-select')?.value || 'female';
  const frame = panel.querySelector('.frame-select')?.value || 'medium';
  if (heightInches <= 0) return;
  let devine, robinson, miller, hamwi;
  const heightOver5ft = Math.max(0, heightInches - 60);
  if (sex === 'male') {
    devine = 50 + 2.3 * heightOver5ft;
    robinson = 52 + 1.9 * heightOver5ft;
    miller = 56.2 + 1.41 * heightOver5ft;
    hamwi = 48 + 2.7 * heightOver5ft;
  } else {
    devine = 45.5 + 2.3 * heightOver5ft;
    robinson = 49 + 1.7 * heightOver5ft;
    miller = 53.1 + 1.36 * heightOver5ft;
    hamwi = 45.5 + 2.2 * heightOver5ft;
  }
  let frameAdjust = 1;
  if (frame === 'small') frameAdjust = 0.9;
  if (frame === 'large') frameAdjust = 1.1;
  devine *= frameAdjust; robinson *= frameAdjust; miller *= frameAdjust; hamwi *= frameAdjust;
  displayIdealWeightResults('ideal', { devine, robinson, miller, hamwi }, heightInches, sex, frame);
}

function calculateLBM() {
  const panel = document.getElementById('panel-lbm');
  const heightInches = getHeightInches(panel);
  const weightLbs = getWeightPounds(panel);
  const sex = panel.querySelector('.sex-select')?.value || 'female';
  if (heightInches <= 0 || weightLbs <= 0) return;
  const weightKg = lbsToKg(weightLbs);
  const heightCm = inchesToCm(heightInches);
  // Boer
  let boer = sex === 'male' ? 0.407 * weightKg + 0.267 * heightCm - 19.2 : 0.252 * weightKg + 0.473 * heightCm - 48.3;
  // James
  let james = sex === 'male' ? 1.1 * weightKg - 128 * (weightKg / heightCm) * (weightKg / heightCm) : 1.07 * weightKg - 148 * (weightKg / heightCm) * (weightKg / heightCm);
  // Hume
  let hume = sex === 'male' ? 0.32810 * weightKg + 0.33929 * heightCm - 29.5336 : 0.29569 * weightKg + 0.41813 * heightCm - 43.2933;
  const lbm = boer;
  const fatMass = weightKg - lbm;
  const bodyFatPct = (fatMass / weightKg) * 100;
  displayLBMResults('lbm', { boer, james, hume }, fatMass, bodyFatPct, weightKg, weightLbs, heightInches, sex);
}

function calculateNewBMI() {
  const panel = document.getElementById('panel-newbmi');
  const heightInches = getHeightInches(panel);
  const weightLbs = getWeightPounds(panel);
  if (heightInches <= 0 || weightLbs <= 0) return;
  const weightKg = lbsToKg(weightLbs);
  const heightM = inchesToCm(heightInches) / 100;
  const traditionalBMI = calculateBMI(weightLbs, heightInches);
  const newBMI = 1.3 * weightKg / Math.pow(heightM, 2.5);
  const diff = round1(newBMI) - round1(traditionalBMI);
  const traditionalCat = getBMICategory(traditionalBMI);
  const newCat = getBMICategory(newBMI);
  const healthyRange = getHealthyWeightRange(heightInches);
  displayNewBMIResults('newbmi', traditionalBMI, newBMI, diff, traditionalCat, newCat, healthyRange, heightInches, weightLbs);
}

/* ===== SHARED HTML GENERATORS ===== */

function genClassificationTable(bmi) {
  bmi = round1(bmi);
  const cats = [
    ['Severe thinness', 'Below 16', 'underweight'],
    ['Moderate thinness', '16–16.9', 'underweight'],
    ['Underweight', '17–18.4', 'underweight'],
    ['Healthy weight', '18.5–24.9', 'normal'],
    ['Overweight', '25–29.9', 'overweight'],
    ['Class 1 obesity', '30–34.9', 'obese'],
    ['Class 2 obesity', '35–39.9', 'obese'],
    ['Class 3 obesity', '40 or higher', 'obese-severe']
  ];
  const thresholds = [0, 16, 17, 18.5, 25, 30, 35, 40, Infinity];
  let activeIdx = 0;
  for (let i = 0; i < thresholds.length - 1; i++) {
    if (bmi >= thresholds[i] && bmi < thresholds[i + 1]) { activeIdx = i; break; }
  }
  let rows = '';
  cats.forEach((c, i) => {
    const active = i === activeIdx;
    rows += `<tr${active ? ' class="er-active"' : ''}><td><span class="er-dot" style="background:${catColor(c[2])};"></span>${c[0]}${active ? ' <span class="er-you">You: ' + bmi.toFixed(1) + '</span>' : ''}</td><td class="er-num">${c[1]}</td></tr>`;
  });
  return `<table class="er-table"><thead><tr><th>Category</th><th class="er-num">BMI range</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function genKeyMetrics(bmi, heightInches, weightLbs) {
  const weightKg = lbsToKg(weightLbs);
  const heightCm = inchesToCm(heightInches);
  const r = round1(bmi), prime = bmiPrime(r);
  const ponderal = (weightKg / Math.pow(heightCm / 100, 3)).toFixed(1);
  return `<div class="er-metrics er-metrics-4">
    <div class="er-metric"><div class="er-metric-label">BMI Prime</div><div class="er-metric-value">${prime}</div><div class="er-metric-sub">${r < 25 ? 'Under the overweight cut-off' : 'At or over the overweight cut-off'}</div></div>
    <div class="er-metric"><div class="er-metric-label">Ponderal Index</div><div class="er-metric-value">${ponderal}</div><div class="er-metric-sub">kg/m&sup3;</div></div>
    <div class="er-metric"><div class="er-metric-label">Weight</div><div class="er-metric-value">${fmtW(weightLbs)}</div><div class="er-metric-sub">${fmtWalt(weightLbs)}</div></div>
    <div class="er-metric"><div class="er-metric-label">Height</div><div class="er-metric-value">${fmtH(heightInches)}</div><div class="er-metric-sub">${fmtHalt(heightInches)}</div></div>
  </div>`;
}

function genWeightMilestones(bmi, heightInches, weightLbs) {
  const healthy = weightBounds(heightInches, 18.5, 24.9);
  const from = cut => weightBounds(heightInches, cut, 99);
  const targets = [
    { label: 'Healthy range starts', bmiVal: 18.5, lb: healthy.minLb, kg: healthy.minKg },
    { label: 'Healthy range ends', bmiVal: 24.9, lb: healthy.maxLb, kg: healthy.maxKg },
    { label: 'Overweight starts', bmiVal: 25, lb: from(25).minLb, kg: from(25).minKg },
    { label: 'Obesity starts', bmiVal: 30, lb: from(30).minLb, kg: from(30).minKg },
    { label: 'Class 2 obesity starts', bmiVal: 35, lb: from(35).minLb, kg: from(35).minKg },
    { label: 'Class 3 obesity starts', bmiVal: 40, lb: from(40).minLb, kg: from(40).minKg },
  ];
  let rows = '';
  targets.forEach(t => {
    const w = CMB_METRIC ? t.kg * 2.20462 : t.lb;
    const diff = w - weightLbs;
    const dU = CMB_METRIC ? Math.round(lbsToKg(diff)) : Math.round(diff), uL = CMB_METRIC ? ' kg' : (Math.abs(dU) === 1 ? ' lb' : ' lbs');
    const diffStr = dU > 0 ? '+' + dU + uL : dU < 0 ? '−' + Math.abs(dU) + uL : '—';
    const isNear = Math.abs(bmi - t.bmiVal) < 2.5;
    rows += `<tr${isNear ? ' class="er-near"' : ''}><td>${t.label}</td><td class="er-num">${t.bmiVal}</td><td class="er-num">${CMB_METRIC ? t.kg + ' kg' : t.lb + ' lbs'}<span class="er-alt">${fmtWalt(w)}</span></td><td class="er-num">${diffStr}</td></tr>`;
  });
  return `<table class="er-table"><thead><tr><th>Milestone</th><th class="er-num">BMI</th><th class="er-num">Weight</th><th class="er-num">Change</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function genWhatIf(bmi, heightInches, weightLbs) {
  const changes = CMB_METRIC ? [-10, -7.5, -5, -2.5, 0, 2.5, 5, 7.5, 10] : [-20, -15, -10, -5, 0, 5, 10, 15, 20];
  const unit = CMB_METRIC ? ' kg' : ' lbs';
  let rows = '';
  changes.forEach(c => {
    const newW = weightLbs + (CMB_METRIC ? kgToLbs(c) : c);
    if (newW <= 0) return;
    const newBmi = round1(calculateBMI(newW, heightInches));
    const cat = getBMICategory(newBmi);
    const isCurrent = c === 0;
    rows += `<tr${isCurrent ? ' class="er-active"' : ''}><td class="er-num">${c === 0 ? 'Current' : (c > 0 ? '+' + c : '−' + Math.abs(c)) + unit}</td><td class="er-num">${fmtW(newW)}</td><td class="er-num" style="font-weight:600;color:${catColor(cat.class)};">${newBmi.toFixed(1)}</td><td>${cat.category}</td></tr>`;
  });
  return `<table class="er-table"><thead><tr><th class="er-num">Change</th><th class="er-num">Weight</th><th class="er-num">BMI</th><th>Category</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function genWeightProgressBar(weightLbs, healthyRange) {
  const zMin = CMB_METRIC ? healthyRange.minKg * 2.20462 : healthyRange.minLb;
  const zMax = CMB_METRIC ? healthyRange.maxKg * 2.20462 : healthyRange.maxLb;
  const min = zMin * 0.75;
  const max = zMax * 1.35;
  const range = max - min;
  const pos = Math.max(0, Math.min(100, ((weightLbs - min) / range) * 100));
  const hMinPos = ((zMin - min) / range) * 100;
  const hMaxPos = ((zMax - min) / range) * 100;
  return `<div class="er-weightbar" role="img" aria-label="Your weight, ${fmtW(weightLbs)}, against the healthy range for your height, ${fmtBand(healthyRange)}">
    <div class="er-weightbar-zone" style="left:${hMinPos}%;width:${hMaxPos - hMinPos}%;"></div>
    <div class="er-weightbar-marker" style="left:${pos}%;"></div>
    <div class="er-weightbar-you" style="left:${Math.max(10, Math.min(90, pos))}%;">${fmtW(weightLbs)}</div>
    <div class="er-weightbar-tick" style="left:${hMinPos}%;">${CMB_METRIC ? healthyRange.minKg : healthyRange.minLb}</div>
    <div class="er-weightbar-tick" style="left:${hMaxPos}%;">${CMB_METRIC ? healthyRange.maxKg : healthyRange.maxLb}</div>
  </div>`;
}

function genSummary(bmi, category, weightLbs, healthyRange, extra) {
  let text = '';
  const rng = fmtBand(healthyRange);
  const gap = fmtD(bandGap(healthyRange, weightLbs).lbs);
  if (category.class === 'normal') {
    text = `Your BMI of <strong>${bmi.toFixed(1)}</strong> is in the <strong>healthy weight</strong> range (18.5 to under 25). At your height, that range is <strong>${rng}</strong>.`;
  } else if (category.class === 'underweight') {
    text = `Your BMI of <strong>${bmi.toFixed(1)}</strong> is below 18.5, the <strong>underweight</strong> cut-off. At your height, the healthy range is <strong>${rng}</strong>, which starts <strong>${gap}</strong> above your current weight. A doctor can tell you whether this is normal for you.`;
  } else if (category.class === 'overweight') {
    text = `Your BMI of <strong>${bmi.toFixed(1)}</strong> is in the <strong>overweight</strong> range (25 to under 30). At your height, the healthy range is <strong>${rng}</strong>; its top is <strong>${gap}</strong> below your current weight. BMI can&rsquo;t tell muscle from fat, so a <a href="/body-fat-calculator/">body fat estimate</a> or a waist measurement adds useful context.`;
  } else {
    text = `Your BMI of <strong>${bmi.toFixed(1)}</strong> is in the <strong>${category.category.toLowerCase()}</strong> range. At your height, the healthy range is <strong>${rng}</strong>; its top is <strong>${gap}</strong> below your current weight. A doctor can put this in context with your other health measures.`;
  }
  let note = '';
  if (extra && extra.age >= 65) {
    note = `<p class="er-summary-note">WHO cut-offs still apply at 65 and over. A meta-analysis of 197,940 adults aged 65 and older found the lowest all-cause mortality across BMI 23 to 33 (<a href="https://pubmed.ncbi.nlm.nih.gov/24452240/" target="_blank" rel="noopener">Winter et al., 2014</a>); it is an observational finding, not a target, and your doctor can say what applies to you.</p>`;
  }
  return `<div class="er-summary"><p>${text}</p>${note}</div>`;
}

/* ===== DISPLAY: BMI RESULTS (Standard, Women, Men, Age) ===== */

function displayBMIResults(type, bmi, category, healthyRange, heightInches, weightLbs, extra) {
  extra = extra || {};
  const section = document.getElementById(type + '-results');
  if (!section) return;

  // Basic existing elements
  const bmiValueEl = document.getElementById(type + '-bmi-value');
  const bmiCategoryEl = document.getElementById(type + '-bmi-category');
  const bmiRangeEl = document.getElementById(type + '-bmi-range');
  const resultCard = document.getElementById(type + '-result-card');
  bmi = round1(bmi);
  if (bmiValueEl) bmiValueEl.textContent = bmi.toFixed(1);
  if (bmiCategoryEl) bmiCategoryEl.textContent = category.category;
  if (bmiRangeEl) bmiRangeEl.textContent = 'BMI range: ' + category.range;
  if (resultCard) {
    resultCard.className = 'bmi-result-card ' + category.class;
    if (bmiValueEl) bmiValueEl.className = 'bmi-value ' + category.class;
  }
  const marker = document.getElementById(type + '-scale-marker');
  if (marker) marker.style.left = getScalePosition(bmi) + '%';
  const healthyMinEl = document.getElementById(type + '-healthy-min');
  const healthyMaxEl = document.getElementById(type + '-healthy-max');
  if (healthyMinEl) healthyMinEl.innerHTML = fmtBound(healthyRange, 'min') + ' <span class="result-item-alt">(' + fmtBound(healthyRange, 'min', true) + ')</span>';
  if (healthyMaxEl) healthyMaxEl.innerHTML = fmtBound(healthyRange, 'max') + ' <span class="result-item-alt">(' + fmtBound(healthyRange, 'max', true) + ')</span>';
  const weightDiffEl = document.getElementById(type + '-weight-diff');
  if (weightDiffEl) weightDiffEl.textContent = healthyRangeText(healthyRange, weightLbs);
  if (extra.adjustedRange) {
    const adjustedEl = document.getElementById(type + '-adjusted-range');
    if (adjustedEl) adjustedEl.textContent = extra.adjustedRange;
  }

  section.classList.add('visible');

  // === EXTENDED RESULTS (CMB-011: the answer first, reference tables after) ===
  const ext = getExtendedContainer(type);
  if (!ext) return;

  let html = '';

  // 1. What the number means, in words
  html += `<div class="er-section"><h2>What your result means</h2>${genSummary(bmi, category, weightLbs, healthyRange, extra)}</div>`;

  // 2. Weight position bar
  html += `<div class="er-section"><h2>Where your weight falls</h2><p class="er-note">The green band is the healthy weight range for your height.</p>${genWeightProgressBar(weightLbs, healthyRange)}</div>`;

  // 3. Weight milestones
  html += `<div class="er-section"><h2>Weight milestones for your height</h2><p class="er-note">The weight at each BMI threshold for ${fmtH(heightInches)} (${fmtHalt(heightInches)}).</p>${genWeightMilestones(bmi, heightInches, weightLbs)}</div>`;

  // 4. What-if scenarios
  html += `<div class="er-section"><h2>What-if weight scenarios</h2><p class="er-note">How gaining or losing weight would change your BMI and category.</p>${genWhatIf(bmi, heightInches, weightLbs)}</div>`;

  // 5. Classification table
  html += `<div class="er-section"><h2>BMI categories</h2>${genClassificationTable(bmi)}</div>`;

  // 6. The remaining numbers
  html += `<div class="er-section"><h2>More numbers</h2>${genKeyMetrics(bmi, heightInches, weightLbs)}</div>`;

  // 7. Sex-specific section (sourced: NIH/NHLBI 1998 waist cut-offs)
  if (extra.sex === 'female' || extra.sex === 'male') {
    const w = extra.sex === 'female' ? '35 inches (88 cm)' : '40 inches (102 cm)';
    const who = extra.sex === 'female' ? 'women' : 'men';
    html += `<div class="er-section"><h2>What else to check</h2>
      <p class="er-note"><strong>Waist size:</strong> US clinical guidelines (NIH) treat a waist above ${w} as a sign of higher risk for ${who}, mainly at a BMI of 25 to 34.9.</p>
      <p class="er-note"><strong>Body fat:</strong> estimate yours with the <a href="/body-fat-calculator/">body fat calculator</a> and see what&rsquo;s typical for your age on the <a href="/body-fat-percentage-chart/">body fat percentage chart</a>. For formula-based weight ranges, see the <a href="/ideal-weight/">ideal weight calculator</a>.</p>
    </div>`;
  }

  // 8. Age: the adult range does not change with age (WHO publishes no age-adjusted cut-offs)
  if (extra.age) {
    let ageText = `At ${extra.age}, the healthy BMI range is 18.5 to 24.9, the same as at every adult age. WHO does not publish age-adjusted BMI cut-offs.`;
    if (extra.age < 20) ageText += ` Under 20, CDC reads BMI against growth charts for age and sex; the <a href="/kids-bmi-calculator/">BMI calculator for children and teens</a> gives that percentile.`;
    html += `<div class="er-section"><h2>BMI and your age</h2><p class="er-note">${ageText}</p></div>`;
  }

  // 9. Health
  html += `<div class="er-section"><h2>BMI and health</h2><p class="er-note">BMI is a screening measure, not a diagnosis. For what the research says about BMI and specific health risks, see our guide to <a href="/blog/bmi-and-health-risks/">BMI and health risks</a>.</p></div>`;

  ext.innerHTML = html;
}

/* ===== DISPLAY: KIDS RESULTS ===== */

function displayKidsResults(type, bmi, category, years, months, sex, heightInches, weightLbs, result) {
  if (typeof months !== 'number') months = 0;
  const section = document.getElementById(type + '-results');
  if (!section) return;

  const bmiValueEl = document.getElementById(type + '-bmi-value');
  const bmiCategoryEl = document.getElementById(type + '-bmi-category');
  const percentileEl = document.getElementById(type + '-percentile-note');
  const resultCard = document.getElementById(type + '-result-card');
  const sexLabel = sex === 'male' ? 'boys' : 'girls';
  const ageText = years + (years === 1 ? ' year' : ' years') + (months ? ' ' + months + (months === 1 ? ' month' : ' months') : '');
  const pct = result ? result.percentile : null;
  const pctText = pct === null ? '' : pct >= 99.5 ? 'Above the 99th percentile' : pct < 0.5 ? 'Below the 1st percentile' : ordinal(Math.round(pct)) + ' percentile';

  if (bmiValueEl) { bmiValueEl.textContent = bmi.toFixed(1); bmiValueEl.className = 'bmi-value ' + category.class; }
  if (bmiCategoryEl) bmiCategoryEl.textContent = category.category;
  if (percentileEl) percentileEl.innerHTML = pctText ? '<strong>' + pctText + '</strong> for ' + sexLabel + ' aged ' + ageText : category.note;
  if (resultCard) resultCard.className = 'bmi-result-card ' + category.class;

  section.classList.add('visible');

  const ext = getExtendedContainer(type);
  if (!ext) return;

  let html = '';

  // 1. What it means, in words
  const b = `<strong>${bmi.toFixed(1)}</strong>`, at = `at ${ageText}`;
  let guidance = '';
  if (category.category === 'Healthy weight') {
    guidance = `A BMI of ${b} ${at} is in the <strong>healthy weight</strong> range for ${sexLabel} (the 5th to below the 85th percentile).`;
  } else if (category.category === 'Underweight') {
    guidance = `A BMI of ${b} ${at} is <strong>below the 5th percentile</strong> for ${sexLabel}, which CDC classes as underweight. That can be normal for a child&rsquo;s growth pattern or a sign that needs attention; a pediatrician can tell which.`;
  } else if (category.category === 'Overweight') {
    guidance = `A BMI of ${b} ${at} is in the <strong>overweight</strong> range for ${sexLabel} (the 85th to below the 95th percentile). Children are still growing, so one reading says little on its own; a pediatrician can look at the growth trend.`;
  } else if (category.category === 'Severe obesity') {
    guidance = `A BMI of ${b} ${at} is at or above <strong>120% of the 95th percentile</strong> for ${sexLabel}, which CDC classes as severe obesity. Talk with your pediatrician, who can look at the growth trend and the whole child before deciding on any next step.`;
  } else {
    guidance = `A BMI of ${b} ${at} is at or above the <strong>95th percentile</strong> for ${sexLabel}, which CDC classes as obesity. Talk with your pediatrician, who can look at the growth trend and the whole child before deciding on any next step.`;
  }
  html += `<div class="er-section"><h2>What this means</h2><div class="er-summary"><p>${guidance}</p><p class="er-summary-note">This uses the CDC BMI-for-age growth charts, with CDC&rsquo;s 2022 extended charts above the 95th percentile. One reading is a screening result, not a diagnosis; pediatricians follow BMI-for-age across checkups.</p></div></div>`;

  // 2. Percentile categories
  const catRows = [['underweight', 'Underweight', 'Below the 5th percentile'], ['normal', 'Healthy weight', '5th to below the 85th'], ['overweight', 'Overweight', '85th to below the 95th'], ['obese', 'Obesity', '95th and above'], ['obese-severe', 'Severe obesity', '120% of the 95th or more, or BMI 35+']];
  let rows = '';
  catRows.forEach(c => {
    const active = category.category === c[1];
    rows += `<tr${active ? ' class="er-active"' : ''}><td><span class="er-dot" style="background:${catColor(c[0])};"></span>${c[1]}${active ? ' <span class="er-you">You</span>' : ''}</td><td>${c[2]}</td></tr>`;
  });
  html += `<div class="er-section"><h2>BMI-for-age categories</h2>
    <p class="er-note">A child&rsquo;s BMI is compared with CDC growth charts for the same age and sex.</p>
    <table class="er-table"><thead><tr><th>Category</th><th>Percentile</th></tr></thead><tbody>${rows}</tbody></table></div>`;

  // 3. The numbers behind the result
  html += `<div class="er-section"><h2>More numbers</h2>
    <div class="er-metrics er-metrics-4">
      <div class="er-metric"><div class="er-metric-label">Percentile</div><div class="er-metric-value">${result ? result.percentile.toFixed(1) : '&mdash;'}</div><div class="er-metric-sub">${result ? 'z = ' + result.z.toFixed(2) : ''}</div></div>
      <div class="er-metric"><div class="er-metric-label">% of 95th percentile</div><div class="er-metric-value">${result ? result.pctP95.toFixed(1) + '%' : '&mdash;'}</div><div class="er-metric-sub">Severe obesity starts at 120%</div></div>
      <div class="er-metric"><div class="er-metric-label">Weight</div><div class="er-metric-value">${fmtW(weightLbs)}</div><div class="er-metric-sub">${fmtWalt(weightLbs)}</div></div>
      <div class="er-metric"><div class="er-metric-label">Height</div><div class="er-metric-value">${fmtH(heightInches)}</div><div class="er-metric-sub">${fmtHalt(heightInches)}</div></div>
    </div></div>`;

  ext.innerHTML = html;
}

/* ===== DISPLAY: IDEAL WEIGHT RESULTS ===== */

function displayIdealWeightResults(type, weights, heightInches, sex, frame) {
  const section = document.getElementById(type + '-results');
  if (!section) return;
  const W = kg => cmbFmtKg(kg), Walt = kg => cmbFmtKgAlt(kg);
  const hr = getHealthyWeightRange(heightInches);
  ['devine', 'robinson', 'miller', 'hamwi'].forEach(k => {
    const el = document.getElementById(type + '-' + k);
    if (el) el.innerHTML = W(weights[k]) + ' <span class="result-item-alt">(' + Walt(weights[k]) + ')</span>';
  });
  const bmiRangeEl = document.getElementById(type + '-bmi-range');
  if (bmiRangeEl) bmiRangeEl.innerHTML = fmtBand(hr) + ' <span class="result-item-alt">(' + fmtBand(hr, true) + ')</span>';
  const avg = (weights.devine + weights.robinson + weights.miller + weights.hamwi) / 4;
  const avgEl = document.getElementById(type + '-average');
  if (avgEl) avgEl.innerHTML = cmbFmtKg(avg, 1) + ' <span class="result-item-alt">(' + cmbFmtKgAlt(avg, 1) + ')</span>';

  section.classList.add('visible');

  const ext = getExtendedContainer(type);
  if (!ext) return;

  const all = [weights.devine, weights.robinson, weights.miller, weights.hamwi];
  const minW = Math.min(...all), maxW = Math.max(...all);
  const frameLabel = frame.charAt(0).toUpperCase() + frame.slice(1);
  const adj = frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1;
  const mediumAvg = avg / adj;
  const bmis = all.map(kg => round1(calculateBMI(kgToLbs(kg), heightInches)));
  const bLo = Math.min(...bmis), bHi = Math.max(...bmis);
  const where = bLo >= 18.5 && bHi < 25 ? 'inside the healthy range of 18.5 to 24.9'
    : bHi < 18.5 ? 'below the healthy range of 18.5 to 24.9'
    : bLo >= 25 ? 'above the healthy range of 18.5 to 24.9'
    : 'partly outside the healthy range of 18.5 to 24.9';
  const bmiText = bLo === bHi ? 'would be ' + bLo.toFixed(1) : 'would be ' + bLo.toFixed(1) + ' to ' + bHi.toFixed(1);

  let html = '';

  html += `<div class="er-section"><h2>What these numbers are</h2><div class="er-summary"><p>For ${fmtH(heightInches)} (${fmtHalt(heightInches)}), ${sex === 'male' ? 'male' : 'female'}, ${frameLabel.toLowerCase()} frame, the four formulas span <strong>${W(minW)}</strong> to <strong>${W(maxW)}</strong>. At those weights your BMI ${bmiText}, ${where}.</p><p class="er-summary-note">The formulas come from clinical work such as drug dosing; for judging a healthy weight, the BMI range in the results above is the standard.</p></div></div>`;

  html += `<div class="er-section"><h2>Where the formulas come from</h2>
    <ul class="er-list">
      <li><strong>Devine (1974):</strong> published for drug dosing, in an article on gentamicin.</li>
      <li><strong>Robinson (1983):</strong> fitted to the 1959 Metropolitan Life height&ndash;weight tables.</li>
      <li><strong>Miller (1983):</strong> fitted to the 1983 Metropolitan Life tables.</li>
      <li><strong>Hamwi (1964):</strong> a quick clinical rule for estimating weight from height.</li>
    </ul>
    <p class="er-note">They agree closely because the height&ndash;weight tables behind them agree; Pai and Paloucek conclude that any one of them may be used (<a href="https://pubmed.ncbi.nlm.nih.gov/10981254/" target="_blank" rel="noopener">2000</a>).</p></div>`;

  const others = ['small', 'medium', 'large'].filter(f => f !== frame).map(f => [f, mediumAvg * (f === 'small' ? 0.9 : f === 'large' ? 1.1 : 1)]);
  html += `<div class="er-section"><h2>Frame size</h2>
    <p class="er-note">You chose a <strong>${frame} frame</strong> (${frame === 'small' ? '10% below the medium-frame average' : frame === 'large' ? '10% above the medium-frame average' : 'no adjustment'}). With a ${others[0][0]} frame the average would be ${W(others[0][1])}; with a ${others[1][0]} frame, ${W(others[1][1])}.</p>
    <p class="er-note">To estimate your frame from your wrist size, see <a href="#frame-size">body frame size</a>.</p></div>`;

  ext.innerHTML = html;
}

/* ===== DISPLAY: LBM RESULTS ===== */

function displayLBMResults(type, formulas, fatMass, bodyFatPct, totalWeightKg, weightLbs, heightInches, sex) {
  const section = document.getElementById(type + '-results');
  if (!section) return;

  const lbm = formulas.boer;
  const M = kg => cmbFmtKg(kg, 1), Malt = kg => cmbFmtKgAlt(kg, 1);
  const lbmEl = document.getElementById(type + '-lbm');
  const fatEl = document.getElementById(type + '-fat-mass');
  const bfEl = document.getElementById(type + '-body-fat');

  // The page's donut chart reads the kilogram values from data-kg (CMB-011).
  if (lbmEl) { lbmEl.innerHTML = M(lbm) + ' <span class="result-item-alt">(' + Malt(lbm) + ')</span>'; lbmEl.dataset.kg = lbm.toFixed(2); }
  if (fatEl) { fatEl.innerHTML = M(fatMass) + ' <span class="result-item-alt">(' + Malt(fatMass) + ')</span>'; fatEl.dataset.kg = fatMass.toFixed(2); }
  if (bfEl) bfEl.textContent = bodyFatPct.toFixed(1) + '%';

  section.classList.add('visible');

  const ext = getExtendedContainer(type);
  if (!ext) return;

  const heightCm = inchesToCm(heightInches);
  const ffmi = lbm / Math.pow(heightCm / 100, 2);
  const adjFfmi = ffmi + 6.1 * (1.8 - heightCm / 100);
  const fatMassJames = totalWeightKg - formulas.james;
  const bfJames = (fatMassJames / totalWeightKg) * 100;
  const fatMassHume = totalWeightKg - formulas.hume;
  const bfHume = (fatMassHume / totalWeightKg) * 100;

  let html = '';

  // Formula comparison (Boer is the one shown above)
  html += `<div class="er-section"><h2>Formula comparison</h2>
    <p class="er-note">Three published formulas estimate lean body mass from height, weight and sex; the results above use Boer.</p>
    <table class="er-table"><thead><tr><th>Formula</th><th class="er-num">Lean mass</th><th class="er-num">Body fat</th></tr></thead><tbody>
      <tr class="er-active"><td>Boer (1984)</td><td class="er-num">${M(formulas.boer)}<span class="er-alt">${Malt(formulas.boer)}</span></td><td class="er-num">${bodyFatPct.toFixed(1)}%</td></tr>
      <tr><td>James (1976)</td><td class="er-num">${M(formulas.james)}<span class="er-alt">${Malt(formulas.james)}</span></td><td class="er-num">${bfJames.toFixed(1)}%</td></tr>
      <tr><td>Hume (1966)</td><td class="er-num">${M(formulas.hume)}<span class="er-alt">${Malt(formulas.hume)}</span></td><td class="er-num">${bfHume.toFixed(1)}%</td></tr>
    </tbody></table></div>`;

  // The remaining numbers
  html += `<div class="er-section"><h2>More numbers</h2>
    <div class="er-metrics er-metrics-2">
      <div class="er-metric"><div class="er-metric-label">FFMI</div><div class="er-metric-value">${ffmi.toFixed(1)}</div><div class="er-metric-sub">Fat-free mass index, kg/m&sup2;</div></div>
      <div class="er-metric"><div class="er-metric-label">Adjusted FFMI</div><div class="er-metric-value">${adjFfmi.toFixed(1)}</div><div class="er-metric-sub">Scaled to a height of 1.8 m</div></div>
    </div>
    <p class="er-note" style="margin-top:0.75rem;">FFMI is lean mass divided by height squared, so it can be compared between people of different heights.</p></div>`;

  html += `<div class="er-section"><h2>How your body fat compares</h2>
    <p class="er-note">Compare your estimate with what US adults your age actually measure on CDC body scans, and with the provisional healthy ranges, on the <a href="/body-fat-percentage-chart/">body fat percentage chart</a>. For a direct estimate from tape measurements or skinfolds, use the <a href="/body-fat-calculator/">body fat calculator</a>.</p></div>`;

  ext.innerHTML = html;
}

/* ===== DISPLAY: NEW BMI RESULTS ===== */

function displayNewBMIResults(type, traditionalBMI, newBMI, diff, traditionalCat, newCat, healthyRange, heightInches, weightLbs) {
  traditionalBMI = round1(traditionalBMI); newBMI = round1(newBMI);
  const section = document.getElementById(type + '-results');
  if (!section) return;

  const bmiValueEl = document.getElementById(type + '-bmi-value');
  const bmiCategoryEl = document.getElementById(type + '-bmi-category');
  const bmiRangeEl = document.getElementById(type + '-bmi-range');
  const resultCard = document.getElementById(type + '-result-card');
  if (bmiValueEl) bmiValueEl.textContent = newBMI.toFixed(1);
  if (bmiCategoryEl) bmiCategoryEl.textContent = newCat.category;
  const cmpEl = document.getElementById(type + '-bmi-value-compare');
  if (cmpEl) cmpEl.textContent = newBMI.toFixed(1);
  if (bmiRangeEl) bmiRangeEl.textContent = 'BMI range: ' + newCat.range;
  if (resultCard) { resultCard.className = 'bmi-result-card ' + newCat.class; if (bmiValueEl) bmiValueEl.className = 'bmi-value ' + newCat.class; }
  const marker = document.getElementById(type + '-scale-marker');
  if (marker) marker.style.left = getScalePosition(newBMI) + '%';
  const tradValueEl = document.getElementById(type + '-traditional-value');
  const tradCatEl = document.getElementById(type + '-traditional-category');
  if (tradValueEl) tradValueEl.textContent = traditionalBMI.toFixed(1);
  if (tradCatEl) tradCatEl.textContent = traditionalCat.category;
  const signed = d => (d > 0 ? '+' : d < 0 ? '−' : '') + Math.abs(d).toFixed(1);
  const diffEl = document.getElementById(type + '-diff');
  if (diffEl) diffEl.textContent = signed(diff);
  const catChangeEl = document.getElementById(type + '-category-change');
  if (catChangeEl) {
    catChangeEl.textContent = traditionalCat.category === newCat.category
      ? 'Same category with both formulas'
      : traditionalCat.category + ' with the traditional formula, ' + newCat.category + ' with the new one';
  }
  const healthyMinEl = document.getElementById(type + '-healthy-min');
  const healthyMaxEl = document.getElementById(type + '-healthy-max');
  if (healthyMinEl) healthyMinEl.innerHTML = fmtBound(healthyRange, 'min') + ' <span class="result-item-alt">(' + fmtBound(healthyRange, 'min', true) + ')</span>';
  if (healthyMaxEl) healthyMaxEl.innerHTML = fmtBound(healthyRange, 'max') + ' <span class="result-item-alt">(' + fmtBound(healthyRange, 'max', true) + ')</span>';
  const weightDiffEl = document.getElementById(type + '-weight-diff');
  if (weightDiffEl) weightDiffEl.textContent = healthyRangeText(healthyRange, weightLbs);
  section.classList.add('visible');

  const ext = getExtendedContainer(type);
  if (!ext) return;

  const weightKg = lbsToKg(weightLbs);
  let html = '';

  // 1. Which number to use, in words first
  const gap = Math.abs(diff).toFixed(1);
  const verdict = Math.abs(diff) < 0.5
    ? `At <strong>${fmtH(heightInches)}</strong>, both formulas give nearly the same result: <strong>${newBMI.toFixed(1)}</strong> with the new formula and ${traditionalBMI.toFixed(1)} with the traditional one.`
    : `At <strong>${fmtH(heightInches)}</strong>, the new formula gives <strong>${newBMI.toFixed(1)}</strong>, ${gap} ${gap === '1.0' ? 'point' : 'points'} ${diff > 0 ? 'higher' : 'lower'} than the traditional ${traditionalBMI.toFixed(1)}. Its author, Nick Trefethen, argued that the traditional formula ${diff > 0 ? 'understates BMI for shorter people' : 'overstates BMI for taller people'}.`;
  html += `<div class="er-section"><h2>Which number to use</h2><div class="er-summary"><p>${verdict}</p><p class="er-summary-note">WHO and CDC define the BMI categories on the traditional formula, so that is the number doctors and health guidelines use. Trefethen proposed the new formula in 2013.</p></div></div>`;

  // 2. Side-by-side classification
  html += `<div class="er-section"><h2>Classification comparison</h2>
    <table class="er-table"><thead><tr><td></td><th class="er-num">Traditional</th><th class="er-num">New (Trefethen)</th></tr></thead><tbody>
      <tr><td>Formula</td><td class="er-num">kg / m&sup2;</td><td class="er-num">1.3 &times; kg / m<sup>2.5</sup></td></tr>
      <tr><td>Your BMI</td><td class="er-num" style="font-weight:700;color:${catColor(traditionalCat.class)};">${traditionalBMI.toFixed(1)}</td><td class="er-num" style="font-weight:700;color:${catColor(newCat.class)};">${newBMI.toFixed(1)}</td></tr>
      <tr><td>Category</td><td class="er-num">${traditionalCat.category}</td><td class="er-num">${newCat.category}</td></tr>
      <tr><td>BMI Prime</td><td class="er-num">${bmiPrime(traditionalBMI)}</td><td class="er-num">${bmiPrime(newBMI)}</td></tr>
    </tbody></table></div>`;

  // 3. Height divergence table
  const heights = [60, 63, 65, 67, 69, 71, 73, 75, 78];
  let divRows = '';
  heights.forEach(h => {
    const hM = inchesToCm(h) / 100;
    const tBmi = round1(calculateBMI(weightLbs, h));
    const nBmi = round1(1.3 * weightKg / Math.pow(hM, 2.5));
    const d = round1(nBmi - tBmi);
    const isCurrent = Math.abs(h - heightInches) < 1.5;
    divRows += `<tr${isCurrent ? ' class="er-active"' : ''}><td class="er-num">${fmtH(h)}<span class="er-alt">${fmtHalt(h)}</span></td><td class="er-num">${tBmi.toFixed(1)}</td><td class="er-num">${nBmi.toFixed(1)}</td><td class="er-num">${signed(d)}</td></tr>`;
  });
  html += `<div class="er-section"><h2>How height changes the difference</h2>
    <p class="er-note">The same weight (${fmtW(weightLbs)}) at different heights.</p>
    <table class="er-table"><thead><tr><th class="er-num">Height</th><th class="er-num">Traditional</th><th class="er-num">New</th><th class="er-num">Difference</th></tr></thead><tbody>${divRows}</tbody></table>
    <p class="er-note" style="margin-top:0.75rem;">The new formula gives a higher BMI below about 1.69 m (5&prime;6.5&Prime;) and a lower one above it; at that height the two agree.</p></div>`;

  // 4. The remaining numbers
  html += `<div class="er-section"><h2>More numbers</h2>
    <div class="er-metrics er-metrics-4">
      <div class="er-metric"><div class="er-metric-label">Weight</div><div class="er-metric-value">${fmtW(weightLbs)}</div><div class="er-metric-sub">${fmtWalt(weightLbs)}</div></div>
      <div class="er-metric"><div class="er-metric-label">Height</div><div class="er-metric-value">${fmtH(heightInches)}</div><div class="er-metric-sub">${fmtHalt(heightInches)}</div></div>
      <div class="er-metric"><div class="er-metric-label">BMI Prime</div><div class="er-metric-value">${bmiPrime(newBMI)}</div><div class="er-metric-sub">New formula</div></div>
      <div class="er-metric"><div class="er-metric-label">BMI Prime</div><div class="er-metric-value">${bmiPrime(traditionalBMI)}</div><div class="er-metric-sub">Traditional formula</div></div>
    </div></div>`;

  ext.innerHTML = html;
}

/* ===== FAQ & NAV ===== */

function setupFAQ() {
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const wasOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
      if (!wasOpen) item.classList.add('open');
    });
  });
}

function setupMobileNav() {
  const toggle = document.querySelector('.nav-toggle');
  const mobileNav = document.querySelector('.nav-mobile');
  if (toggle && mobileNav) {
    toggle.addEventListener('click', () => mobileNav.classList.toggle('active'));
  }
}
