"""
=============================================================================
Digit Span Backward — Simple Dashboard Generator
=============================================================================
Reads all 4 E-Prime CSV files and writes a self-contained HTML file.
Open the HTML in any browser — no internet needed after first load.

OUTPUT: digit_span_simple_dashboard.html  (same folder as this script)
=============================================================================
"""

import pandas as pd
import json
import os

# ── CONFIG — update paths if needed ──────────────────────────────────────────
BASE = r"C:\Users\ASSUS\ATN\Digit Span Backwards\Data\Eprime Data\Digit Span Backwards v3.2"

SESSIONS = [
    {"label": "S1", "stim": "No stimulation",  "color": "#3266ad",
     "csv": os.path.join(BASE, "DigitSpanBackward v3.3-6-1-Scores.csv")},
    {"label": "S2", "stim": "Targeted stim",   "color": "#1D9E75",
     "csv": os.path.join(BASE, "DigitSpanBackward v3.3-6-2-Scores.csv")},
    {"label": "S3", "stim": "Targeted stim",   "color": "#D4537E",
     "csv": os.path.join(BASE, "DigitSpanBackward v3.3-6-3-Scores.csv")},
    {"label": "S4", "stim": "Stim throughout", "color": "#7F77DD",
     "csv": os.path.join(BASE, "DigitSpanBackward v3.3-6-4-Scores.csv")},
]

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "digit_span_simple_dashboard.html")

