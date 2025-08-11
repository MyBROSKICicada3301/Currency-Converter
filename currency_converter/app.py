from __future__ import annotations

import threading
from decimal import Decimal, InvalidOperation
import tkinter as tk
from tkinter import ttk, messagebox

from .currencies import sorted_currency_codes, describe
from .rates import get_rates, format_decimal, DECIMAL_PLACES


class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, master=None, values=None, **kwargs):
        super().__init__(master, values=values or [], **kwargs)
        self._all_values = list(values or [])
        self.bind('<KeyRelease>', self._on_keyrelease)

    def _on_keyrelease(self, event):
        text = self.get().upper()
        matches = [v for v in self._all_values if v.startswith(text)] if text else self._all_values
        self['values'] = matches
        if matches:
            # Keep cursor at end
            self.icursor(tk.END)


class ConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Currency Converter")
        self.geometry("520x280")
        self.minsize(480, 260)

        self.amount_var = tk.StringVar(value="1.00")
        self.from_var = tk.StringVar(value="USD")
        self.to_var = tk.StringVar(value="EUR")
        self.result_var = tk.StringVar(value="...")
        self.status_var = tk.StringVar(value="Loading rates...")

        self._rates = None

        self._build_ui()
        self._load_rates_async()

    def _build_ui(self):
        pad = 10
        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True, padx=pad, pady=pad)

        # Row 1: Amount
        row1 = ttk.Frame(frm)
        row1.pack(fill=tk.X, pady=(0, pad))
        ttk.Label(row1, text="Amount").pack(side=tk.LEFT)
        amt_entry = ttk.Entry(row1, textvariable=self.amount_var, width=15)
        amt_entry.pack(side=tk.LEFT, padx=(8, 0))
        amt_entry.bind('<KeyRelease>', lambda e: self._recompute())

        # Row 2: From / To
        row2 = ttk.Frame(frm)
        row2.pack(fill=tk.X, pady=(0, pad))

        codes = sorted_currency_codes()
        display_values = [f"{c} - {describe(c).split(' - ',1)[1]}" for c in codes]
        code_map = {f"{c} - {describe(c).split(' - ',1)[1]}": c for c in codes}
        self._code_map = code_map

        ttk.Label(row2, text="From").grid(row=0, column=0, sticky=tk.W)
        self.from_cb = AutocompleteCombobox(row2, values=display_values, width=30)
        self.from_cb.grid(row=0, column=1, padx=(8, 18))
        self.from_cb.set("USD - US Dollar")
        self.from_cb.bind('<<ComboboxSelected>>', lambda e: self._on_currency_change())
        self.from_cb.bind('<KeyRelease>', lambda e: self._on_currency_change())

        ttk.Label(row2, text="To").grid(row=0, column=2, sticky=tk.W)
        self.to_cb = AutocompleteCombobox(row2, values=display_values, width=30)
        self.to_cb.grid(row=0, column=3)
        self.to_cb.set("EUR - Euro")
        self.to_cb.bind('<<ComboboxSelected>>', lambda e: self._on_currency_change())
        self.to_cb.bind('<KeyRelease>', lambda e: self._on_currency_change())

        for i in range(4):
            row2.grid_columnconfigure(i, weight=1)

        # Row 3: Result
        row3 = ttk.Frame(frm)
        row3.pack(fill=tk.BOTH, expand=True, pady=(0, pad))
        self.result_label = ttk.Label(row3, textvariable=self.result_var, font=("Segoe UI", 20, "bold"))
        self.result_label.pack(anchor=tk.W)

        # Row 4: Actions
        row4 = ttk.Frame(frm)
        row4.pack(fill=tk.X)
        self.swap_btn = ttk.Button(row4, text="Swap", command=self._swap)
        self.swap_btn.pack(side=tk.LEFT)

        refresh_btn = ttk.Button(row4, text="Refresh rates", command=self._refresh_async)
        refresh_btn.pack(side=tk.LEFT, padx=(8, 0))

        # Status bar
        status = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)

    def _on_currency_change(self):
        self._recompute()

    def _swap(self):
        a = self.from_cb.get()
        b = self.to_cb.get()
        self.from_cb.set(b)
        self.to_cb.set(a)
        self._recompute()

    def _load_rates_async(self):
        def worker():
            try:
                self._rates = get_rates()
                self.status_var.set("Rates loaded")
            except Exception as e:
                self.status_var.set(f"Rates unavailable: {e}")
            finally:
                self._recompute()
        threading.Thread(target=worker, daemon=True).start()

    def _refresh_async(self):
        self.status_var.set("Refreshing rates...")
        self._load_rates_async()

    def _parse_amount(self) -> Decimal:
        txt = self.amount_var.get().strip()
        if not txt:
            return Decimal(0)
        try:
            return Decimal(txt)
        except InvalidOperation:
            return Decimal(0)

    def _get_selected_codes(self):
        def to_code(text: str) -> str:
            if ' - ' in text:
                return text.split(' - ', 1)[0]
            return text.strip().upper()
        return to_code(self.from_cb.get()), to_code(self.to_cb.get())

    def _recompute(self):
        if self._rates is None:
            self.result_var.set("Loading rates...")
            return
        amount = self._parse_amount()
        src, dst = self._get_selected_codes()
        try:
            converted = self._rates.convert(amount, src, dst)
            self.result_var.set(f"{format_decimal(amount, DECIMAL_PLACES)} {src} = {format_decimal(converted, DECIMAL_PLACES)} {dst}")
        except Exception as e:
            self.result_var.set(f"Error: {e}")


def main():
    app = ConverterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
