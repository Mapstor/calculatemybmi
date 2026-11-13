// CMB-043: check /childhood-obesity-statistics/'s CSV against NCHS Health E-Stat 112 as published.
// Run in a browser's console on https://www.cdc.gov/nchs/data/hestat/hestat112.htm (chat ran it in Chrome on
// 2026-11-13). It reads Tables 1-3 from the page itself (no copy of CDC's numbers passes through anyone's hands),
// turns each cell into the CSV's own row form (table|period|group|measure|percent|se|flag; Table 3 without its
// standard errors, which the CSV doesn't carry, and only the 2017-2018 and 2021-2023 periods the CSV has), and
// prints the SHA-256 of the sorted rows. research/cmb-043/he112_canon.py prints the same hash for the CSV; equal
// hashes mean every row's percent, standard error and flag is CDC's.
// 2026-11-13: 278 rows on both sides, sha256 4ac5923e653732381454885a9dbd389f9024e7af75eb223d2808160ccc897a5f
// (per table: 1 126 rows d166c917dd52f122, 2 132 rows ffefd9770a43fa07, 3 20 rows 2751fff15871f7ce).
(async () => {
  const clean = s => s.replace(/\s+/g, ' ').trim();
  const rows = [];
  [...document.querySelectorAll('table')].forEach((t, ti) => {
    const grid = [];
    [...t.querySelectorAll('tr')].forEach((r, ri) => {
      grid[ri] = grid[ri] || [];
      let c = 0;
      [...r.children].forEach(cell => {
        while (grid[ri][c]) c++;
        const rs = cell.rowSpan || 1, cs = cell.colSpan || 1;
        for (let dr = 0; dr < rs; dr++) for (let dc = 0; dc < cs; dc++) {
          grid[ri + dr] = grid[ri + dr] || [];
          grid[ri + dr][c + dc] = {text: clean(cell.textContent), cs};
        }
        c += cs;
      });
    });
    const first = ti === 0 ? 2 : 1;              // Table 1 has a sample-size column after the period
    for (let ri = 3; ri < grid.length; ri++) {   // rows 0-2: group, measure and "Percent (standard error)" headings
      for (let c = first; c < grid[0].length; c += 2) {
        const a = grid[ri][c], b = grid[ri][c + 1];
        rows.push([String(ti + 1), grid[ri][0].text, grid[0][c].text, grid[1][c].text, a.text, a.cs === 2 ? '' : b.text]);
      }
    }
  });
  const sex = g => ({All1: 'all', All: 'all', Boys: 'boys', Boys1: 'boys', Girls: 'girls', Girls1: 'girls'})[g];
  const lines = [];
  for (const [t, p0, g, sub, v0, se0] of rows) {
    if (v0 === '– – –') continue;                // not measured in that survey
    const period = p0.replace(/^(\d{4}–\d{4})\d+$/, '$1').replace('August 2021–August 2023', 'Aug 2021–Aug 2023');
    let flag = '', v = v0;
    if (/^[*†]/.test(v)) { flag = v[0]; v = v.slice(1); }
    const se = t === '3' ? '' : se0.replace(/[()]/g, '');
    let group, measure = 'obesity';
    if (t === '1') {
      group = sex(g) + ' 2-19';
      measure = {Overweight: 'overweight', Obesity: 'obesity', 'Severe obesity': 'severe_obesity'}[sub];
    } else if (t === '2') {
      group = sex(g) + ' ' + sub.replace(/–/g, '-') + (p0.startsWith('1966–1970') && sub === '12–19' ? ' (12-17)' : '');
    } else {
      if (!/2017–2018|2021/.test(period)) continue;
      group = sex(g) + ' ' + sub;
    }
    lines.push([t, period, group, measure, v, se, flag].join('|'));
  }
  const sha = async s => [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)))]
    .map(x => x.toString(16).padStart(2, '0')).join('');
  console.log(lines.length, 'rows, sha256', await sha([...lines].sort().join('\n') + '\n'));
})();
