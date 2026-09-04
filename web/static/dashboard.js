/**
 * OptionAlpha Agent — Real-Time Dashboard Client
 * Polls backend REST endpoints and dynamically updates Greeks, positions, and logs.
 */

document.addEventListener('DOMContentLoaded', () => {
  const clockEl = document.getElementById('clock');
  const equityEl = document.getElementById('equity-val');
  const pnlEl = document.getElementById('pnl-val');
  const varEl = document.getElementById('var-val');
  const deltaEl = document.getElementById('greek-delta');
  const gammaEl = document.getElementById('greek-gamma');
  const vegaEl = document.getElementById('greek-vega');
  const thetaEl = document.getElementById('greek-theta');
  const terminalLog = document.getElementById('terminal-log');

  // 1. UTC Clock
  setInterval(() => {
    const now = new Date();
    clockEl.textContent = now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
  }, 1000);

  // 2. Poll Status Endpoint
  async function fetchStatus() {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) return;
      const data = await res.json();

      if (data.equity !== undefined) {
        equityEl.textContent = `$${data.equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      }
      if (data.daily_pnl !== undefined) {
        const sign = data.daily_pnl >= 0 ? '+' : '';
        const pct = ((data.daily_pnl / 100000.0) * 100).toFixed(2);
        pnlEl.textContent = `${sign}$${data.daily_pnl.toFixed(2)} (${sign}${pct}% today)`;
        pnlEl.className = data.daily_pnl >= 0 ? 'stat-change positive' : 'stat-change negative';
      }
    } catch (e) {
      console.debug('Status poll offline, using simulated telemetry');
    }
  }

  // 3. Poll Positions Endpoint
  async function fetchPositions() {
    try {
      const res = await fetch('/api/positions');
      if (!res.ok) return;
      const positions = await res.json();
      const tbody = document.getElementById('positions-body');
      if (positions && positions.length > 0 && tbody) {
        tbody.innerHTML = '';
        positions.forEach(p => {
          const tr = document.createElement('tr');
          const pnl = p.unrealized_pl || 0.0;
          const sign = pnl >= 0 ? '+' : '';
          tr.innerHTML = `
            <td>${p.symbol}</td>
            <td><span style="color: var(--accent-blue);">${p.asset_class || 'OPTION'}</span></td>
            <td>${p.qty}</td>
            <td>$${(p.avg_cost || 0).toFixed(2)}</td>
            <td>$${(p.market_value ? Math.abs(p.market_value / (p.qty * 100)) : 0).toFixed(2)}</td>
            <td class="${pnl >= 0 ? 'positive' : 'negative'}">${sign}$${pnl.toFixed(2)}</td>
            <td><span style="color: var(--accent-green);">Active Track</span></td>
          `;
          tbody.appendChild(tr);
        });
      }
    } catch (e) {
      // Keep static display
    }
  }

  // Initial & Recurring Polls
  fetchStatus();
  fetchPositions();
  setInterval(fetchStatus, 3000);
  setInterval(fetchPositions, 5000);
});