# ── LOAD ──────────────────────────────────────────────────────────────────────
def load(path, label):
    if not os.path.exists(path):
        print(f"  ⚠  Not found: {path}  →  {label} skipped")
        return None
    df_raw = pd.read_csv(path, header=None)
    cols   = df_raw.iloc[1].tolist()
    df     = pd.DataFrame(df_raw.values[2:], columns=cols)
    for c in ["Block","Trial","CurrentSpanSize[Trial]",
              "CollectResponse.ACC","CollectResponse.RESP",
              "CorrectResp","CollectResponse.RT"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["CollectResponse.ACC"])
    trial = (
        df.groupby(["Block","Trial"])
        .agg(span=("CurrentSpanSize[Trial]","first"),
             acc=("CollectResponse.ACC","first"),
             resp=("CollectResponse.RESP","first"),
             cresp=("CorrectResp","first"),
             rt=("CollectResponse.RT","first"))
        .reset_index().sort_values(["Block","Trial"]).reset_index(drop=True)
    )
    trial["resp"]  = trial["resp"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    trial["cresp"] = trial["cresp"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    return trial

print("=" * 55)
print("Digit Span Backward — Simple Dashboard Generator")
print("=" * 55)

loaded = []
for s in SESSIONS:
    print(f"\nLoading {s['label']} ({s['stim']})...")
    t = load(s["csv"], s["label"])
    if t is None:
        continue
    s["trials"] = t[["span","acc","resp","cresp","rt"]].to_dict(orient="records")
    loaded.append(s)
    cor = sum(1 for r in t.itertuples() if r.acc == 1)
    print(f"  {len(t)} trials  |  {cor} correct  |  {len(t)-cor} not correct")

if not loaded:
    print("\nNo files found. Check the BASE path at the top of this script.")
    raise SystemExit(1)

sessions_json = json.dumps(
    [{"label":s["label"],"stim":s["stim"],"color":s["color"],"trials":s["trials"]}
     for s in loaded], indent=2)

# ── HTML ──────────────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Digit Span Backward — Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
body{background:#f8f8f6;color:#1a1a1a;font-size:14px;line-height:1.6}
.container{max-width:1000px;margin:0 auto;padding:2rem 1.5rem}
h1{font-size:22px;font-weight:500;margin-bottom:4px}
.sub{font-size:13px;color:#666;margin-bottom:2rem}
.section{margin-bottom:2.5rem}
.section-label{font-size:11px;font-weight:500;letter-spacing:.07em;text-transform:uppercase;color:#888;margin-bottom:4px}
.section-q{font-size:18px;font-weight:500;margin-bottom:1rem}
.story{border-radius:10px;padding:14px 18px;font-size:14px;line-height:1.75;
       color:#555;margin-bottom:1.2rem;border:1px solid #e8e8e4;background:#fff}
.story strong{color:#1a1a1a}
.divider{height:1px;background:#e8e8e4;margin:2rem 0}
/* session cards */
.sess-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:1.5rem}
.sc{border-radius:12px;padding:18px 16px;border:1px solid #e8e8e4;background:#fff}
.sc-name{font-size:13px;font-weight:500;margin-bottom:2px}
.sc-stim{font-size:12px;color:#888;margin-bottom:14px}
.sc-acc{font-size:36px;font-weight:500;line-height:1;margin-bottom:2px}
.sc-acc-label{font-size:12px;color:#888;margin-bottom:14px}
.brow{display:flex;align-items:center;gap:8px;margin-bottom:5px}
.brow-label{font-size:12px;width:76px;flex-shrink:0}
.brow-track{flex:1;height:12px;background:#f0f0ee;border-radius:3px;overflow:hidden}
.brow-fill{height:100%;border-radius:3px}
.brow-val{font-size:12px;font-weight:500;width:22px;text-align:right;flex-shrink:0}
.badge{display:inline-block;font-size:11px;padding:3px 9px;border-radius:20px;margin-top:12px;font-weight:500}
.b-up{background:#e6f5ed;color:#1a7a3f}
.b-dn{background:#fdecea;color:#c0392b}
.b-eq{background:#f0f0ee;color:#666}
/* improvement row */
.imp-row{display:flex;align-items:center;flex-wrap:wrap;gap:4px;margin-bottom:1.5rem}
.imp-block{text-align:center;padding:12px 18px;border-radius:10px;border:1px solid #e8e8e4;background:#fff}
.imp-num{font-size:30px;font-weight:500;line-height:1}
.imp-label{font-size:11px;color:#888;margin-top:3px}
.imp-arrow{font-size:20px;color:#bbb;padding:0 2px}
/* legend */
.legend{display:flex;gap:18px;margin-bottom:10px;font-size:12px;color:#666;flex-wrap:wrap}
.ld{width:12px;height:12px;border-radius:2px;display:inline-block;margin-right:5px;vertical-align:middle}
/* span table */
.span-table{width:100%;border-collapse:collapse;font-size:13px;margin-bottom:8px}
.span-table th{text-align:left;padding:8px 10px;font-weight:500;font-size:12px;
               color:#888;border-bottom:1px solid #e8e8e4}
.span-table td{padding:10px 10px;border-bottom:1px solid #f0f0ee;vertical-align:top}
.span-table tr:last-child td{border-bottom:none}
.stat-pct{font-size:15px;font-weight:500}
.stat-detail{font-size:11px;color:#888;margin-top:2px}
.note{font-size:12px;color:#888;margin-top:6px}
.chart-wrap{position:relative}
</style>
</head>
<body>
<div class="container">

  <h1>Digit Span Backward — Patient Performance</h1>
  <div class="sub">Single patient &middot; 4 sessions &middot; Stimulation conditions compared</div>

  <!-- SECTION 1 -->
  <div class="section">
    <div class="section-label">Question 1</div>
    <div class="section-q">Did the patient improve across sessions?</div>
    <div class="imp-row" id="imp-row"></div>
    <div class="story" id="story1"></div>
    <div class="legend">
      <span><span class="ld" style="background:#27a05a"></span>Correct — exact answer</span>
      <span><span class="ld" style="background:#EF9F27"></span>Almost correct — off by just 1 digit</span>
      <span><span class="ld" style="background:#E24B4A"></span>Incorrect — 2 or more digits wrong</span>
    </div>
    <div class="chart-wrap" style="height:230px"><canvas id="cMain"></canvas></div>
  </div>

  <div class="divider"></div>

  <!-- SECTION 2 -->
  <div class="section">
    <div class="section-label">Question 2</div>
    <div class="section-q">What was the correct vs wrong breakdown in each session?</div>
    <div class="sess-grid" id="sess-cards"></div>
    <div class="story" id="story2"></div>
  </div>

  <div class="divider"></div>

  <!-- SECTION 3 -->
  <div class="section">
    <div class="section-label">Bonus — where did difficulty matter?</div>
    <div class="section-q">At which span size did the patient start struggling?</div>
    <div class="story">
      The task gets harder as the number of digits increases — <strong>2 digits is easy, 5 digits is very hard</strong>.
      The table below shows accuracy at each difficulty level across all sessions.
      C = correct &nbsp;|&nbsp; A = almost correct &nbsp;|&nbsp; W = wrong.
    </div>
    <div id="span-table"></div>
  </div>

</div>

<script>
const SESSIONS = SESSION_DATA_PLACEHOLDER;

function clf(tr) {
  if (tr.acc === 1) return 'correct';
  const r = String(tr.resp), c = String(tr.cresp);
  const wrong = Math.max(r.length, c.length) - [...r].filter((ch,i) => ch === c[i]).length;
  return wrong <= 1 ? 'almost' : 'incorrect';
}

const ST = SESSIONS.map(s => {
  const res = s.trials.map(clf);
  const cor = res.filter(x => x==='correct').length;
  const alm = res.filter(x => x==='almost').length;
  const inc = res.filter(x => x==='incorrect').length;
  const n   = s.trials.length;
  return { cor, alm, inc, n, acc: Math.round(cor/n*100), res };
});

// ── Improvement row ────────────────────────────────────────────────────────
const impRow = document.getElementById('imp-row');
SESSIONS.forEach((s, i) => {
  if (i > 0) impRow.innerHTML += `<div class="imp-arrow">&#8594;</div>`;
  impRow.innerHTML += `
    <div class="imp-block" style="border-color:${s.color}44">
      <div class="imp-num" style="color:${s.color}">${ST[i].acc}%</div>
      <div class="imp-label">${s.label} &mdash; ${s.stim}</div>
    </div>`;
});

// ── Story 1 ────────────────────────────────────────────────────────────────
const bestI  = ST.reduce((bi, x, xi) => x.acc > ST[bi].acc ? xi : bi, 0);
const worstI = ST.reduce((bi, x, xi) => x.acc < ST[bi].acc ? xi : bi, 0);
const trend  = ST[ST.length-1].acc > ST[0].acc ? 'improved overall' : ST[ST.length-1].acc < ST[0].acc ? 'did not improve overall' : 'stayed about the same overall';
document.getElementById('story1').innerHTML =
  `The patient <strong>${trend}</strong> from S1 (${ST[0].acc}%) to S${ST.length} (${ST[ST.length-1].acc}%).
   Best session was <strong>${SESSIONS[bestI].label} — ${SESSIONS[bestI].stim}</strong> at <strong>${ST[bestI].acc}%</strong>.
   Worst session was <strong>${SESSIONS[worstI].label} — ${SESSIONS[worstI].stim}</strong> at <strong>${ST[worstI].acc}%</strong>.`;

// ── Main chart ─────────────────────────────────────────────────────────────
new Chart(document.getElementById('cMain'), {
  type: 'bar',
  data: {
    labels: SESSIONS.map(s => `${s.label} — ${s.stim}`),
    datasets: [
      { label:'Correct',       data: ST.map(s=>s.cor), backgroundColor:'#27a05a', borderRadius:4, stack:'s' },
      { label:'Almost correct',data: ST.map(s=>s.alm), backgroundColor:'#EF9F27', borderRadius:0, stack:'s' },
      { label:'Incorrect',     data: ST.map(s=>s.inc), backgroundColor:'#E24B4A', borderRadius:0, stack:'s' },
    ]
  },
  options: { responsive:true, maintainAspectRatio:false,
    plugins:{ legend:{ display:false },
      tooltip:{ callbacks:{ footer: items => `Accuracy: ${ST[items[0].dataIndex].acc}% correct` }}},
    scales:{
      x:{ stacked:true, grid:{display:false}, ticks:{font:{size:12}} },
      y:{ stacked:true, grid:{color:'rgba(0,0,0,0.05)'},
          title:{display:true, text:'Number of trials (out of 14)', font:{size:11}, color:'#888'},
          ticks:{stepSize:2} }
    }
  }
});

// ── Session cards ──────────────────────────────────────────────────────────
const cardsEl = document.getElementById('sess-cards');
SESSIONS.forEach((s, i) => {
  const st = ST[i];
  const prev = i > 0 ? ST[i-1] : null;
  let badge = '';
  if (prev) {
    const diff = st.acc - prev.acc;
    if      (diff >  5) badge = `<span class="badge b-up">+${diff}% better than last session</span>`;
    else if (diff < -5) badge = `<span class="badge b-dn">${Math.abs(diff)}% worse than last session</span>`;
    else                badge = `<span class="badge b-eq">Similar to last session</span>`;
  }
  const pC = Math.round(st.cor/st.n*100);
  const pA = Math.round(st.alm/st.n*100);
  const pI = Math.round(st.inc/st.n*100);
  cardsEl.innerHTML += `
    <div class="sc" style="border-top:3px solid ${s.color}">
      <div class="sc-name" style="color:${s.color}">${s.label}</div>
      <div class="sc-stim">${s.stim}</div>
      <div class="sc-acc" style="color:${s.color}">${st.acc}%</div>
      <div class="sc-acc-label">${st.cor} correct out of ${st.n} trials</div>
      <div class="brow">
        <div class="brow-label" style="color:#27a05a">Correct</div>
        <div class="brow-track"><div class="brow-fill" style="width:${pC}%;background:#27a05a"></div></div>
        <div class="brow-val" style="color:#27a05a">${st.cor}</div>
      </div>
      <div class="brow">
        <div class="brow-label" style="color:#EF9F27">Almost</div>
        <div class="brow-track"><div class="brow-fill" style="width:${pA}%;background:#EF9F27"></div></div>
        <div class="brow-val" style="color:#EF9F27">${st.alm}</div>
      </div>
      <div class="brow">
        <div class="brow-label" style="color:#E24B4A">Incorrect</div>
        <div class="brow-track"><div class="brow-fill" style="width:${pI}%;background:#E24B4A"></div></div>
        <div class="brow-val" style="color:#E24B4A">${st.inc}</div>
      </div>
      ${badge}
    </div>`;
});

// ── Story 2 ────────────────────────────────────────────────────────────────
const best4 = SESSIONS.map((s, i) => {
  const grp = s.trials.filter(t => t.span === 4);
  const res = grp.map(clf);
  return grp.length ? Math.round(res.filter(x=>x==='correct').length / grp.length * 100) : 0;
});
const best4i = best4.indexOf(Math.max(...best4));
document.getElementById('story2').innerHTML =
  `At <strong>4 digits</strong> (the most common difficulty level), performance varied the most:
   ${SESSIONS.map((s,i) => `${s.label}: ${best4[i]}%`).join(', ')}.
   <strong>${SESSIONS[best4i].label} (${SESSIONS[best4i].stim})</strong> handled 4-digit trials best.`;

// ── Span table ─────────────────────────────────────────────────────────────
const spans = [2, 3, 4, 5];
const spanNames = { 2:'2 digits (easy)', 3:'3 digits', 4:'4 digits (medium)', 5:'5 digits (hard)' };
let th = `<table class="span-table"><thead><tr>
  <th>Difficulty</th>
  ${SESSIONS.map(s=>`<th style="color:${s.color}">${s.label}</th>`).join('')}
</tr></thead><tbody>`;

spans.forEach(sp => {
  th += `<tr><td style="color:#666;font-size:12px">${spanNames[sp]}</td>`;
  SESSIONS.forEach((s, i) => {
    const grp = s.trials.filter(t => t.span === sp);
    if (!grp.length) { th += `<td style="color:#ccc">—</td>`; return; }
    const res = grp.map(clf);
    const cor = res.filter(x=>x==='correct').length;
    const alm = res.filter(x=>x==='almost').length;
    const inc = res.filter(x=>x==='incorrect').length;
    const acc = Math.round(cor / res.length * 100);
    const tc  = acc===100 ? '#1a7a3f' : acc>=50 ? '#9a5d00' : '#c0392b';
    const bg  = acc===100 ? '#e6f5ed' : acc>=50 ? '#fef9ed' : '#fdecea';
    th += `<td>
      <div class="stat-pct" style="color:${tc};background:${bg};
        display:inline-block;padding:2px 8px;border-radius:6px">${acc}%</div>
      <div class="stat-detail">${cor}C &nbsp;${alm}A &nbsp;${inc}W</div>
    </td>`;
  });
  th += '</tr>';
});
th += '</tbody></table><div class="note">C = correct &nbsp; A = almost correct &nbsp; W = wrong &nbsp; Green = 100% &nbsp; Yellow = 50%+ &nbsp; Red = under 50%</div>';
document.getElementById('span-table').innerHTML = th;
</script>
</body>
</html>"""

HTML = HTML.replace("SESSION_DATA_PLACEHOLDER", sessions_json)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"\n{'='*55}")
print(f"Done! Open this file in your browser:")
print(f"  {OUTPUT}")
print(f"{'='*55}")