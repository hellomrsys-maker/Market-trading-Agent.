/**
 * app.js — OptionAlpha Agent Live Dashboard
 * Polls /api/status every 10 seconds and updates all UI elements.
 * Falls back to reading dashboard_data.json via local file serve.
 */

'use strict';

// ─────────────────────────────────────────────────────────────
// Config
// ─────────────────────────────────────────────────────────────
const POLL_INTERVAL_MS = 10_000;
const API_BASE         = window.location.origin;
const STARTING_CAPITAL = 100_000;

const REGIME_COLORS = {
  'Neutral':      '#a78bfa',
  'Bull Trend':   '#22c55e',
  'Bear Trend':   '#ef4444',
  'High-IV Crush':'#f59e0b',
};

const STRATEGY_COLORS = {
  'WHEEL_CSP': '#7c3aed',
  'WHEEL_CC':  '#3b82f6',
  'IRON_CONDOR':'#f59e0b',
};

// ─────────────────────────────────────────────────────────────
// Chart instances
// ─────────────────────────────────────────────────────────────
let equityChart, donutChart;
let equityHistory = [];

// ─────────────────────────────────────────────────────────────
// Init
// ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initCharts();
  startClock();
  pollData();
  setInterval(pollData, POLL_INTERVAL_MS);
});

// ─────────────────────────────────────────────────────────────
// Clock
// ─────────────────────────────────────────────────────────────
function startClock() {
  function tick() {
    const now = new Date();
    const et  = new Intl.DateTimeFormat('en-US', {
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      timeZone: 'America/New_York', hour12: false
    }).format(now);
    document.getElementById('live-clock').textContent = et + ' ET';
  }
  tick();
  setInterval(tick, 1000);
}

// ─────────────────────────────────────────────────────────────
// Data polling
// ─────────────────────────────────────────────────────────────
async function pollData() {
  try {
    // Try the FastAPI /api/status endpoint first
    let data;
    try {
      const resp = await fetch(`${API_BASE}/api/status`, { signal: AbortSignal.timeout(5000) });
      if (resp.ok) {
        data = await resp.json();
      }
    } catch (e) {
      // Fallback: read the JSON log file served as static content
      const resp2 = await fetch('./dashboard_data.json', { signal: AbortSignal.timeout(5000) });
      if (resp2.ok) {
        const arr = await resp2.json();
        data = Array.isArray(arr) && arr.length ? arr[arr.length - 1] : null;
      }
    }
    if (data) updateDashboard(data);
    else      setOffline();
  } catch (e) {
    setOffline();
  }
}

// ─────────────────────────────────────────────────────────────
// Dashboard update
// ─────────────────────────────────────────────────────────────
function updateDashboard(d) {
  const equity   = d.equity    ?? STARTING_CAPITAL;
  const dailyPnl = d.daily_pnl ?? 0;
  const nPos     = d.n_positions ?? 0;
  const halted   = d.risk?.halted ?? false;

  // Status pill
  const pill = document.getElementById('status-pill');
  const dot  = document.getElementById('status-dot');
  const txt  = document.getElementById('status-text');
  if (halted) {
    dot.className = 'status-dot halted';
    txt.textContent = 'HALTED';
    pill.style.borderColor = 'rgba(239,68,68,0.5)';
  } else {
    dot.className = 'status-dot';
    txt.textContent = 'LIVE';
    pill.style.borderColor = '';
  }

  // KPI: Equity
  const totalReturn = (equity / STARTING_CAPITAL - 1) * 100;
  document.getElementById('equity-val').textContent    = fmt$(equity);
  const retEl = document.getElementById('equity-return');
  retEl.textContent  = `${totalReturn >= 0 ? '+' : ''}${totalReturn.toFixed(2)}% total return`;
  retEl.className    = `kpi-delta ${totalReturn >= 0 ? 'pos' : 'neg'}`;

  // KPI: Daily P&L
  const pnlPct = (dailyPnl / equity) * 100;
  document.getElementById('pnl-val').textContent = `${dailyPnl >= 0 ? '+' : ''}${fmt$(dailyPnl)}`;
  const pnlEl = document.getElementById('pnl-pct');
  pnlEl.textContent = `${pnlPct >= 0 ? '+' : ''}${pnlPct.toFixed(2)}% today`;
  pnlEl.className   = `kpi-delta ${pnlPct >= 0 ? 'pos' : 'neg'}`;

  // KPI: Positions
  document.getElementById('pos-val').textContent = nPos;

  // KPI: Regime
  const regime = d.regime ?? 'Neutral';
  const regimeEl = document.getElementById('regime-val');
  regimeEl.textContent  = regime;
  regimeEl.style.color  = REGIME_COLORS[regime] ?? '#a78bfa';

  // Equity history for chart
  equityHistory.push({ t: new Date().toLocaleTimeString(), v: equity });
  if (equityHistory.length > 100) equityHistory.shift();
  updateEquityChart();

  // Positions table
  updatePositionsTable(d.wheel_pos ?? [], d.ic_pos ?? []);

  // Donut chart
  updateDonut(d.wheel_pos ?? [], d.ic_pos ?? []);

  // Risk meters
  updateRisk(d.risk ?? {}, equity);

  // Circuit breaker badge
  const cb = document.getElementById('circuit-breaker-badge');
  if (halted) { cb.className = 'circuit-breaker active'; cb.textContent = '⛔ CIRCUIT BREAKER: ACTIVE'; }
  else        { cb.className = 'circuit-breaker';        cb.textContent = '✅ CIRCUIT BREAKER: OFF'; }

  // AI status (static — indicate model status)
  updateAIStatus(d.ai_status ?? {});

  // Last update
  document.getElementById('last-update').textContent =
    'Last update: ' + new Date().toLocaleTimeString();

  // Log entry
  addLog(`Equity=${fmt$(equity)} | P&L=${fmt$(dailyPnl,true)} | Positions=${nPos}`, 'info');
}

