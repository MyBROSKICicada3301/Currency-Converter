from __future__ import annotations

import threading
import time
import webbrowser
from decimal import Decimal, InvalidOperation
from typing import Optional

from flask import Flask, jsonify, request, Response

from .currencies import sorted_currency_codes, describe, get_flag
from .rates import get_rates, format_decimal, DECIMAL_PLACES, Rates


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
    # Complete, modern, responsive UI with vanilla CSS/JS and currency animations
    html = f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Currency Converter</title>
      <style>
        :root {{
          --bg: #0f172a; /* slate-900 */
          --panel: #111827; /* gray-900 */
          --text: #e5e7eb; /* gray-200 */
          --muted: #9ca3af; /* gray-400 */
          --accent: #22d3ee; /* cyan-400 */
          --accent2: #a78bfa; /* violet-400 */
          --border: #1f2937; /* gray-800 */
          --error: #f87171; /* red-400 */
        }}
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; background: linear-gradient(135deg, #0b1020, #0f172a); color: var(--text); font: 16px/1.4 system-ui, -apple-system, Segoe UI, Roboto, sans-serif; overflow-x: hidden; }}
        /* Animated background canvas */
        #bg {{ position: fixed; inset: 0; width: 100%; height: 100%; z-index: -1; display: block; background: radial-gradient(1200px 600px at 10% 10%, rgba(34,211,238,0.06), transparent), radial-gradient(1000px 500px at 90% 90%, rgba(167,139,250,0.06), transparent); }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 32px 16px; }}
        .card {{ background: rgba(17,24,39,0.85); border: 1px solid var(--border); border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.35); backdrop-filter: blur(6px); }}
        h1 {{ margin: 0 0 16px; font-size: 28px; letter-spacing: 0.3px; }}
        .grid {{ display: grid; gap: 16px; grid-template-columns: 1fr; }}
        @media (min-width: 720px) {{ .grid {{ grid-template-columns: 1fr 1fr; }} }}
        label {{ display:block; margin-bottom: 6px; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
        input, select {{ width: 100%; padding: 12px 14px; border-radius: 10px; border: 1px solid var(--border); background: #0b1220; color: var(--text); outline: none; }}
        input:focus, select:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px rgba(34,211,238,0.15); }}
        .row {{ display:flex; gap: 12px; align-items: end; }}
        .btn {{ padding: 10px 14px; border-radius: 10px; border: 1px solid var(--border); background: linear-gradient(135deg, rgba(34,211,238,0.2), rgba(167,139,250,0.2)); color: var(--text); cursor: pointer; white-space: nowrap; border: none; }}
        .btn:hover {{ filter: brightness(1.1); }}
        .btn:active {{ filter: brightness(0.9); }}
        .result {{ margin-top: 18px; font-size: 22px; font-weight: 700; letter-spacing: .3px; }}
        .status {{ margin-top: 8px; color: var(--muted); font-size: 13px; }}
        .error {{ color: var(--error); }}
        .footer {{ margin-top: 24px; font-size: 12px; color: var(--muted); text-align: right; }}
        .actions {{ margin-top: 16px; display: flex; gap: 12px; }}
      </style>
    </head>
    <body>
      <canvas id="bg" aria-hidden="true"></canvas>
      <div class="container">
        <div class="card">
          <h1>Currency Converter</h1>
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
          <div class="footer">Base: EUR · Precision: {DECIMAL_PLACES} dp</div>
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

        async function loadCurrencies() {{
          const res = await fetch('/api/currencies');
          const data = await res.json();
          const opts = data.currencies.map(c => `<option value="${{c.code}}">${{c.flag}} ${{c.code}} - ${{c.name}}</option>`).join('');
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
              resultEl.textContent = `${{data.src_flag}} ${{data.formatted_amount}} ${{data.src}} = ${{data.dst_flag}} ${{data.formatted_converted}} ${{data.dst}}`;
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

        $("swap").addEventListener('click', () => {{
          const a = fromEl.value; fromEl.value = toEl.value; toEl.value = a; convert();
        }});

        $("refresh").addEventListener('click', refreshRates);

        [amountEl, fromEl, toEl].forEach(el => el.addEventListener('input', () => {{
          // Small debounce
          clearTimeout(window.__t);
          window.__t = setTimeout(convert, 120);
        }}));

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
          await loadCurrencies();
          // try an initial convert; backend may still be loading
          await convert();
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
        # Extract just the name part after "flag CODE - "
        parts = full_desc.split(" - ", 1)
        if len(parts) == 2:
            flag_code, name = parts
            flag = flag_code.split()[0]  # Extract just the flag emoji
            items.append({"code": code, "name": name, "flag": flag})
        else:
            items.append({"code": code, "name": "Unknown", "flag": "❓"})
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
        "src_flag": get_flag(src),
        "dst_flag": get_flag(dst),
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
