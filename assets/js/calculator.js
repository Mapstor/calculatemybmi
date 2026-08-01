/* BMI CALCULATOR - ENHANCED JAVASCRIPT */

document.addEventListener('DOMContentLoaded', init);

function init() {
  setupTabs();
  setupCalculateButtons();
  setupUnitToggles();
  setupFAQ();
  setupMobileNav();
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
  return (weightLbs / (heightInches * heightInches)) * 703;
}

function getBMICategory(bmi) {
  if (bmi < 16) return { category: 'Severe Thinness', class: 'underweight', range: 'Below 16', risk: 'Very High' };
  if (bmi < 17) return { category: 'Moderate Thinness', class: 'underweight', range: '16 - 16.9', risk: 'High' };
  if (bmi < 18.5) return { category: 'Underweight', class: 'underweight', range: '17 - 18.4', risk: 'Moderate' };
  if (bmi < 25) return { category: 'Normal', class: 'normal', range: '18.5 - 24.9', risk: 'Low' };
  if (bmi < 30) return { category: 'Overweight', class: 'overweight', range: '25 - 29.9', risk: 'Moderate' };
  if (bmi < 35) return { category: 'Obese (Class I)', class: 'obese', range: '30 - 34.9', risk: 'High' };
  if (bmi < 40) return { category: 'Obese (Class II)', class: 'obese', range: '35 - 39.9', risk: 'Very High' };
  return { category: 'Obese (Class III)', class: 'obese-severe', range: '40+', risk: 'Extremely High' };
}

function getHealthyWeightRange(heightInches) {
  const minWeight = (18.5 * heightInches * heightInches) / 703;
  const maxWeight = (24.9 * heightInches * heightInches) / 703;
  return { min: minWeight, max: maxWeight };
}

function getWeightForBMI(targetBMI, heightInches) {
  return (targetBMI * heightInches * heightInches) / 703;
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
  const ft = Math.floor(inches / 12);
  const inn = Math.round(inches % 12);
  return ft + "'" + inn + '"';
}

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

function riskColor(level) {
  const m = { 'Low': '#22c55e', 'Moderate': '#f59e0b', 'High': '#f97316', 'Very High': '#ef4444', 'Extremely High': '#991b1b' };
  return m[level] || '#6b7280';
}

function catColor(cls) {
  const m = { underweight: '#3b82f6', normal: '#22c55e', overweight: '#f59e0b', obese: '#ef4444', 'obese-severe': '#991b1b' };
  return m[cls] || '#6b7280';
}

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
  const idealMin = (19 * heightInches * heightInches) / 703;
  const idealMax = (24 * heightInches * heightInches) / 703;
  displayBMIResults('women', bmi, category, healthyRange, heightInches, weightLbs, { idealMin, idealMax, sex: 'female' });
}

function calculateMen() {
  const panel = document.getElementById('panel-men');
  const heightInches = getHeightInches(panel);
  const weightLbs = getWeightPounds(panel);
  const bmi = calculateBMI(weightLbs, heightInches);
  if (bmi <= 0) return;
  const category = getBMICategory(bmi);
  const healthyRange = getHealthyWeightRange(heightInches);
  const idealMin = (20 * heightInches * heightInches) / 703;
  const idealMax = (25 * heightInches * heightInches) / 703;
  displayBMIResults('men', bmi, category, healthyRange, heightInches, weightLbs, { idealMin, idealMax, sex: 'male' });
}

function calculateByAge() {
  const panel = document.getElementById('panel-age');
  const heightInches = getHeightInches(panel);
  const weightLbs = getWeightPounds(panel);
  const age = parseInt(panel.querySelector('.age-input')?.value) || 30;
  const bmi = calculateBMI(weightLbs, heightInches);
  if (bmi <= 0) return;
  let adjustedRange;
  if (age < 65) adjustedRange = '18.5 - 24.9 (WHO adult range)';
  else adjustedRange = '18.5 - 24.9 (WHO) &middot; 23 - 33 lowest-mortality plateau in Winter 2014 meta-analysis';
  const category = getBMICategory(bmi);
  const healthyRange = getHealthyWeightRange(heightInches);
  displayBMIResults('age', bmi, category, healthyRange, heightInches, weightLbs, { adjustedRange, age });
}

function calculateKids() {
  const panel = document.getElementById('panel-kids');
  const heightInches = getHeightInches(panel);
  const weightLbs = getWeightPounds(panel);
  const age = parseInt(panel.querySelector('.age-input')?.value) || 10;
  const sex = panel.querySelector('.sex-select')?.value || 'female';
  const bmi = calculateBMI(weightLbs, heightInches);
  if (bmi <= 0) return;
  let percentileCategory;
  if (bmi < 14) percentileCategory = { category: 'Underweight', class: 'underweight', note: 'Below 5th percentile' };
  else if (bmi < 22) percentileCategory = { category: 'Healthy Weight', class: 'normal', note: '5th - 84th percentile' };
  else if (bmi < 27) percentileCategory = { category: 'Overweight', class: 'overweight', note: '85th - 94th percentile' };
  else percentileCategory = { category: 'Obese', class: 'obese', note: '95th percentile or higher' };
  displayKidsResults('kids', bmi, percentileCategory, age, sex, heightInches, weightLbs);
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
  const bmiMin = getWeightForBMI(18.5, heightInches) / 2.20462;
  const bmiMax = getWeightForBMI(24.9, heightInches) / 2.20462;
  displayIdealWeightResults('ideal', { devine, robinson, miller, hamwi, bmiMin, bmiMax }, heightInches, sex, frame);
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
  const diff = newBMI - traditionalBMI;
  const traditionalCat = getBMICategory(traditionalBMI);
  const newCat = getBMICategory(newBMI);
  const healthyRange = getHealthyWeightRange(heightInches);
  displayNewBMIResults('newbmi', traditionalBMI, newBMI, diff, traditionalCat, newCat, healthyRange, heightInches, weightLbs);
}

/* ===== SHARED HTML GENERATORS ===== */