// ─────────────────────────────────────────────────────────────
// Chart initialisation
// ─────────────────────────────────────────────────────────────
function initCharts() {
  // Equity chart
  const eCtx = document.getElementById('equity-chart').getContext('2d');
  equityChart = new Chart(eCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label:            'Portfolio',
          data:             [],
          borderColor:      '#7c3aed',
          backgroundColor:  'rgba(124,58,237,0.08)',
          fill:             true,
          tension:          0.4,
          pointRadius:      0,
          borderWidth:      2,
        },
        {
          label:           'Benchmark',
          data:            [],
          borderColor:     '#3b82f6',
          backgroundColor: 'transparent',
          fill:            false,
          tension:         0.4,
          pointRadius:     0,
          borderWidth:     1.5,
          borderDash:      [4,4],
        }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 400 },
      plugins: { legend: { display: false }, tooltip: {
        mode: 'index', intersect: false,
        backgroundColor: '#181c24', borderColor: 'rgba(255,255,255,0.06)',
        titleColor: '#f1f5f9', bodyColor: '#94a3b8', borderWidth: 1,
        callbacks: { label: ctx => `$${ctx.parsed.y.toLocaleString()}` }
      }},
      scales: {
        x: { display: false },
        y: {
          grid:  { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            color:    '#64748b',
            callback: v => '$' + (v/1000).toFixed(0) + 'k',
          }
        }
      }
    }
  });

  // Donut chart
  const dCtx = document.getElementById('donut-chart').getContext('2d');
  donutChart = new Chart(dCtx, {
    type: 'doughnut',
    data: {
      labels:   ['Wheel CSP', 'Wheel CC', 'Iron Condor', 'Cash'],
      datasets: [{ data: [0,0,0,100], backgroundColor: ['#7c3aed','#3b82f6','#f59e0b','#1e293b'],
                   borderWidth: 0, hoverOffset: 6 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: '68%',
      plugins: { legend: { display: false },
        tooltip: { backgroundColor: '#181c24', borderColor: 'rgba(255,255,255,0.06)', borderWidth: 1 }
      }
    }
  });
}

// ─────────────────────────────────────────────────────────────
// Chart updates
// ─────────────────────────────────────────────────────────────
function updateEquityChart() {
  equityChart.data.labels   = equityHistory.map(p => p.t);
  equityChart.data.datasets[0].data = equityHistory.map(p => p.v);
  equityChart.data.datasets[1].data = equityHistory.map(_ => STARTING_CAPITAL);
  equityChart.update('none');
}

function updateDonut(wheelPos, icPos) {
  const csp  = wheelPos.filter(p => p.stage === 'CSP').length;
  const cc   = wheelPos.filter(p => p.stage === 'CC').length;
  const ic   = icPos.length;
  const cash = Math.max(0, 10 - csp - cc - ic);
  donutChart.data.datasets[0].data = [csp, cc, ic, cash];
  donutChart.update('none');

  // Legend
  const lg = document.getElementById('donut-legend');
  const items = [
    { label: `CSP (${csp})`,   color: '#7c3aed' },
    { label: `CC  (${cc})`,    color: '#3b82f6' },
    { label: `IC  (${ic})`,    color: '#f59e0b' },
    { label: `Cash(${cash})`,  color: '#1e293b' },
  ];
  lg.innerHTML = items.map(i =>
    `<div class="dl-item"><div class="dl-dot" style="background:${i.color}"></div>${i.label}</div>`
  ).join('');
}

// ─────────────────────────────────────────────────────────────
// Positions table
// ─────────────────────────────────────────────────────────────
function updatePositionsTable(wheelPos, icPos) {
  const tbody = document.getElementById('positions-body');
  const badge = document.getElementById('pos-count-badge');
  const all   = [...wheelPos.map(p => ({...p, _type:'wheel'})),
                  ...icPos.map(p => ({...p, _type:'ic'}))];
  badge.textContent = all.length;
  document.getElementById('pos-val').textContent = all.length;

  if (!all.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-row">No positions open</td></tr>';
    return;
  }
  tbody.innerHTML = all.map(p => {
    const sym   = p.symbol ?? p.underlying ?? '—';
    const strat = p._type === 'ic' ? 'IRON_CONDOR' : (p.stage || '—');
    const strike= p.strike   ? `$${p.strike}` : (p.be_lower ? `${fmt$(p.be_lower)}–${fmt$(p.be_upper)}` : '—');
    const dte   = p.dte      ?? '—';
    const prem  = p.premium  ? fmt$(p.premium) : (p.credit ? fmt$(p.credit) : '—');
    const tagClass = strat === 'IRON_CONDOR' ? 'tag-ic' : strat === 'CC' ? 'tag-cc' : 'tag-csp';
    return `<tr>
      <td>${sym}</td>
      <td class="${tagClass}">${strat}</td>
      <td>${strike}</td>
      <td>${dte}d</td>
      <td>${prem}</td>
      <td>—</td>
    </tr>`;
  }).join('');
}

// ─────────────────────────────────────────────────────────────
// Risk meters
// ─────────────────────────────────────────────────────────────
function updateRisk(risk, equity) {
  const daily  = Math.abs(risk.daily_pnl ?? 0);
  const limit  = risk.daily_loss_limit ?? 2000;
  const nPos   = risk.position_count ?? 0;
  const maxPos = risk.max_positions ?? 10;
  const delta  = Math.abs(risk.delta_exp ?? 0);
  const maxDel = 500;

  setBar('loss-bar',  (daily  / limit)  * 100, 'loss-used',  `$${daily.toFixed(0)} / $${limit}`,  daily/limit  > 0.7 ? 'danger' : 'normal');
  setBar('pos-bar',   (nPos   / maxPos) * 100, 'pos-used',   `${nPos} / ${maxPos}`,                nPos/maxPos  > 0.8 ? 'warning': 'normal');
  setBar('delta-bar', (delta  / maxDel) * 100, 'delta-used', `$${delta.toFixed(0)} / $${maxDel}`, delta/maxDel > 0.7 ? 'warning': 'normal');
}
function setBar(barId, pct, valId, label, cls) {
  const bar = document.getElementById(barId);
  bar.style.width = Math.min(pct, 100) + '%';
  bar.className   = `progress-fill ${cls}`;
  document.getElementById(valId).textContent = label;
}

// ─────────────────────────────────────────────────────────────
// AI status
// ─────────────────────────────────────────────────────────────
function updateAIStatus(status) {
  const map = {
    'ai-ppo':      status.ppo      ?? 'ready',
    'ai-regime':   status.regime   ?? 'ready',
    'ai-ensemble': status.ensemble ?? 'ready',
    'ai-rust':     status.rust     ?? 'ready',
    'ai-cpp':      status.cpp      ?? 'ready',
    'ai-julia':    status.julia    ?? 'ready',
  };
  for (const [id, st] of Object.entries(map)) {
    const el = document.getElementById(id);
    el.textContent = st === 'ready' ? '✓ Ready' : st === 'loading' ? '⟳ Loading' : '✗ Offline';
    el.className   = `ai-status ${st}`;
  }
}

// ─────────────────────────────────────────────────────────────
// Trade log
// ─────────────────────────────────────────────────────────────
function addLog(msg, level = 'info') {
  const log  = document.getElementById('trade-log');
  const ts   = new Date().toLocaleTimeString();
  const div  = document.createElement('div');
  div.className   = `log-entry log-${level}`;
  div.textContent = `[${ts}] ${msg}`;
  log.prepend(div);
  while (log.children.length > 50) log.removeChild(log.lastChild);
}

function setOffline() {
  document.getElementById('status-text').textContent = 'Offline';
  document.getElementById('status-dot').className    = 'status-dot halted';
  addLog('Connection to agent lost — retrying...', 'warning');
}

// ─────────────────────────────────────────────────────────────
// Formatters
// ─────────────────────────────────────────────────────────────
function fmt$(v, signed = false) {
  const s = signed && v >= 0 ? '+' : '';
  return s + '$' + Math.abs(v).toLocaleString('en-US', { maximumFractionDigits: 0 });
}
