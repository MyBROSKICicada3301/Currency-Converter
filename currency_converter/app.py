from __future__ import annotations

import subprocess
import sys
import threading
import time
import webbrowser
from decimal import Decimal, InvalidOperation
from typing import Optional


def install_requirements():
    """Automatically install required packages if they're missing"""
    required_packages = [
        ("flask", "flask>=3.0,<4"),
        ("yfinance", "yfinance>=0.2.0"),
        ("requests", "requests>=2.31.0")
    ]
    
    missing_packages = []
    
    print("Checking dependencies...")
    for package_name, package_spec in required_packages:
        try:
            __import__(package_name)
            print(f"✓ {package_name} is available")
        except ImportError:
            print(f"✗ {package_name} is missing")
            missing_packages.append(package_spec)
    
    if missing_packages:
        print(f"\n📦 Installing missing dependencies: {', '.join(missing_packages)}")
        print("This may take a moment...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            print("✅ Dependencies installed successfully!\n")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("💡 Please install manually using: pip install -r requirements.txt")
            sys.exit(1)
    else:
        print("✅ All dependencies are available!\n")


# Install requirements before importing other modules
install_requirements()

from flask import Flask, jsonify, request, Response

try:
    # Try relative import first (when run as module)
    from .currencies import sorted_currency_codes, describe
    from .rates import get_rates, format_decimal, DECIMAL_PLACES, Rates, get_historical_data
except ImportError:
    # Fall back to absolute import (when run directly)
    from currencies import sorted_currency_codes, describe
    from rates import get_rates, format_decimal, DECIMAL_PLACES, Rates, get_historical_data


app = Flask(__name__)

# Shared rates cache
_rates_lock = threading.Lock()
_rates: Optional[Rates] = None


def _ensure_rates_loaded() -> None:
    global _rates
    with _rates_lock:
        if _rates is None:
            _rates = get_rates()


def _load_rates_async() -> None:
    def worker():
        try:
            _ensure_rates_loaded()
        except Exception:
            # Keep None, UI will show error on convert
            pass
    threading.Thread(target=worker, daemon=True).start()


@app.get("/")
def index() -> Response:
    html = f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Currency Converter</title>
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
      <style>
        :root {{
          /* Dark Theme (Default) */
          --bg: #0f172a; /* slate-900 */
          --panel: #111827; /* gray-900 */
          --text: #e5e7eb; /* gray-200 */
          --muted: #9ca3af; /* gray-400 */
          --accent: #22d3ee; /* cyan-400 */
          --accent2: #a78bfa; /* violet-400 */
          --border: #1f2937; /* gray-800 */
          --error: #f87171; /* red-400 */
          --success: #34d399; /* emerald-400 */
        }}

        /* Light Theme */
        [data-theme="light"] {{
          --bg: #f8fafc; /* slate-50 */
          --panel: #ffffff; /* white */
          --text: #1e293b; /* slate-800 */
          --muted: #64748b; /* slate-500 */
          --accent: #0ea5e9; /* sky-500 */
          --accent2: #8b5cf6; /* violet-500 */
          --border: #e2e8f0; /* slate-200 */
          --error: #ef4444; /* red-500 */
          --success: #10b981; /* emerald-500 */
        }}

        /* Blue Theme */
        [data-theme="blue"] {{
          --bg: #0c1426; /* blue-950 */
          --panel: #1e293b; /* slate-800 */
          --text: #f1f5f9; /* slate-100 */
          --muted: #94a3b8; /* slate-400 */
          --accent: #3b82f6; /* blue-500 */
          --accent2: #6366f1; /* indigo-500 */
          --border: #334155; /* slate-700 */
          --error: #f87171; /* red-400 */
          --success: #22d3ee; /* cyan-400 */
        }}

        /* Green Theme */
        [data-theme="green"] {{
          --bg: #0f1419; /* emerald-950 */
          --panel: #1f2937; /* gray-800 */
          --text: #ecfdf5; /* emerald-50 */
          --muted: #a1a1aa; /* zinc-400 */
          --accent: #10b981; /* emerald-500 */
          --accent2: #22c55e; /* green-500 */
          --border: #374151; /* gray-700 */
          --error: #f87171; /* red-400 */
          --success: #34d399; /* emerald-400 */
        }}

        /* Purple Theme */
        [data-theme="purple"] {{
          --bg: #1a0b2e; /* custom purple-950 */
          --panel: #2d1b4e; /* custom purple-900 */
          --text: #f3e8ff; /* purple-50 */
          --muted: #a855f7; /* purple-500 */
          --accent: #8b5cf6; /* violet-500 */
          --accent2: #a855f7; /* purple-500 */
          --border: #4c1d95; /* purple-800 */
          --error: #f87171; /* red-400 */
          --success: #34d399; /* emerald-400 */
        }}

        /* Rose Theme */
        [data-theme="rose"] {{
          --bg: #1f0a13; /* custom rose-950 */
          --panel: #3f1725; /* custom rose-900 */
          --text: #fdf2f8; /* pink-50 */
          --muted: #f472b6; /* pink-400 */
          --accent: #ec4899; /* pink-500 */
          --accent2: #f43f5e; /* rose-500 */
          --border: #881337; /* rose-800 */
          --error: #f87171; /* red-400 */
          --success: #34d399; /* emerald-400 */
        }}

        /* Base styles */
        * {{ box-sizing: border-box; }}
        body {{ 
          margin: 0; 
          background: linear-gradient(135deg, var(--bg), var(--panel)); 
          color: var(--text); 
          font: 16px/1.4 system-ui, -apple-system, Segoe UI, Roboto, sans-serif; 
          overflow-x: hidden; 
          transition: background 0.3s ease, color 0.3s ease;
        }}
        /* Animated background canvas */
        #bg {{ 
          position: fixed; 
          inset: 0; 
          width: 100%; 
          height: 100%; 
          z-index: -1; 
          display: block; 
        }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 32px 16px; }}
        .card {{ 
          background: var(--panel); 
          border: 1px solid var(--border); 
          border-radius: 16px; 
          padding: 24px; 
          box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
          backdrop-filter: blur(6px); 
          transition: background 0.3s ease, border-color 0.3s ease;
        }}
        h1 {{ margin: 0 0 16px; font-size: 28px; letter-spacing: 0.3px; display: flex; justify-content: space-between; align-items: center; }}
        .grid {{ display: grid; gap: 16px; grid-template-columns: 1fr; }}
        @media (min-width: 720px) {{ .grid {{ grid-template-columns: 1fr 1fr; }} }}
        label {{ display:block; margin-bottom: 6px; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
        input, select {{ 
          width: 100%; 
          padding: 12px 14px; 
          border-radius: 10px; 
          border: 1px solid var(--border); 
          background: var(--bg); 
          color: var(--text); 
          outline: none; 
          transition: border-color 0.3s ease, background 0.3s ease;
        }}
        input:focus, select:focus {{ 
          border-color: var(--accent); 
          box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.15); 
        }}
        .row {{ display:flex; gap: 12px; align-items: end; }}
        .btn {{ 
          padding: 10px 14px; 
          border-radius: 10px; 
          border: 1px solid var(--border); 
          background: var(--accent); 
          color: var(--bg); 
          cursor: pointer; 
          white-space: nowrap; 
          font-weight: 600;
          transition: all 0.3s ease;
        }}
        .btn:hover {{ filter: brightness(1.1); }}
        .btn:active {{ filter: brightness(0.9); }}
        .result {{ margin-top: 18px; font-size: 22px; font-weight: 700; letter-spacing: .3px; }}
        .status {{ margin-top: 8px; color: var(--muted); font-size: 13px; }}
        .error {{ color: var(--error); }}
        .footer {{ margin-top: 24px; font-size: 12px; color: var(--muted); text-align: right; }}
        .actions {{ margin-top: 16px; display: flex; gap: 12px; }}
        .chart-section {{ margin-top: 24px; }}
        .chart-container {{ position: relative; height: 300px; margin-top: 16px; }}
        .chart-controls {{ display: flex; gap: 8px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }}
        .period-btn {{ 
          padding: 6px 12px; 
          border-radius: 6px; 
          border: 1px solid var(--border); 
          background: var(--panel); 
          color: var(--muted); 
          cursor: pointer; 
          font-size: 12px; 
          transition: all 0.3s ease;
        }}
        .period-btn.active {{ background: var(--accent); color: var(--bg); }}
        .period-btn:hover {{ filter: brightness(1.1); }}
        
        /* Theme Selector Styles */
        .theme-selector {{ 
          display: flex; 
          gap: 4px; 
          align-items: center;
        }}
        .theme-btn {{ 
          width: 24px; 
          height: 24px; 
          border-radius: 50%; 
          border: 2px solid var(--border); 
          cursor: pointer; 
          transition: all 0.3s ease; 
          position: relative;
        }}
        .theme-btn:hover {{ transform: scale(1.1); }}
        .theme-btn.active {{ 
          border-color: #FFA500; 
          box-shadow: 0 0 0 2px #FFA500; 
          transform: scale(1.05);
        }}
        .theme-btn[data-theme="dark"] {{ background: linear-gradient(135deg, #0f172a, #22d3ee); }}
        .theme-btn[data-theme="light"] {{ background: linear-gradient(135deg, #ffffff, #0ea5e9); }}
        .theme-btn[data-theme="blue"] {{ background: linear-gradient(135deg, #0c1426, #3b82f6); }}
        .theme-btn[data-theme="green"] {{ background: linear-gradient(135deg, #0f1419, #10b981); }}
        .theme-btn[data-theme="purple"] {{ background: linear-gradient(135deg, #1a0b2e, #8b5cf6); }}
        .theme-btn[data-theme="rose"] {{ background: linear-gradient(135deg, #1f0a13, #ec4899); }}
      </style>
    </head>
    <body>
      <canvas id="bg" aria-hidden="true"></canvas>
      <div class="container">
        <div class="card">
          <h1>
            Currency Converter
            <div class="theme-selector" title="Choose Theme">
              <div class="theme-btn active" data-theme="dark"></div>
              <div class="theme-btn" data-theme="light"></div>
              <div class="theme-btn" data-theme="blue"></div>
              <div class="theme-btn" data-theme="green"></div>
              <div class="theme-btn" data-theme="purple"></div>
              <div class="theme-btn" data-theme="rose"></div>
            </div>
          </h1>
          <div class="grid">
            <div>
              <label for="amount">Amount</label>
              <input id="amount" type="text" value="1.00" />
            </div>
            <div class="row">
              <div style="flex:1">
                <label for="from">From</label>
                <select id="from"></select>
              </div>
              <button class="btn" id="swap" title="Swap currencies">⇄</button>
              <div style="flex:1">
                <label for="to">To</label>
                <select id="to"></select>
              </div>
            </div>
          </div>
          <div class="result" id="result">...</div>
          <div class="actions">
            <button class="btn" id="refresh">🔄 Refresh Rates</button>
          </div>
          <div class="status" id="status">Loading rates...</div>
          
          <!-- Chart Section -->
          <div class="chart-section">
            <h3 style="margin: 0 0 12px; font-size: 18px;">Exchange Rate History</h3>
            <div class="chart-controls">
              <span style="font-size: 12px; color: var(--muted);">Period:</span>
              <button class="period-btn active" data-period="1mo">1M</button>
              <button class="period-btn" data-period="3mo">3M</button>
              <button class="period-btn" data-period="6mo">6M</button>
              <button class="period-btn" data-period="1y">1Y</button>
              <button class="period-btn" data-period="2y">2Y</button>
            </div>
            <div class="chart-container">
              <canvas id="chart"></canvas>
            </div>
          </div>
          
          <div class="footer" style="display: flex; justify-content: space-between; align-items: center;">
            <span>Data: Yahoo Finance</span>
            <span>Base: EUR · Precision: {DECIMAL_PLACES} dp</span>
          </div>
        </div>
        <div style="text-align: center; margin-top: 16px; font-size: 11px; color: var(--muted); opacity: 0.6;">
          Created by MyBROSKICicada3301
        </div>
      </div>
      <script>
        const $ = (id) => document.getElementById(id);
        const amountEl = $("amount");
        const fromEl = $("from");
        const toEl = $("to");
        const resultEl = $("result");
        const statusEl = $("status");
        const bg = $("bg");
        
        // Chart variables
        let chartInstance = null;
        let currentPeriod = '1mo';
        
        // Theme functions
        function setTheme(theme) {{
          document.body.setAttribute('data-theme', theme);
          localStorage.setItem('preferred-theme', theme);
          
          // Update active theme button
          document.querySelectorAll('.theme-btn').forEach(btn => {{
            btn.classList.remove('active');
          }});
          document.querySelector(`[data-theme="${{theme}}"]`).classList.add('active');
          
          // Update canvas background
          updateCanvasBackground();
          
          // Update chart colors if chart exists
          if (chartInstance) {{
            updateChartTheme();
          }}
        }}
        
        function updateCanvasBackground() {{
          const theme = document.body.getAttribute('data-theme') || 'dark';
          const style = getComputedStyle(document.body);
          const accent = style.getPropertyValue('--accent').trim();
          const accent2 = style.getPropertyValue('--accent2').trim();
          
          // Update background canvas gradient based on theme
          if (bg) {{
            const gradients = {{
              'dark': `radial-gradient(1200px 600px at 10% 10%, rgba(34,211,238,0.06), transparent), radial-gradient(1000px 500px at 90% 90%, rgba(167,139,250,0.06), transparent)`,
              'light': `radial-gradient(1200px 600px at 10% 10%, rgba(14,165,233,0.06), transparent), radial-gradient(1000px 500px at 90% 90%, rgba(139,92,246,0.06), transparent)`,
              'blue': `radial-gradient(1200px 600px at 10% 10%, rgba(59,130,246,0.06), transparent), radial-gradient(1000px 500px at 90% 90%, rgba(99,102,241,0.06), transparent)`,
              'green': `radial-gradient(1200px 600px at 10% 10%, rgba(16,185,129,0.06), transparent), radial-gradient(1000px 500px at 90% 90%, rgba(34,197,94,0.06), transparent)`,
              'purple': `radial-gradient(1200px 600px at 10% 10%, rgba(139,92,246,0.06), transparent), radial-gradient(1000px 500px at 90% 90%, rgba(168,85,247,0.06), transparent)`,
              'rose': `radial-gradient(1200px 600px at 10% 10%, rgba(236,72,153,0.06), transparent), radial-gradient(1000px 500px at 90% 90%, rgba(244,63,94,0.06), transparent)`
            }};
            bg.style.background = gradients[theme] || gradients['dark'];
          }}
        }}
        
        function updateChartTheme() {{
          if (!chartInstance) return;
          
          const style = getComputedStyle(document.body);
          const textColor = style.getPropertyValue('--text').trim();
          const mutedColor = style.getPropertyValue('--muted').trim();
          const accentColor = style.getPropertyValue('--accent').trim();
          
          chartInstance.options.plugins.legend.labels.color = textColor;
          chartInstance.options.scales.x.ticks.color = mutedColor;
          chartInstance.options.scales.y.ticks.color = mutedColor;
          chartInstance.options.scales.x.grid.color = mutedColor + '33';
          chartInstance.options.scales.y.grid.color = mutedColor + '33';
          chartInstance.data.datasets[0].borderColor = accentColor;
          chartInstance.data.datasets[0].backgroundColor = accentColor + '1A';
          chartInstance.update();
        }}
        
        // Load saved theme
        function loadSavedTheme() {{
          const savedTheme = localStorage.getItem('preferred-theme') || 'dark';
          setTheme(savedTheme);
        }}

        async function loadCurrencies() {{
          const res = await fetch('/api/currencies');
          const data = await res.json();
          const opts = data.currencies.map(c => `<option value="${{c.code}}">${{c.code}} - ${{c.name}}</option>`).join('');
          fromEl.innerHTML = opts;
          toEl.innerHTML = opts;
          fromEl.value = 'USD';
          toEl.value = 'EUR';
        }}

        async function convert() {{
          const amount = amountEl.value.trim();
          const src = fromEl.value; const dst = toEl.value;
          if (!amount) return;
          try {{
            const res = await fetch(`/api/convert?amount=${{encodeURIComponent(amount)}}&src=${{src}}&dst=${{dst}}`);
            const data = await res.json();
            if (res.ok) {{
              resultEl.textContent = `${{data.formatted_amount}} ${{data.src}} = ${{data.formatted_converted}} ${{data.dst}}`;
              statusEl.textContent = 'Rates loaded';
              statusEl.classList.remove('error');
            }} else {{
              resultEl.textContent = '...';
              statusEl.textContent = data.error || 'Error';
              statusEl.classList.add('error');
            }}
          }} catch (e) {{
            statusEl.textContent = 'Network error';
            statusEl.classList.add('error');
          }}
        }}

        async function refreshRates() {{
          statusEl.textContent = 'Refreshing rates...';
          statusEl.classList.remove('error');
          try {{
            await fetch('/api/refresh', {{ method: 'POST' }});
            await convert();
          }} catch (e) {{
            statusEl.textContent = 'Refresh failed';
            statusEl.classList.add('error');
          }}
        }}

        // Chart functions
        async function loadChart() {{
          const from = fromEl.value;
          const to = toEl.value;
          
          try {{
            const res = await fetch(`/api/historical?from=${{from}}&to=${{to}}&period=${{currentPeriod}}`);
            const data = await res.json();
            
            if (res.ok && data.data && data.data.length > 0) {{
              updateChart(data);
            }} else {{
              console.log('No historical data available');
            }}
          }} catch (e) {{
            console.log('Failed to load chart data:', e);
          }}
        }}

        function updateChart(data) {{
          const ctx = $('chart').getContext('2d');
          
          if (chartInstance) {{
            chartInstance.destroy();
          }}

          const chartData = data.data.map(point => ({{
            x: new Date(point.date),
            y: point.rate
          }}));

          // Get current theme colors
          const style = getComputedStyle(document.body);
          const accentColor = style.getPropertyValue('--accent').trim();
          const textColor = style.getPropertyValue('--text').trim();
          const mutedColor = style.getPropertyValue('--muted').trim();

          chartInstance = new Chart(ctx, {{
            type: 'line',
            data: {{
              datasets: [{{
                label: `${{data.from}} to ${{data.to}}`,
                data: chartData,
                borderColor: accentColor,
                backgroundColor: accentColor + '1A',
                borderWidth: 2,
                fill: true,
                tension: 0.1
              }}]
            }},
            options: {{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {{
                legend: {{
                  labels: {{
                    color: textColor
                  }}
                }}
              }},
              scales: {{
                x: {{
                  type: 'time',
                  time: {{
                    displayFormats: {{
                      day: 'MMM dd',
                      week: 'MMM dd',
                      month: 'MMM yyyy'
                    }}
                  }},
                  ticks: {{
                    color: mutedColor
                  }},
                  grid: {{
                    color: mutedColor + '33'
                  }}
                }},
                y: {{
                  ticks: {{
                    color: mutedColor
                  }},
                  grid: {{
                    color: mutedColor + '33'
                  }}
                }}
              }}
            }}
          }});
        }}

        $("swap").addEventListener('click', () => {{
          const a = fromEl.value; fromEl.value = toEl.value; toEl.value = a; 
          convert();
          loadChart();
        }});

        $("refresh").addEventListener('click', refreshRates);

        [amountEl, fromEl, toEl].forEach(el => el.addEventListener('input', () => {{
          // Small debounce
          clearTimeout(window.__t);
          window.__t = setTimeout(() => {{
            convert();
            if (el === fromEl || el === toEl) {{
              loadChart();
            }}
          }}, 120);
        }}));

        // Period button event listeners
        document.querySelectorAll('.period-btn').forEach(btn => {{
          btn.addEventListener('click', () => {{
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentPeriod = btn.dataset.period;
            loadChart();
          }});
        }});

        // Theme button event listeners
        document.querySelectorAll('.theme-btn').forEach(btn => {{
          btn.addEventListener('click', () => {{
            setTheme(btn.dataset.theme);
          }});
        }});

        // ===== Animated background of moving currency symbols =====
        (function currencyAnimation() {{
          const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          if (!bg || prefersReduced) return; // Respect reduced motion
          const ctx = bg.getContext('2d');
          const DPR = Math.min(window.devicePixelRatio || 1, 2);
          let W, H, running = true;
          const SYMBOLS = ['$', '€', '£', '¥', '₩', '₹', '₽', '₺', '₴', '₫'];
          const COLORS = ['#22d3ee', '#a78bfa', '#60a5fa', '#34d399', '#f472b6'];
          let particles = [];

          function resize() {{
            W = Math.floor(window.innerWidth);
            H = Math.floor(window.innerHeight);
            bg.width = Math.floor(W * DPR);
            bg.height = Math.floor(H * DPR);
            bg.style.width = W + 'px';
            bg.style.height = H + 'px';
            ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
          }}

          function spawn(count) {{
            for (let i = 0; i < count; i++) {{
              const size = 14 + Math.random() * 28; // 14 – 42px
              particles.push({{
                x: Math.random() * W,
                y: Math.random() * H,
                vx: (-0.2 + Math.random() * 0.4) * (size/24),
                vy: (0.2 + Math.random() * 0.6) * (size/26),
                s: size,
                a: 0.25 + Math.random() * 0.55,
                sym: SYMBOLS[(Math.random() * SYMBOLS.length) | 0],
                col: COLORS[(Math.random() * COLORS.length) | 0],
                rot: Math.random() * Math.PI * 2,
                rv: (-0.005 + Math.random()*0.01),
              }});
            }}
          }}

          function step() {{
            if (!running) return;
            ctx.clearRect(0, 0, W, H);
            for (let p of particles) {{
              p.x += p.vx; p.y += p.vy; p.rot += p.rv;
              if (p.x < -50) p.x = W + 50; if (p.x > W + 50) p.x = -50;
              if (p.y > H + 60) {{ p.y = -40; p.x = Math.random() * W; }}
              ctx.save();
              ctx.translate(p.x, p.y);
              ctx.rotate(p.rot);
              ctx.globalAlpha = p.a;
              ctx.fillStyle = p.col;
              ctx.font = `700 ${{p.s}}px system-ui, Segoe UI, Roboto, sans-serif`;
              ctx.fillText(p.sym, -p.s*0.5, p.s*0.5);
              ctx.restore();
            }}
            requestAnimationFrame(step);
          }}

          function init() {{
            resize();
            particles = [];
            const density = Math.max(22, Math.floor((W*H) / 38000)); // scale with screen size
            spawn(density);
            step();
          }}

          window.addEventListener('resize', () => {{
            resize();
            // keep count roughly consistent
            const target = Math.max(22, Math.floor((W*H) / 38000));
            if (particles.length < target) spawn(target - particles.length);
            else if (particles.length > target) particles.length = target;
          }});

          document.addEventListener('visibilitychange', () => {{ running = document.visibilityState === 'visible'; if (running) step(); }});
          init();
        }})();

        (async function init() {{
          // Load saved theme first
          loadSavedTheme();
          
          await loadCurrencies();
          // try an initial convert; backend may still be loading
          await convert();
          // Load initial chart
          await loadChart();
        }})();
      </script>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")


@app.get("/api/currencies")
def currencies_endpoint():
    items = []
    for code in sorted_currency_codes():
        full_desc = describe(code)
        # Extract just the name part after "CODE - "
        parts = full_desc.split(" - ", 1)
        if len(parts) == 2:
            flag_code, name = parts
            items.append({"code": code, "name": name})
        else:
            items.append({"code": code, "name": "Unknown"})
    return jsonify({"currencies": items})


@app.get("/api/convert")
def convert_endpoint():
    global _rates
    amt_str = request.args.get("amount", "").strip()
    src = (request.args.get("src") or "").upper().strip()
    dst = (request.args.get("dst") or "").upper().strip()
    if not amt_str:
        return jsonify({"error": "Amount required"}), 400
    try:
        amount = Decimal(amt_str)
    except InvalidOperation:
        return jsonify({"error": "Invalid amount"}), 400

    # Ensure rates
    if _rates is None:
        try:
            _ensure_rates_loaded()
        except Exception as e:
            return jsonify({"error": f"Rates unavailable: {e}"}), 503

    try:
        with _rates_lock:
            r = _rates
            if r is None:
                raise RuntimeError("Rates not loaded")
            converted = r.convert(amount, src, dst)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "amount": float(amount),
        "src": src,
        "dst": dst,
        "converted": float(converted),
        "formatted_amount": format_decimal(amount, DECIMAL_PLACES),
        "formatted_converted": format_decimal(converted, DECIMAL_PLACES),
    })


@app.post("/api/refresh")
def refresh_endpoint():
    global _rates
    def worker():
        try:
            fresh = get_rates(use_cache=False)
            with _rates_lock:
                globals()["_rates"] = fresh
        except Exception:
            pass
    threading.Thread(target=worker, daemon=True).start()
    return jsonify({"status": "refreshing"})


@app.get("/api/historical")
def historical_endpoint():
    from_currency = (request.args.get("from") or "").upper().strip()
    to_currency = (request.args.get("to") or "").upper().strip()
    period = request.args.get("period", "1mo").strip()
    
    if not from_currency or not to_currency:
        return jsonify({"error": "Both 'from' and 'to' currencies required"}), 400
    
    # Validate period
    valid_periods = ["1mo", "3mo", "6mo", "1y", "2y"]
    if period not in valid_periods:
        period = "1mo"
    
    try:
        historical_data = get_historical_data(from_currency, to_currency, period)
        return jsonify({
            "from": from_currency,
            "to": to_currency,
            "period": period,
            "data": historical_data
        })
    except Exception as e:
        return jsonify({"error": f"Failed to fetch historical data: {e}"}), 500


def main(host: str = "127.0.0.1", port: int = 5000, open_browser: bool = True) -> None:
    # Preload rates in background and optionally open the browser
    _load_rates_async()
    if open_browser:
        def openit():
            # Give the server a moment to start
            time.sleep(0.6)
            try:
                webbrowser.open(f"http://{host}:{port}")
            except Exception:
                pass
        threading.Thread(target=openit, daemon=True).start()
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