function genClassificationTable(bmi) {
  const cats = [
    ['Severe Thinness', '< 16', '#3b82f6'],
    ['Moderate Thinness', '16 - 16.9', '#60a5fa'],
    ['Underweight', '17 - 18.4', '#93c5fd'],
    ['Normal weight', '18.5 - 24.9', '#22c55e'],
    ['Overweight', '25 - 29.9', '#f59e0b'],
    ['Obese Class I', '30 - 34.9', '#f97316'],
    ['Obese Class II', '35 - 39.9', '#ef4444'],
    ['Obese Class III', '40+', '#991b1b']
  ];
  const thresholds = [0, 16, 17, 18.5, 25, 30, 35, 40, 100];
  let activeIdx = 0;
  for (let i = 0; i < thresholds.length - 1; i++) {
    if (bmi >= thresholds[i] && bmi < thresholds[i + 1]) { activeIdx = i; break; }
  }
  if (bmi >= 40) activeIdx = 7;
  let rows = '';
  cats.forEach((c, i) => {
    const active = i === activeIdx;
    rows += `<tr class="${active ? 'er-active' : ''}"><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${c[2]};margin-right:6px;vertical-align:middle;"></span>${c[0]}</td><td>${c[1]}</td><td style="text-align:center;">${active ? '<strong style="color:var(--primary-dark);">&#10140; You (' + bmi.toFixed(1) + ')</strong>' : ''}</td></tr>`;
  });
  return `<table class="er-table"><thead><tr><th>Category</th><th>BMI Range</th><th style="text-align:center;">Your Status</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function genKeyMetrics(bmi, heightInches, weightLbs, healthyRange, extra) {
  const weightKg = lbsToKg(weightLbs);
  const heightCm = inchesToCm(heightInches);
  const bmiPrime = (bmi / 25).toFixed(2);
  const ponderal = (weightKg / Math.pow(heightCm / 100, 3)).toFixed(1);
  let metrics = `
    <div class="er-metric"><div class="er-metric-label">BMI</div><div class="er-metric-value" style="color:${catColor(getBMICategory(bmi).class)};">${bmi.toFixed(1)}</div></div>
    <div class="er-metric"><div class="er-metric-label">BMI Prime</div><div class="er-metric-value">${bmiPrime}</div><div class="er-metric-sub">${bmiPrime < 1 ? 'Below upper normal' : 'Above upper normal'}</div></div>
    <div class="er-metric"><div class="er-metric-label">Ponderal Index</div><div class="er-metric-value">${ponderal}</div><div class="er-metric-sub">kg/m&sup3; (normal 11-15)</div></div>
    <div class="er-metric"><div class="er-metric-label">Weight</div><div class="er-metric-value">${Math.round(weightLbs)} lbs</div><div class="er-metric-sub">${weightKg.toFixed(1)} kg</div></div>
    <div class="er-metric"><div class="er-metric-label">Height</div><div class="er-metric-value">${heightToFtIn(heightInches)}</div><div class="er-metric-sub">${Math.round(heightCm)} cm</div></div>
    <div class="er-metric"><div class="er-metric-label">Healthy Range</div><div class="er-metric-value">${Math.round(healthyRange.min)}-${Math.round(healthyRange.max)}</div><div class="er-metric-sub">lbs (${lbsToKg(healthyRange.min).toFixed(0)}-${lbsToKg(healthyRange.max).toFixed(0)} kg)</div></div>`;
  return `<div class="er-metrics">${metrics}</div>`;
}

function genWeightMilestones(bmi, heightInches, weightLbs) {
  const targets = [
    { label: 'Underweight threshold', bmiVal: 18.5 },
    { label: 'Normal low end', bmiVal: 20 },
    { label: 'Normal midpoint', bmiVal: 22 },
    { label: 'Normal upper end', bmiVal: 24.9 },
    { label: 'Overweight threshold', bmiVal: 25 },
    { label: 'Obese threshold', bmiVal: 30 },
    { label: 'Obese Class II', bmiVal: 35 },
  ];
  let rows = '';
  targets.forEach(t => {
    const w = getWeightForBMI(t.bmiVal, heightInches);
    const diff = w - weightLbs;
    const diffStr = diff > 0 ? '+' + Math.round(diff) + ' lbs' : diff < 0 ? Math.round(diff) + ' lbs' : '—';
    const color = Math.abs(diff) < 1 ? 'var(--primary-dark)' : diff > 0 ? 'var(--gray-600)' : 'var(--gray-600)';
    const isCurrent = Math.abs(bmi - t.bmiVal) < 2.5;
    rows += `<tr${isCurrent ? ' style="background:var(--gray-50);"' : ''}><td>${t.label}</td><td style="text-align:center;font-weight:600;">${t.bmiVal}</td><td style="text-align:center;">${Math.round(w)} lbs <span style="color:var(--gray-500);font-size:0.75rem;">(${lbsToKg(w).toFixed(1)} kg)</span></td><td style="text-align:center;color:${color};font-weight:600;">${diffStr}</td></tr>`;
  });
  return `<table class="er-table"><thead><tr><th>Milestone</th><th style="text-align:center;">BMI</th><th style="text-align:center;">Weight Needed</th><th style="text-align:center;">Change</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function genWhatIf(bmi, heightInches, weightLbs) {
  const changes = [-20, -15, -10, -5, 0, 5, 10, 15, 20];
  let rows = '';
  changes.forEach(c => {
    const newW = weightLbs + c;
    if (newW <= 0) return;
    const newBmi = calculateBMI(newW, heightInches);
    const cat = getBMICategory(newBmi);
    const isCurrent = c === 0;
    rows += `<tr${isCurrent ? ' class="er-active"' : ''}><td style="text-align:center;font-weight:${isCurrent ? '700' : '400'};">${c === 0 ? 'Current' : (c > 0 ? '+' + c : c) + ' lbs'}</td><td style="text-align:center;">${Math.round(newW)} lbs</td><td style="text-align:center;font-weight:600;color:${catColor(cat.class)};">${newBmi.toFixed(1)}</td><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${catColor(cat.class)};margin-right:4px;vertical-align:middle;"></span>${cat.category}</td></tr>`;
  });
  return `<table class="er-table"><thead><tr><th style="text-align:center;">Change</th><th style="text-align:center;">Weight</th><th style="text-align:center;">BMI</th><th>Category</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function genHealthRisks(bmi) {
  const risks = [
    { name: 'Type 2 Diabetes', low: 25, high: 30 },
    { name: 'Heart Disease', low: 25, high: 30 },
    { name: 'High Blood Pressure', low: 25, high: 30 },
    { name: 'Sleep Apnea', low: 27, high: 35 },
    { name: 'Joint Problems', low: 25, high: 30 },
    { name: 'Certain Cancers', low: 30, high: 35 },
    { name: 'Stroke', low: 25, high: 30 },
    { name: 'Nutritional Deficiency', low: 0, high: 18.5 },
  ];
  let html = '';
  risks.forEach(r => {
    let level, color;
    if (r.name === 'Nutritional Deficiency') {
      if (bmi < 16) { level = 'High'; color = '#ef4444'; }
      else if (bmi < 18.5) { level = 'Moderate'; color = '#f59e0b'; }
      else { level = 'Low'; color = '#22c55e'; }
    } else {
      if (bmi >= r.high) { level = 'High'; color = '#ef4444'; }
      else if (bmi >= r.low) { level = 'Moderate'; color = '#f59e0b'; }
      else if (bmi < 18.5) { level = 'Low-Mod'; color = '#60a5fa'; }
      else { level = 'Low'; color = '#22c55e'; }
    }
    html += `<div class="er-risk"><div class="er-risk-dot" style="background:${color};"></div><span style="flex:1;">${r.name}</span><span class="er-badge" style="background:${color}22;color:${color};">${level}</span></div>`;
  });
  return `<div class="er-risk-grid">${html}</div>`;
}

function genWeightProgressBar(weightLbs, healthyRange) {
  const min = healthyRange.min * 0.75;
  const max = healthyRange.max * 1.35;
  const range = max - min;
  const pos = Math.max(0, Math.min(100, ((weightLbs - min) / range) * 100));
  const hMinPos = ((healthyRange.min - min) / range) * 100;
  const hMaxPos = ((healthyRange.max - min) / range) * 100;
  return `<div style="position:relative;height:32px;background:var(--gray-100);border-radius:16px;margin:0.75rem 0;overflow:visible;">
    <div style="position:absolute;left:${hMinPos}%;width:${hMaxPos - hMinPos}%;height:100%;background:#dcfce7;border-radius:16px;"></div>
    <div style="position:absolute;left:${pos}%;top:-4px;width:20px;height:40px;background:var(--primary-dark);border-radius:10px;transform:translateX(-50%);border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.2);"></div>
    <div style="position:absolute;left:${hMinPos}%;bottom:-20px;font-size:0.6875rem;color:var(--gray-500);transform:translateX(-50%);">${Math.round(healthyRange.min)}</div>
    <div style="position:absolute;left:${hMaxPos}%;bottom:-20px;font-size:0.6875rem;color:var(--gray-500);transform:translateX(-50%);">${Math.round(healthyRange.max)}</div>
    <div style="position:absolute;left:${pos}%;top:-22px;font-size:0.75rem;font-weight:700;color:var(--primary-dark);transform:translateX(-50%);">${Math.round(weightLbs)} lbs</div>
  </div>`;
}

function genSummary(bmi, category, weightLbs, healthyRange, extra) {
  const weightKg = lbsToKg(weightLbs);
  let text = '';
  if (category.class === 'normal') {
    const margin = Math.round(healthyRange.max - weightLbs);
    text = `Your BMI of <strong>${bmi.toFixed(1)}</strong> places you in the <strong>normal weight</strong> category. You are ${margin > 0 ? margin + ' lbs below the overweight threshold' : 'at the upper end of normal'}. Maintain your weight through balanced nutrition and regular physical activity. A BMI in this range is associated with the lowest risk of weight-related health complications.`;
  } else if (category.class === 'underweight') {
    const gain = Math.round(healthyRange.min - weightLbs);
    text = `Your BMI of <strong>${bmi.toFixed(1)}</strong> suggests you are <strong>underweight</strong>. You would need to gain approximately <strong>${gain} lbs (${lbsToKg(gain).toFixed(1)} kg)</strong> to reach the healthy range. Being underweight can lead to nutritional deficiencies, weakened immunity, and bone loss. Consider consulting a healthcare provider or dietitian.`;
  } else if (category.class === 'overweight') {
    const lose = Math.round(weightLbs - healthyRange.max);
    text = `Your BMI of <strong>${bmi.toFixed(1)}</strong> places you in the <strong>overweight</strong> category. Losing approximately <strong>${lose} lbs (${lbsToKg(lose).toFixed(1)} kg)</strong> would bring you into the healthy range. Even a 5-10% weight reduction can significantly improve blood pressure, cholesterol, and blood sugar levels. Focus on sustainable lifestyle changes rather than crash diets.`;
  } else {
    const lose = Math.round(weightLbs - healthyRange.max);
    text = `Your BMI of <strong>${bmi.toFixed(1)}</strong> places you in the <strong>${category.category}</strong> category. To reach the healthy weight range, a reduction of approximately <strong>${lose} lbs (${lbsToKg(lose).toFixed(1)} kg)</strong> would be needed. This BMI level is associated with increased health risks. Please consult with a healthcare provider who can create a personalized plan considering your full health picture.`;
  }
  if (extra?.sex === 'female') {
    text += ' <em>Note for women: body fat distribution, hormonal cycles, and life stages (pregnancy, menopause) all affect how BMI translates to actual health risk.</em>';
  }
  if (extra?.sex === 'male') {
    text += ' <em>Note for men: if you carry significant muscle mass, your BMI may overestimate body fat. Consider waist circumference (risk increases above 40 inches / 102 cm) as an additional measure.</em>';
  }
  if (extra?.age && extra.age >= 65) {
    text += ` <em>Note for adults 65+: WHO cut-offs still apply, but an observational meta-analysis of ~200,000 older adults (Winter 2014, Am J Clin Nutr) found the lowest all-cause mortality across BMI 23-33 in this age group. Discuss what applies to you with your doctor.</em>`;
  }
  return `<div class="er-summary">${text}</div>`;
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
  if (bmiValueEl) bmiValueEl.textContent = bmi.toFixed(1);
  if (bmiCategoryEl) bmiCategoryEl.textContent = category.category;
  if (bmiRangeEl) bmiRangeEl.textContent = 'BMI Range: ' + category.range;
  if (resultCard) {
    resultCard.className = 'bmi-result-card ' + category.class;
    if (bmiValueEl) bmiValueEl.className = 'bmi-value ' + category.class;
  }
  const marker = document.getElementById(type + '-scale-marker');
  if (marker) marker.style.left = getScalePosition(bmi) + '%';
  const healthyMinEl = document.getElementById(type + '-healthy-min');
  const healthyMaxEl = document.getElementById(type + '-healthy-max');
  if (healthyMinEl) healthyMinEl.textContent = Math.round(healthyRange.min) + ' lbs (' + Math.round(lbsToKg(healthyRange.min)) + ' kg)';
  if (healthyMaxEl) healthyMaxEl.textContent = Math.round(healthyRange.max) + ' lbs (' + Math.round(lbsToKg(healthyRange.max)) + ' kg)';
  const weightDiffEl = document.getElementById(type + '-weight-diff');
  if (weightDiffEl) {
    if (weightLbs < healthyRange.min) {
      var diff = Math.round(healthyRange.min - weightLbs);
      weightDiffEl.textContent = 'Gain ' + diff + ' lbs (' + Math.round(lbsToKg(diff)) + ' kg) to reach healthy range';
    }
    else if (weightLbs > healthyRange.max) {
      var diff = Math.round(weightLbs - healthyRange.max);
      weightDiffEl.textContent = 'Lose ' + diff + ' lbs (' + Math.round(lbsToKg(diff)) + ' kg) to reach healthy range';
    }
    else weightDiffEl.textContent = 'You are within the healthy weight range';
  }
  if (extra.adjustedRange) {
    const adjustedEl = document.getElementById(type + '-adjusted-range');
    if (adjustedEl) adjustedEl.textContent = extra.adjustedRange;
  }

  section.classList.add('visible');

  // === EXTENDED RESULTS ===
  const ext = getExtendedContainer(type);
  if (!ext) return;

  let html = '';

  // 1. Key Metrics
  html += `<div class="er-section"><h3><span class="er-icon">&#128202;</span> Your Key Metrics</h3>${genKeyMetrics(bmi, heightInches, weightLbs, healthyRange, extra)}</div>`;

  // 2. Weight position bar
  html += `<div class="er-section"><h3><span class="er-icon">&#127919;</span> Where Your Weight Falls</h3><p style="font-size:0.8125rem;color:var(--gray-500);margin:0 0 0.5rem;">Green zone = healthy weight range for your height</p>${genWeightProgressBar(weightLbs, healthyRange)}<div style="height:24px;"></div></div>`;

  // 3. Classification table
  html += `<div class="er-section"><h3><span class="er-icon">&#128203;</span> BMI Classification</h3>${genClassificationTable(bmi)}</div>`;

  // 4. Weight milestones
  html += `<div class="er-section"><h3><span class="er-icon">&#127947;</span> Weight Milestones for Your Height</h3><p style="font-size:0.8125rem;color:var(--gray-500);margin:0 0 0.5rem;">How much weight change is needed to reach each BMI threshold at ${heightToFtIn(heightInches)} (${Math.round(inchesToCm(heightInches))} cm)</p>${genWeightMilestones(bmi, heightInches, weightLbs)}</div>`;

  // 5. What-if scenarios
  html += `<div class="er-section"><h3><span class="er-icon">&#128161;</span> What-If Weight Scenarios</h3><p style="font-size:0.8125rem;color:var(--gray-500);margin:0 0 0.5rem;">See how gaining or losing weight would change your BMI and category</p>${genWhatIf(bmi, heightInches, weightLbs)}</div>`;

  // 6. Health risks
  html += `<div class="er-section"><h3><span class="er-icon">&#9829;</span> Health Risk Assessment</h3><p style="font-size:0.8125rem;color:var(--gray-500);margin:0 0 0.75rem;">Estimated relative risk based on BMI category (not a medical diagnosis)</p>${genHealthRisks(bmi)}</div>`;

  // 7. Sex-specific sections
  if (extra.sex === 'female') {
    const bf = (1.20 * bmi + 0.23 * 30 - 10.8 * 0 - 5.4).toFixed(1);
    let bfCat = 'Athletic';
    const bfN = parseFloat(bf);
    if (bfN < 14) bfCat = 'Essential Fat';
    else if (bfN < 21) bfCat = 'Athletic';
    else if (bfN < 25) bfCat = 'Fitness';
    else if (bfN < 32) bfCat = 'Average';
    else bfCat = 'Above Average';
    html += `<div class="er-section"><h3><span class="er-icon">&#9792;</span> Women&rsquo;s Health Insights</h3>
      <div class="er-metrics" style="margin-bottom:1rem;">
        <div class="er-metric"><div class="er-metric-label">Est. Body Fat</div><div class="er-metric-value">${bf}%</div><div class="er-metric-sub">${bfCat}</div></div>
        <div class="er-metric"><div class="er-metric-label">Ideal BMI Range</div><div class="er-metric-value">19-24</div><div class="er-metric-sub">Women-specific</div></div>
        <div class="er-metric"><div class="er-metric-label">Ideal Weight</div><div class="er-metric-value">${Math.round(extra.idealMin * 2.20462)}-${Math.round(extra.idealMax * 2.20462)} lbs</div><div class="er-metric-sub">${extra.idealMin?.toFixed(0)}-${extra.idealMax?.toFixed(0)} kg</div></div>
      </div>
      <table class="er-table"><thead><tr><th>Life Stage</th><th>BMI Consideration</th></tr></thead><tbody>
        <tr><td>Reproductive Age (18-44)</td><td>BMI 18.5-24.9 optimal for fertility; underweight or obesity can affect ovulation</td></tr>
        <tr><td>Pregnancy</td><td>Pre-pregnancy BMI determines recommended weight gain (25-35 lbs for normal BMI)</td></tr>
        <tr><td>Postpartum</td><td>Allow 6-12 months for gradual return to pre-pregnancy weight</td></tr>
        <tr><td>Perimenopause (45-55)</td><td>Hormonal changes shift fat to abdomen; waist circumference becomes key metric</td></tr>
        <tr><td>Post-Menopause (55+)</td><td>WHO cut-offs unchanged; resistance training and bone-density care are the actionable levers</td></tr>
      </tbody></table>
      <p style="font-size:0.8125rem;color:var(--gray-500);margin:0.75rem 0 0;">Waist circumference risk: &ge;35 inches (88 cm) indicates increased health risk for women. Menstrual cycle can cause 2-6 lb fluctuations &mdash; weigh at the same cycle point monthly.</p>
    </div>`;
  }

  if (extra.sex === 'male') {
    const bf = (1.20 * bmi + 0.23 * 30 - 10.8 * 1 - 5.4).toFixed(1);
    let bfCat = 'Athletic';
    const bfN = parseFloat(bf);
    if (bfN < 6) bfCat = 'Essential Fat';
    else if (bfN < 14) bfCat = 'Athletic';
    else if (bfN < 18) bfCat = 'Fitness';
    else if (bfN < 25) bfCat = 'Average';
    else bfCat = 'Above Average';
    html += `<div class="er-section"><h3><span class="er-icon">&#9794;</span> Men&rsquo;s Health Insights</h3>
      <div class="er-metrics" style="margin-bottom:1rem;">
        <div class="er-metric"><div class="er-metric-label">Est. Body Fat</div><div class="er-metric-value">${bf}%</div><div class="er-metric-sub">${bfCat}</div></div>
        <div class="er-metric"><div class="er-metric-label">Ideal BMI Range</div><div class="er-metric-value">20-25</div><div class="er-metric-sub">Men-specific</div></div>
        <div class="er-metric"><div class="er-metric-label">Ideal Weight</div><div class="er-metric-value">${Math.round(extra.idealMin * 2.20462)}-${Math.round(extra.idealMax * 2.20462)} lbs</div><div class="er-metric-sub">${extra.idealMin?.toFixed(0)}-${extra.idealMax?.toFixed(0)} kg</div></div>
      </div>
      <table class="er-table"><thead><tr><th>Metric</th><th>Low Risk</th><th>Increased Risk</th><th>High Risk</th></tr></thead><tbody>
        <tr><td>Waist Circumference</td><td>&lt; 37&quot; (94 cm)</td><td>37-40&quot; (94-102 cm)</td><td>&gt; 40&quot; (102 cm)</td></tr>
        <tr><td>Waist-to-Hip Ratio</td><td>&lt; 0.90</td><td>0.90-0.99</td><td>&ge; 1.0</td></tr>
        <tr><td>Body Fat %</td><td>8-19%</td><td>20-24%</td><td>&ge; 25%</td></tr>
      </tbody></table>
      <p style="font-size:0.8125rem;color:var(--gray-500);margin:0.75rem 0 0;">Men with significant muscle mass (regular resistance training) may have an elevated BMI despite low body fat. If your waist is under 37&quot;, an &ldquo;overweight&rdquo; BMI is less concerning. Visceral fat (around organs) poses greater risk than subcutaneous fat.</p>
    </div>`;
  }

  // 8. Age-specific section
  if (extra.age) {
    const decades = [
      { range: '20-29', rec: '18.5 - 24.9', note: 'WHO adult range; peak metabolic rate' },
      { range: '30-39', rec: '18.5 - 24.9', note: 'WHO adult range; muscle mass declines gradually' },
      { range: '40-49', rec: '18.5 - 24.9', note: 'WHO adult range; body composition shifts but cut-offs unchanged' },
      { range: '50-59', rec: '18.5 - 24.9', note: 'WHO adult range; strength training helps preserve muscle' },
      { range: '60-64', rec: '18.5 - 24.9', note: 'WHO adult range still applies' },
      { range: '65+', rec: '18.5 - 24.9 (WHO)', note: 'Observational: Winter 2014 meta-analysis found lowest mortality across BMI 23-33 in adults 65+' },
    ];
    let bandIdx = extra.age < 30 ? 0 : extra.age < 40 ? 1 : extra.age < 50 ? 2 : extra.age < 60 ? 3 : extra.age < 65 ? 4 : 5;
    let rows = '';
    decades.forEach((d, i) => {
      rows += `<tr${i === bandIdx ? ' class="er-active"' : ''}><td>${d.range}</td><td style="font-weight:600;">${d.rec}</td><td>${d.note}</td></tr>`;
    });
    html += `<div class="er-section"><h3><span class="er-icon">&#128197;</span> BMI by Age Group</h3>
      <p style="font-size:0.8125rem;color:var(--gray-500);margin:0 0 0.5rem;">WHO does not publish age-adjusted BMI cut-offs. Your age: <strong>${extra.age}</strong></p>
      <table class="er-table"><thead><tr><th>Age Range</th><th>WHO Adult Range</th><th>Notes</th></tr></thead><tbody>${rows}</tbody></table>
      <p style="font-size:0.8125rem;color:var(--gray-500);margin:0.75rem 0 0;">Your range: <strong>${extra.adjustedRange}</strong>. Individual factors such as muscle mass, existing conditions, and fitness level matter more than BMI alone.</p>
    </div>`;
  }

  // 9. Summary
  html += `<div class="er-section"><h3><span class="er-icon">&#128221;</span> Personalized Summary</h3>${genSummary(bmi, category, weightLbs, healthyRange, extra)}</div>`;

  ext.innerHTML = html;
}

/* ===== DISPLAY: KIDS RESULTS ===== */

function displayKidsResults(type, bmi, category, age, sex, heightInches, weightLbs) {
  const section = document.getElementById(type + '-results');
  if (!section) return;

  const bmiValueEl = document.getElementById(type + '-bmi-value');
  const bmiCategoryEl = document.getElementById(type + '-bmi-category');
  const percentileEl = document.getElementById(type + '-percentile-note');
  const resultCard = document.getElementById(type + '-result-card');

  if (bmiValueEl) { bmiValueEl.textContent = bmi.toFixed(1); bmiValueEl.className = 'bmi-value ' + category.class; }
  if (bmiCategoryEl) bmiCategoryEl.textContent = category.category;
  if (percentileEl) percentileEl.textContent = category.note;
  if (resultCard) resultCard.className = 'bmi-result-card ' + category.class;

  section.classList.add('visible');

  const ext = getExtendedContainer(type);
  if (!ext) return;

  const weightKg = lbsToKg(weightLbs);
  const heightCm = inchesToCm(heightInches);
  const sexLabel = sex === 'male' ? 'boys' : 'girls';

  let html = '';

  // Key metrics
  html += `<div class="er-section"><h3><span class="er-icon">&#128202;</span> Key Metrics</h3>
    <div class="er-metrics">
      <div class="er-metric"><div class="er-metric-label">BMI</div><div class="er-metric-value" style="color:${catColor(category.class)};">${bmi.toFixed(1)}</div></div>
      <div class="er-metric"><div class="er-metric-label">Age</div><div class="er-metric-value">${age} years</div><div class="er-metric-sub">${sexLabel}</div></div>
      <div class="er-metric"><div class="er-metric-label">Weight</div><div class="er-metric-value">${Math.round(weightLbs)} lbs</div><div class="er-metric-sub">${weightKg.toFixed(1)} kg</div></div>
      <div class="er-metric"><div class="er-metric-label">Height</div><div class="er-metric-value">${heightToFtIn(heightInches)}</div><div class="er-metric-sub">${Math.round(heightCm)} cm</div></div>
      <div class="er-metric"><div class="er-metric-label">Category</div><div class="er-metric-value">${category.category}</div><div class="er-metric-sub">${category.note}</div></div>
      <div class="er-metric"><div class="er-metric-label">Assessment</div><div class="er-metric-value">Percentile</div><div class="er-metric-sub">Based, not adult BMI</div></div>
    </div></div>`;

  // Percentile categories
  html += `<div class="er-section"><h3><span class="er-icon">&#128203;</span> Pediatric BMI Categories</h3>
    <p style="font-size:0.8125rem;color:var(--gray-500);margin:0 0 0.5rem;">For children and teens, BMI is interpreted using age- and sex-specific percentile charts from the CDC</p>
    <table class="er-table"><thead><tr><th>Category</th><th>Percentile Range</th><th style="text-align:center;">Status</th></tr></thead><tbody>
      <tr${category.class === 'underweight' ? ' class="er-active"' : ''}><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#3b82f6;margin-right:6px;vertical-align:middle;"></span>Underweight</td><td>Below 5th percentile</td><td style="text-align:center;">${category.class === 'underweight' ? '<strong style="color:var(--primary-dark);">&#10140; Current</strong>' : ''}</td></tr>
      <tr${category.class === 'normal' ? ' class="er-active"' : ''}><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#22c55e;margin-right:6px;vertical-align:middle;"></span>Healthy Weight</td><td>5th to 84th percentile</td><td style="text-align:center;">${category.class === 'normal' ? '<strong style="color:var(--primary-dark);">&#10140; Current</strong>' : ''}</td></tr>
      <tr${category.class === 'overweight' ? ' class="er-active"' : ''}><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#f59e0b;margin-right:6px;vertical-align:middle;"></span>Overweight</td><td>85th to 94th percentile</td><td style="text-align:center;">${category.class === 'overweight' ? '<strong style="color:var(--primary-dark);">&#10140; Current</strong>' : ''}</td></tr>
      <tr${category.class === 'obese' ? ' class="er-active"' : ''}><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#ef4444;margin-right:6px;vertical-align:middle;"></span>Obese</td><td>95th percentile and above</td><td style="text-align:center;">${category.class === 'obese' ? '<strong style="color:var(--primary-dark);">&#10140; Current</strong>' : ''}</td></tr>
    </tbody></table></div>`;

  // Age-specific context
  html += `<div class="er-section"><h3><span class="er-icon">&#128106;</span> Understanding Your Child&rsquo;s BMI</h3>
    <table class="er-table"><thead><tr><th>Factor</th><th>Why It Matters</th></tr></thead><tbody>
      <tr><td>Growth Spurts</td><td>Children grow in spurts; a temporary high BMI before a growth spurt is common and often normalizes</td></tr>
      <tr><td>Puberty</td><td>Body composition changes dramatically during puberty; ${sex === 'female' ? 'girls naturally gain more body fat' : 'boys gain more muscle mass'}; timing varies widely</td></tr>
      <tr><td>Physical Activity</td><td>${age < 6 ? 'Toddlers need 3+ hours of active play daily' : age < 13 ? 'Children need 60+ minutes of moderate-to-vigorous activity daily' : 'Teens should aim for 60+ min/day, including muscle-strengthening 3x/week'}</td></tr>
      <tr><td>Nutrition</td><td>${age < 6 ? 'Focus on varied, nutrient-dense foods; avoid restricting fat in children under 2' : 'Focus on whole foods, fruits, vegetables; limit sugary drinks and ultra-processed snacks'}</td></tr>
      <tr><td>Sleep</td><td>${age < 6 ? '10-13 hours per night recommended' : age < 13 ? '9-12 hours per night recommended' : '8-10 hours per night recommended'}; poor sleep is linked to higher BMI in children</td></tr>
    </tbody></table></div>`;

  // Guidance
  let guidance = '';
  if (category.class === 'normal') {
    guidance = `A BMI of <strong>${bmi.toFixed(1)}</strong> at age <strong>${age}</strong> falls in the <strong>healthy weight</strong> range for ${sexLabel}. Continue encouraging balanced meals, regular physical activity, and adequate sleep. Annual checkups with a pediatrician will track growth over time.`;
  } else if (category.class === 'underweight') {
    guidance = `A BMI of <strong>${bmi.toFixed(1)}</strong> at age <strong>${age}</strong> falls <strong>below the 5th percentile</strong> for ${sexLabel}. This may indicate the child is underweight. It could be normal for their growth pattern, or it may warrant attention. Consult your pediatrician to rule out nutritional deficiencies or underlying conditions. Do not put children on restrictive diets without medical guidance.`;
  } else if (category.class === 'overweight') {
    guidance = `A BMI of <strong>${bmi.toFixed(1)}</strong> at age <strong>${age}</strong> falls in the <strong>overweight</strong> range (85th-94th percentile) for ${sexLabel}. Focus on increasing physical activity and improving nutrition quality rather than calorie restriction. Children are still growing, and the goal is often to maintain current weight while height catches up. Consult your pediatrician for personalized guidance.`;
  } else {
    guidance = `A BMI of <strong>${bmi.toFixed(1)}</strong> at age <strong>${age}</strong> falls at or above the <strong>95th percentile</strong> for ${sexLabel}, indicating obesity. Please consult your pediatrician for a comprehensive evaluation. Treatment should focus on family-based lifestyle changes, not restrictive dieting. Early intervention can significantly improve long-term health outcomes.`;
  }
  html += `<div class="er-section"><h3><span class="er-icon">&#128221;</span> Guidance</h3><div class="er-summary">${guidance}<br><br><em>Important: This is a simplified BMI estimate. For accurate pediatric assessment, your child&rsquo;s BMI must be plotted on CDC growth charts by a healthcare provider who can account for their individual growth trajectory.</em></div></div>`;

  ext.innerHTML = html;
}

/* ===== DISPLAY: IDEAL WEIGHT RESULTS ===== */

function displayIdealWeightResults(type, weights, heightInches, sex, frame) {
  const section = document.getElementById(type + '-results');
  if (!section) return;

  const devineEl = document.getElementById(type + '-devine');
  const robinsonEl = document.getElementById(type + '-robinson');
  const millerEl = document.getElementById(type + '-miller');
  const hamwiEl = document.getElementById(type + '-hamwi');
  const bmiRangeEl = document.getElementById(type + '-bmi-range');
  const avgEl = document.getElementById(type + '-average');

  if (devineEl) devineEl.textContent = weights.devine.toFixed(1) + ' kg';
  if (robinsonEl) robinsonEl.textContent = weights.robinson.toFixed(1) + ' kg';
  if (millerEl) millerEl.textContent = weights.miller.toFixed(1) + ' kg';
  if (hamwiEl) hamwiEl.textContent = weights.hamwi.toFixed(1) + ' kg';
  if (bmiRangeEl) bmiRangeEl.textContent = weights.bmiMin.toFixed(1) + ' - ' + weights.bmiMax.toFixed(1) + ' kg';

  const avg = (weights.devine + weights.robinson + weights.miller + weights.hamwi) / 4;
  if (avgEl) avgEl.textContent = avg.toFixed(1) + ' kg (' + kgToLbs(avg).toFixed(1) + ' lbs)';

  section.classList.add('visible');

  const ext = getExtendedContainer(type);
  if (!ext) return;

  const all = [weights.devine, weights.robinson, weights.miller, weights.hamwi];
  const minW = Math.min(...all);
  const maxW = Math.max(...all);
  const heightCm = inchesToCm(heightInches);
  const sexLabel = sex === 'male' ? 'Men' : 'Women';
  const frameLabel = frame.charAt(0).toUpperCase() + frame.slice(1);

  // Visual bar comparison
  const barMax = maxW * 1.15;
  function formulaBar(name, val, color) {
    const pct = (val / barMax) * 100;
    const bmiAtWeight = calculateBMI(kgToLbs(val), heightInches);
    return `<div class="er-progress"><div class="er-progress-label">${name}</div><div class="er-progress-bar"><div class="er-progress-fill" style="width:${pct}%;background:${color};">${val.toFixed(1)}</div></div><div style="min-width:80px;text-align:right;font-size:0.8125rem;color:var(--gray-500);">${kgToLbs(val).toFixed(0)} lbs &middot; BMI ${bmiAtWeight.toFixed(1)}</div></div>`;
  }

  let html = '';

  // Summary metrics
  html += `<div class="er-section"><h3><span class="er-icon">&#128202;</span> Summary</h3>
    <div class="er-metrics">
      <div class="er-metric"><div class="er-metric-label">Average Ideal</div><div class="er-metric-value">${avg.toFixed(1)} kg</div><div class="er-metric-sub">${kgToLbs(avg).toFixed(0)} lbs</div></div>
      <div class="er-metric"><div class="er-metric-label">Formula Range</div><div class="er-metric-value">${minW.toFixed(1)}-${maxW.toFixed(1)}</div><div class="er-metric-sub">kg (${kgToLbs(minW).toFixed(0)}-${kgToLbs(maxW).toFixed(0)} lbs)</div></div>
      <div class="er-metric"><div class="er-metric-label">BMI Range</div><div class="er-metric-value">${weights.bmiMin.toFixed(1)}-${weights.bmiMax.toFixed(1)}</div><div class="er-metric-sub">kg (18.5-24.9 BMI)</div></div>
      <div class="er-metric"><div class="er-metric-label">Height</div><div class="er-metric-value">${heightToFtIn(heightInches)}</div><div class="er-metric-sub">${Math.round(heightCm)} cm</div></div>
      <div class="er-metric"><div class="er-metric-label">Sex</div><div class="er-metric-value">${sexLabel}</div><div class="er-metric-sub">${frameLabel} frame</div></div>
      <div class="er-metric"><div class="er-metric-label">BMI at Average</div><div class="er-metric-value">${calculateBMI(kgToLbs(avg), heightInches).toFixed(1)}</div><div class="er-metric-sub">${getBMICategory(calculateBMI(kgToLbs(avg), heightInches)).category}</div></div>
    </div></div>`;

  // Visual comparison
  html += `<div class="er-section"><h3><span class="er-icon">&#128200;</span> Formula Comparison</h3>
    ${formulaBar('Devine', weights.devine, '#06b6d4')}
    ${formulaBar('Robinson', weights.robinson, '#8b5cf6')}
    ${formulaBar('Miller', weights.miller, '#22c55e')}
    ${formulaBar('Hamwi', weights.hamwi, '#f59e0b')}
    ${formulaBar('Average', avg, 'var(--primary-dark)')}
    ${formulaBar('BMI Min', weights.bmiMin, '#94a3b8')}
    ${formulaBar('BMI Max', weights.bmiMax, '#94a3b8')}
  </div>`;

  // Detailed table
  html += `<div class="er-section"><h3><span class="er-icon">&#128203;</span> Detailed Comparison</h3>
    <table class="er-table"><thead><tr><th>Formula</th><th style="text-align:center;">Weight (kg)</th><th style="text-align:center;">Weight (lbs)</th><th style="text-align:center;">BMI</th><th>Origin</th></tr></thead><tbody>
      <tr><td>Devine (1974)</td><td style="text-align:center;font-weight:600;">${weights.devine.toFixed(1)}</td><td style="text-align:center;">${kgToLbs(weights.devine).toFixed(0)}</td><td style="text-align:center;">${calculateBMI(kgToLbs(weights.devine), heightInches).toFixed(1)}</td><td>Drug dosage calculations; widely used clinically</td></tr>
      <tr><td>Robinson (1983)</td><td style="text-align:center;font-weight:600;">${weights.robinson.toFixed(1)}</td><td style="text-align:center;">${kgToLbs(weights.robinson).toFixed(0)}</td><td style="text-align:center;">${calculateBMI(kgToLbs(weights.robinson), heightInches).toFixed(1)}</td><td>Modification of Devine; based on mortality data</td></tr>
      <tr><td>Miller (1983)</td><td style="text-align:center;font-weight:600;">${weights.miller.toFixed(1)}</td><td style="text-align:center;">${kgToLbs(weights.miller).toFixed(0)}</td><td style="text-align:center;">${calculateBMI(kgToLbs(weights.miller), heightInches).toFixed(1)}</td><td>Tends to give higher estimates; accounts for larger frames</td></tr>
      <tr><td>Hamwi (1964)</td><td style="text-align:center;font-weight:600;">${weights.hamwi.toFixed(1)}</td><td style="text-align:center;">${kgToLbs(weights.hamwi).toFixed(0)}</td><td style="text-align:center;">${calculateBMI(kgToLbs(weights.hamwi), heightInches).toFixed(1)}</td><td>One of the oldest; used in clinical nutrition</td></tr>
      <tr style="background:var(--primary-bg);"><td><strong>Average</strong></td><td style="text-align:center;font-weight:700;">${avg.toFixed(1)}</td><td style="text-align:center;font-weight:700;">${kgToLbs(avg).toFixed(0)}</td><td style="text-align:center;font-weight:700;">${calculateBMI(kgToLbs(avg), heightInches).toFixed(1)}</td><td>Mean of all four formulas</td></tr>
      <tr><td>BMI 18.5 (min)</td><td style="text-align:center;">${weights.bmiMin.toFixed(1)}</td><td style="text-align:center;">${kgToLbs(weights.bmiMin).toFixed(0)}</td><td style="text-align:center;">18.5</td><td>Lower bound of WHO healthy range</td></tr>
      <tr><td>BMI 24.9 (max)</td><td style="text-align:center;">${weights.bmiMax.toFixed(1)}</td><td style="text-align:center;">${kgToLbs(weights.bmiMax).toFixed(0)}</td><td style="text-align:center;">24.9</td><td>Upper bound of WHO healthy range</td></tr>
    </tbody></table></div>`;

  // Frame size explanation
  html += `<div class="er-section"><h3><span class="er-icon">&#128170;</span> Frame Size Adjustment</h3>
    <p style="font-size:0.875rem;color:var(--gray-600);margin:0 0 0.75rem;">Your selection: <strong>${frameLabel} frame</strong> (${frame === 'small' ? '-10%' : frame === 'large' ? '+10%' : 'no'} adjustment applied)</p>
    <table class="er-table"><thead><tr><th>Frame Size</th><th>Adjustment</th><th>Average Ideal</th><th>How to Determine</th></tr></thead><tbody>
      <tr${frame === 'small' ? ' class="er-active"' : ''}><td>Small</td><td>-10%</td><td>${(avg / frameLabel === 'Small' ? 1 : (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1)) * 0.9 > 0 ? ((weights.devine / (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1) + weights.robinson / (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1) + weights.miller / (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1) + weights.hamwi / (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1)) / 4 * 0.9).toFixed(1) : avg.toFixed(1)} kg</td><td>Wrist circumference &lt; ${sex === 'male' ? '6.5"' : '6"'}; fingers overlap when circling wrist</td></tr>
      <tr${frame === 'medium' ? ' class="er-active"' : ''}><td>Medium</td><td>None</td><td>${((weights.devine / (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1) + weights.robinson / (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1) + weights.miller / (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1) + weights.hamwi / (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1)) / 4).toFixed(1)} kg</td><td>Wrist ${sex === 'male' ? '6.5-7.5"' : '6-6.25"'}; fingers just touch</td></tr>
      <tr${frame === 'large' ? ' class="er-active"' : ''}><td>Large</td><td>+10%</td><td>${((weights.devine / (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1) + weights.robinson / (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1) + weights.miller / (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1) + weights.hamwi / (frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1)) / 4 * 1.1).toFixed(1)} kg</td><td>Wrist &gt; ${sex === 'male' ? '7.5"' : '6.25"'}; fingers don&rsquo;t touch</td></tr>
    </tbody></table></div>`;

  // Summary
  html += `<div class="er-section"><h3><span class="er-icon">&#128221;</span> Recommendation</h3><div class="er-summary">Based on your height of <strong>${heightToFtIn(heightInches)}</strong> (${Math.round(heightCm)} cm), ${sex === 'male' ? 'male' : 'female'} sex, and <strong>${frameLabel.toLowerCase()} frame</strong>, your ideal weight averages <strong>${avg.toFixed(1)} kg (${kgToLbs(avg).toFixed(0)} lbs)</strong> across four established formulas. The WHO BMI-based healthy range for your height is <strong>${weights.bmiMin.toFixed(1)}-${weights.bmiMax.toFixed(1)} kg</strong>. These formulas provide useful targets, but your true ideal weight depends on body composition, fitness level, and overall health markers. Use these numbers as a reference range, not an absolute target.</div></div>`;

  ext.innerHTML = html;
}

/* ===== DISPLAY: LBM RESULTS ===== */

function displayLBMResults(type, formulas, fatMass, bodyFatPct, totalWeightKg, weightLbs, heightInches, sex) {
  const section = document.getElementById(type + '-results');
  if (!section) return;

  const lbm = formulas.boer;
  const lbmEl = document.getElementById(type + '-lbm');
  const fatEl = document.getElementById(type + '-fat-mass');
  const bfEl = document.getElementById(type + '-body-fat');
  const lbmLbsEl = document.getElementById(type + '-lbm-lbs');

  if (lbmEl) lbmEl.textContent = lbm.toFixed(1) + ' kg';
  if (fatEl) fatEl.textContent = fatMass.toFixed(1) + ' kg';
  if (bfEl) bfEl.textContent = bodyFatPct.toFixed(1) + '%';
  if (lbmLbsEl) lbmLbsEl.textContent = kgToLbs(lbm).toFixed(1) + ' lbs';

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

  // Body fat categories
  let bfCategory, bfColor;
  if (sex === 'male') {
    if (bodyFatPct < 6) { bfCategory = 'Essential Fat'; bfColor = '#ef4444'; }
    else if (bodyFatPct < 14) { bfCategory = 'Athletic'; bfColor = '#06b6d4'; }
    else if (bodyFatPct < 18) { bfCategory = 'Fitness'; bfColor = '#22c55e'; }
    else if (bodyFatPct < 25) { bfCategory = 'Average'; bfColor = '#f59e0b'; }
    else { bfCategory = 'Above Average'; bfColor = '#ef4444'; }
  } else {
    if (bodyFatPct < 14) { bfCategory = 'Essential Fat'; bfColor = '#ef4444'; }
    else if (bodyFatPct < 21) { bfCategory = 'Athletic'; bfColor = '#06b6d4'; }
    else if (bodyFatPct < 25) { bfCategory = 'Fitness'; bfColor = '#22c55e'; }
    else if (bodyFatPct < 32) { bfCategory = 'Average'; bfColor = '#f59e0b'; }
    else { bfCategory = 'Above Average'; bfColor = '#ef4444'; }
  }

  let html = '';

  // Key metrics
  html += `<div class="er-section"><h3><span class="er-icon">&#128202;</span> Body Composition Breakdown</h3>
    <div class="er-metrics">
      <div class="er-metric"><div class="er-metric-label">Lean Body Mass</div><div class="er-metric-value" style="color:#06b6d4;">${lbm.toFixed(1)} kg</div><div class="er-metric-sub">${kgToLbs(lbm).toFixed(0)} lbs</div></div>
      <div class="er-metric"><div class="er-metric-label">Fat Mass</div><div class="er-metric-value" style="color:#f59e0b;">${fatMass.toFixed(1)} kg</div><div class="er-metric-sub">${kgToLbs(fatMass).toFixed(0)} lbs</div></div>
      <div class="er-metric"><div class="er-metric-label">Body Fat %</div><div class="er-metric-value" style="color:${bfColor};">${bodyFatPct.toFixed(1)}%</div><div class="er-metric-sub">${bfCategory}</div></div>
      <div class="er-metric"><div class="er-metric-label">FFMI</div><div class="er-metric-value">${ffmi.toFixed(1)}</div><div class="er-metric-sub">Fat-Free Mass Index</div></div>
      <div class="er-metric"><div class="er-metric-label">Adj. FFMI</div><div class="er-metric-value">${adjFfmi.toFixed(1)}</div><div class="er-metric-sub">Height-normalized</div></div>
      <div class="er-metric"><div class="er-metric-label">Total Weight</div><div class="er-metric-value">${totalWeightKg.toFixed(1)} kg</div><div class="er-metric-sub">${Math.round(weightLbs)} lbs</div></div>
    </div></div>`;

  // Composition visual bar
  const leanPct = ((lbm / totalWeightKg) * 100).toFixed(1);
  html += `<div class="er-section"><h3><span class="er-icon">&#127912;</span> Composition Visualization</h3>
    <div style="display:flex;height:36px;border-radius:18px;overflow:hidden;margin:0.5rem 0;">
      <div style="width:${leanPct}%;background:linear-gradient(135deg,#06b6d4,#0891b2);display:flex;align-items:center;justify-content:center;color:white;font-size:0.75rem;font-weight:700;">Lean ${leanPct}%</div>
      <div style="width:${bodyFatPct.toFixed(1)}%;background:linear-gradient(135deg,#f59e0b,#d97706);display:flex;align-items:center;justify-content:center;color:white;font-size:0.75rem;font-weight:700;">Fat ${bodyFatPct.toFixed(1)}%</div>
    </div>
    <div style="display:flex;justify-content:space-between;margin-top:0.5rem;font-size:0.8125rem;color:var(--gray-500);"><span>Lean: ${lbm.toFixed(1)} kg (${kgToLbs(lbm).toFixed(0)} lbs)</span><span>Fat: ${fatMass.toFixed(1)} kg (${kgToLbs(fatMass).toFixed(0)} lbs)</span></div></div>`;

  // Multi-formula comparison
  html += `<div class="er-section"><h3><span class="er-icon">&#128203;</span> Formula Comparison</h3>
    <p style="font-size:0.8125rem;color:var(--gray-500);margin:0 0 0.5rem;">Three established formulas for estimating lean body mass</p>
    <table class="er-table"><thead><tr><th>Formula</th><th style="text-align:center;">LBM (kg)</th><th style="text-align:center;">LBM (lbs)</th><th style="text-align:center;">Fat Mass</th><th style="text-align:center;">Body Fat %</th></tr></thead><tbody>
      <tr class="er-active"><td>Boer (1984)</td><td style="text-align:center;font-weight:600;">${formulas.boer.toFixed(1)}</td><td style="text-align:center;">${kgToLbs(formulas.boer).toFixed(0)}</td><td style="text-align:center;">${fatMass.toFixed(1)} kg</td><td style="text-align:center;">${bodyFatPct.toFixed(1)}%</td></tr>
      <tr><td>James (1976)</td><td style="text-align:center;font-weight:600;">${formulas.james.toFixed(1)}</td><td style="text-align:center;">${kgToLbs(formulas.james).toFixed(0)}</td><td style="text-align:center;">${fatMassJames.toFixed(1)} kg</td><td style="text-align:center;">${bfJames.toFixed(1)}%</td></tr>
      <tr><td>Hume (1966)</td><td style="text-align:center;font-weight:600;">${formulas.hume.toFixed(1)}</td><td style="text-align:center;">${kgToLbs(formulas.hume).toFixed(0)}</td><td style="text-align:center;">${fatMassHume.toFixed(1)} kg</td><td style="text-align:center;">${bfHume.toFixed(1)}%</td></tr>
    </tbody></table></div>`;

  // Body fat categories
  const bfCats = sex === 'male'
    ? [['Essential Fat', '2-5%', '#ef4444'], ['Athletic', '6-13%', '#06b6d4'], ['Fitness', '14-17%', '#22c55e'], ['Average', '18-24%', '#f59e0b'], ['Above Average', '25%+', '#ef4444']]
    : [['Essential Fat', '10-13%', '#ef4444'], ['Athletic', '14-20%', '#06b6d4'], ['Fitness', '21-24%', '#22c55e'], ['Average', '25-31%', '#f59e0b'], ['Above Average', '32%+', '#ef4444']];
  let catRows = '';
  bfCats.forEach(c => {
    const isActive = c[0] === bfCategory;
    catRows += `<tr${isActive ? ' class="er-active"' : ''}><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${c[2]};margin-right:6px;vertical-align:middle;"></span>${c[0]}</td><td style="text-align:center;">${c[1]}</td><td style="text-align:center;">${isActive ? '<strong style="color:var(--primary-dark);">&#10140; You (' + bodyFatPct.toFixed(1) + '%)</strong>' : ''}</td></tr>`;
  });
  html += `<div class="er-section"><h3><span class="er-icon">&#127947;</span> Body Fat Categories (${sex === 'male' ? 'Men' : 'Women'})</h3>
    <table class="er-table"><thead><tr><th>Category</th><th style="text-align:center;">Range</th><th style="text-align:center;">Your Status</th></tr></thead><tbody>${catRows}</tbody></table></div>`;

  // FFMI interpretation
  let ffmiNote = '';
  if (sex === 'male') {
    if (ffmi < 18) ffmiNote = 'Below average for men. May indicate low muscle mass.';
    else if (ffmi < 20) ffmiNote = 'Average range for men.';
    else if (ffmi < 22) ffmiNote = 'Above average. Indicates regular strength training.';
    else if (ffmi < 25) ffmiNote = 'Well-muscled. Consistent resistance training.';
    else ffmiNote = 'Exceptional. Near natural muscular limit (~25 FFMI).';
  } else {
    if (ffmi < 14) ffmiNote = 'Below average for women.';
    else if (ffmi < 17) ffmiNote = 'Average range for women.';
    else if (ffmi < 19) ffmiNote = 'Above average. Regular strength training likely.';
    else if (ffmi < 21) ffmiNote = 'Well-muscled for a woman.';
    else ffmiNote = 'Exceptional muscle mass.';
  }
  html += `<div class="er-section"><h3><span class="er-icon">&#128170;</span> FFMI Interpretation</h3>
    <div class="er-summary">Your Fat-Free Mass Index is <strong>${ffmi.toFixed(1)}</strong> (adjusted: <strong>${adjFfmi.toFixed(1)}</strong>). ${ffmiNote} FFMI provides a height-normalized measure of muscle mass, useful for tracking strength training progress. The natural limit for men is approximately 25; for women approximately 21. Values above these thresholds without performance-enhancing substances are exceptionally rare.</div></div>`;

  ext.innerHTML = html;
}

/* ===== DISPLAY: NEW BMI RESULTS ===== */

function displayNewBMIResults(type, traditionalBMI, newBMI, diff, traditionalCat, newCat, healthyRange, heightInches, weightLbs) {
  const section = document.getElementById(type + '-results');
  if (!section) return;

  const bmiValueEl = document.getElementById(type + '-bmi-value');
  const bmiCategoryEl = document.getElementById(type + '-bmi-category');
  const bmiRangeEl = document.getElementById(type + '-bmi-range');
  const resultCard = document.getElementById(type + '-result-card');
  if (bmiValueEl) bmiValueEl.textContent = newBMI.toFixed(1);
  if (bmiCategoryEl) bmiCategoryEl.textContent = newCat.category;
  if (bmiRangeEl) bmiRangeEl.textContent = 'BMI Range: ' + newCat.range;
  if (resultCard) { resultCard.className = 'bmi-result-card ' + newCat.class; bmiValueEl.className = 'bmi-value ' + newCat.class; }
  const marker = document.getElementById(type + '-scale-marker');
  if (marker) marker.style.left = getScalePosition(newBMI) + '%';
  const tradValueEl = document.getElementById(type + '-traditional-value');
  const tradCatEl = document.getElementById(type + '-traditional-category');
  if (tradValueEl) tradValueEl.textContent = traditionalBMI.toFixed(1);
  if (tradCatEl) tradCatEl.textContent = traditionalCat.category;
  const diffEl = document.getElementById(type + '-diff');
  if (diffEl) {
    const sign = diff >= 0 ? '+' : '';
    diffEl.textContent = sign + diff.toFixed(1);
    diffEl.style.color = Math.abs(diff) < 0.5 ? 'var(--gray-600)' : diff > 0 ? 'var(--error)' : 'var(--success)';
  }
  const catChangeEl = document.getElementById(type + '-category-change');
  if (catChangeEl) {
    if (traditionalCat.category === newCat.category) { catChangeEl.textContent = 'Same category with both formulas'; catChangeEl.style.color = 'var(--gray-600)'; }
    else { catChangeEl.textContent = 'Category changed: ' + traditionalCat.category + ' → ' + newCat.category; catChangeEl.style.color = 'var(--primary)'; }
  }
  const healthyMinEl = document.getElementById(type + '-healthy-min');
  const healthyMaxEl = document.getElementById(type + '-healthy-max');
  if (healthyMinEl) healthyMinEl.textContent = Math.round(healthyRange.min) + ' lbs (' + Math.round(lbsToKg(healthyRange.min)) + ' kg)';
  if (healthyMaxEl) healthyMaxEl.textContent = Math.round(healthyRange.max) + ' lbs (' + Math.round(lbsToKg(healthyRange.max)) + ' kg)';
  const weightDiffEl = document.getElementById(type + '-weight-diff');
  if (weightDiffEl) {
    if (weightLbs < healthyRange.min) {
      var diff = Math.round(healthyRange.min - weightLbs);
      weightDiffEl.textContent = 'Gain ' + diff + ' lbs (' + Math.round(lbsToKg(diff)) + ' kg) to reach healthy range';
    }
    else if (weightLbs > healthyRange.max) {
      var diff = Math.round(weightLbs - healthyRange.max);
      weightDiffEl.textContent = 'Lose ' + diff + ' lbs (' + Math.round(lbsToKg(diff)) + ' kg) to reach healthy range';
    }
    else weightDiffEl.textContent = 'You are within the healthy weight range';
  }
  section.classList.add('visible');

  // Extended results
  const ext = getExtendedContainer(type);
  if (!ext) return;

  const weightKg = lbsToKg(weightLbs);
  const heightM = inchesToCm(heightInches) / 100;
  const heightCm = inchesToCm(heightInches);

  let html = '';

  // Key metrics
  html += `<div class="er-section"><h3><span class="er-icon">&#128202;</span> Detailed Comparison</h3>
    <div class="er-metrics">
      <div class="er-metric"><div class="er-metric-label">New BMI</div><div class="er-metric-value" style="color:${catColor(newCat.class)};">${newBMI.toFixed(1)}</div><div class="er-metric-sub">${newCat.category}</div></div>
      <div class="er-metric"><div class="er-metric-label">Traditional BMI</div><div class="er-metric-value" style="color:${catColor(traditionalCat.class)};">${traditionalBMI.toFixed(1)}</div><div class="er-metric-sub">${traditionalCat.category}</div></div>
      <div class="er-metric"><div class="er-metric-label">Difference</div><div class="er-metric-value" style="color:${Math.abs(diff) < 0.5 ? 'var(--gray-600)' : diff > 0 ? '#ef4444' : '#22c55e'};">${diff >= 0 ? '+' : ''}${diff.toFixed(2)}</div><div class="er-metric-sub">${Math.abs(diff) < 0.5 ? 'Minimal' : Math.abs(diff) < 1 ? 'Small' : 'Significant'}</div></div>
      <div class="er-metric"><div class="er-metric-label">Weight</div><div class="er-metric-value">${Math.round(weightLbs)} lbs</div><div class="er-metric-sub">${weightKg.toFixed(1)} kg</div></div>
      <div class="er-metric"><div class="er-metric-label">Height</div><div class="er-metric-value">${heightToFtIn(heightInches)}</div><div class="er-metric-sub">${Math.round(heightCm)} cm</div></div>
      <div class="er-metric"><div class="er-metric-label">BMI Prime</div><div class="er-metric-value">${(newBMI / 25).toFixed(2)}</div><div class="er-metric-sub">New formula basis</div></div>
    </div></div>`;

  // Side-by-side classification
  html += `<div class="er-section"><h3><span class="er-icon">&#128203;</span> Classification Comparison</h3>
    <table class="er-table"><thead><tr><th>Metric</th><th style="text-align:center;">Traditional Formula</th><th style="text-align:center;">New Formula (Trefethen)</th></tr></thead><tbody>
      <tr><td>Formula</td><td style="text-align:center;">weight(kg) / height(m)&sup2;</td><td style="text-align:center;">1.3 &times; weight(kg) / height(m)<sup>2.5</sup></td></tr>
      <tr><td>Your BMI</td><td style="text-align:center;font-weight:700;color:${catColor(traditionalCat.class)};">${traditionalBMI.toFixed(1)}</td><td style="text-align:center;font-weight:700;color:${catColor(newCat.class)};">${newBMI.toFixed(1)}</td></tr>
      <tr><td>Category</td><td style="text-align:center;">${traditionalCat.category}</td><td style="text-align:center;">${newCat.category}</td></tr>
      <tr><td>Risk Level</td><td style="text-align:center;">${traditionalCat.risk}</td><td style="text-align:center;">${newCat.risk}</td></tr>
      <tr><td>BMI Prime</td><td style="text-align:center;">${(traditionalBMI / 25).toFixed(2)}</td><td style="text-align:center;">${(newBMI / 25).toFixed(2)}</td></tr>
    </tbody></table></div>`;

  // Height divergence table
  const heights = [60, 63, 65, 67, 69, 71, 73, 75, 78];
  let divRows = '';
  heights.forEach(h => {
    const hM = inchesToCm(h) / 100;
    const tBmi = calculateBMI(weightLbs, h);
    const nBmi = 1.3 * weightKg / Math.pow(hM, 2.5);
    const d = nBmi - tBmi;
    const isCurrent = Math.abs(h - heightInches) < 1.5;
    divRows += `<tr${isCurrent ? ' class="er-active"' : ''}><td>${heightToFtIn(h)}</td><td style="text-align:center;">${Math.round(inchesToCm(h))} cm</td><td style="text-align:center;">${tBmi.toFixed(1)}</td><td style="text-align:center;">${nBmi.toFixed(1)}</td><td style="text-align:center;font-weight:600;color:${d > 0 ? '#ef4444' : d < -0.5 ? '#22c55e' : 'var(--gray-600)'};">${d >= 0 ? '+' : ''}${d.toFixed(1)}</td></tr>`;
  });
  html += `<div class="er-section"><h3><span class="er-icon">&#128207;</span> How Height Affects the Difference</h3>
    <p style="font-size:0.8125rem;color:var(--gray-500);margin:0 0 0.5rem;">Same weight (${Math.round(weightLbs)} lbs) at different heights &mdash; the New BMI corrects the traditional formula&rsquo;s height bias</p>
    <table class="er-table"><thead><tr><th>Height</th><th style="text-align:center;">cm</th><th style="text-align:center;">Trad. BMI</th><th style="text-align:center;">New BMI</th><th style="text-align:center;">Diff</th></tr></thead><tbody>${divRows}</tbody></table>
    <p style="font-size:0.8125rem;color:var(--gray-500);margin:0.5rem 0 0;"><strong>Key insight:</strong> For shorter people, the new formula gives a <em>higher</em> BMI (traditional underestimates). For taller people, it gives a <em>lower</em> BMI (traditional overestimates). The crossover point is around 5&rsquo;7&rdquo; (170 cm).</p></div>`;

  // Which should you use
  html += `<div class="er-section"><h3><span class="er-icon">&#128161;</span> Which Formula Should You Use?</h3><div class="er-summary">
    ${Math.abs(diff) < 0.5
      ? `At your height of <strong>${heightToFtIn(heightInches)}</strong>, both formulas give nearly identical results (difference of just ${Math.abs(diff).toFixed(1)} points). Either formula works well for you.`
      : heightInches < 66
        ? `At <strong>${heightToFtIn(heightInches)}</strong>, you are shorter than average. The traditional formula likely <strong>underestimates</strong> your BMI by about ${Math.abs(diff).toFixed(1)} points. The New BMI (${newBMI.toFixed(1)}) may be more accurate for you.`
        : `At <strong>${heightToFtIn(heightInches)}</strong>, you are taller than average. The traditional formula likely <strong>overestimates</strong> your BMI by about ${Math.abs(diff).toFixed(1)} points. The New BMI (${newBMI.toFixed(1)}) may be more accurate for you.`
    }
    <br><br><em>Note: The traditional BMI remains the standard used by healthcare providers worldwide. The Trefethen formula (2013) has not been adopted by WHO or major health organizations, but it offers a useful second opinion, especially for very short or very tall individuals.</em>
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
