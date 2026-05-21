"""WOW DB Project - Tkinter GUI
World of Warcraft 3.3.5a Item List (Tkinter refactor)

This script opens a small GUI to search the local `wowdb.sqlite3` database
for items by name and export results to HTML.
"""

VERSION = "0.6 Copilot Powered"

import os
import sqlite3
import sys
import html
from tkinter import Tk, StringVar, N, S, E, W, END
from tkinter import ttk, messagebox


class Encyclopedia:
    def __init__(self, db_name=None):
        if db_name is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_name = os.path.join(script_dir, "wowdb.sqlite3")
        self.db_name = db_name
        self.con = None
        self.cur = None

    def on_load(self):
        try:
            self.con = sqlite3.connect(self.db_name, timeout=20)
            self.cur = self.con.cursor()
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", f"Cannot open database: {error}")
            raise

    def search_items(self, term):
        term = term or ""
        try:
            self.cur.execute(
                "SELECT entry, name, itemlevel, requiredlevel FROM item_list WHERE name LIKE ? ORDER BY entry",
                (f"%{term}%",),
            )
            return self.cur.fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Query Error", str(error))
            return []

    def close(self):
        if self.cur:
            try:
                self.cur.close()
            except Exception:
                pass
        if self.con:
            try:
                self.con.close()
            except Exception:
                pass


class WOWDBApp:
    def __init__(self, root, encyclopedia: Encyclopedia):
        self.root = root
        self.ency = encyclopedia
        self.root.title(f"WOW DB Item List - v{VERSION}")

        self.search_var = StringVar()
        self._sort_column = None
        self._sort_reverse = False
        self._column_headings = {
            "entry": "Entry",
            "name": "Name",
            "itemlevel": "Item Level",
            "requiredlevel": "Req Level",
        }

        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.grid(row=0, column=0, sticky=(N, S, E, W))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        search_entry = ttk.Entry(frm, textvariable=self.search_var, width=40)
        search_entry.grid(row=0, column=0, padx=(0, 6), pady=(0, 6), sticky=(W))
        search_entry.bind('<Return>', lambda e: self.on_search())

        search_btn = ttk.Button(frm, text="Search", command=self.on_search)
        search_btn.grid(row=0, column=1, padx=(0, 6), pady=(0, 6))

        export_btn = ttk.Button(frm, text="Export HTML", command=self.on_export)
        export_btn.grid(row=0, column=2, padx=(0, 6), pady=(0, 6))

        quit_btn = ttk.Button(frm, text="Quit", command=self.on_quit)
        quit_btn.grid(row=0, column=3, padx=(0, 0), pady=(0, 6))

        cols = ("entry", "name", "itemlevel", "requiredlevel")
        self.tree = ttk.Treeview(frm, columns=cols, show="headings", height=20)
        self.tree.heading("entry", text=self._column_headings["entry"], command=lambda: self._on_heading_click("entry"))
        self.tree.heading("name", text=self._column_headings["name"], command=lambda: self._on_heading_click("name"))
        self.tree.heading("itemlevel", text=self._column_headings["itemlevel"], command=lambda: self._on_heading_click("itemlevel"))
        self.tree.heading("requiredlevel", text=self._column_headings["requiredlevel"], command=lambda: self._on_heading_click("requiredlevel"))
        self.tree.column("entry", width=80, anchor="center")
        self.tree.column("name", width=400)
        self.tree.column("itemlevel", width=100, anchor="center")
        self.tree.column("requiredlevel", width=100, anchor="center")

        vsb = ttk.Scrollbar(frm, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.grid(row=1, column=0, columnspan=4, sticky=(N, S, E, W))
        vsb.grid(row=1, column=4, sticky=(N, S))

        frm.rowconfigure(1, weight=1)
        frm.columnconfigure(0, weight=1)

        self.status = ttk.Label(frm, text="Ready")
        self.status.grid(row=2, column=0, columnspan=4, sticky=(W), pady=(6, 0))

    def on_search(self):
        term = self.search_var.get().strip()
        results = self.ency.search_items(term)
        self._populate_tree(results)
        self.status.config(text=f"{len(results)} item(s) found")

    def _populate_tree(self, rows):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in rows:
            self.tree.insert("", END, values=r)

    def _on_heading_click(self, column):
        columns = ("entry", "name", "itemlevel", "requiredlevel")
        column_index = columns.index(column)

        items = [(self.tree.item(item_id, "values"), item_id) for item_id in self.tree.get_children()]
        if column in ("entry", "itemlevel", "requiredlevel"):
            key = lambda item: int(item[0][column_index]) if item[0][column_index] != "" else -1
        else:
            key = lambda item: item[0][column_index].lower()

        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False

        items.sort(key=key, reverse=self._sort_reverse)
        self._refresh_heading_arrows()

        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        for values, _ in items:
            self.tree.insert("", END, values=values)

    def _refresh_heading_arrows(self):
        for column, heading in self._column_headings.items():
            if column == self._sort_column:
                arrow = " ▲" if not self._sort_reverse else " ▼"
                self.tree.heading(column, text=f"{heading}{arrow}")
            else:
                self.tree.heading(column, text=heading)

    def on_export(self):
        rows = [self.tree.item(i, "values") for i in self.tree.get_children()]
        if not rows:
            messagebox.showinfo("Export", "No results to export")
            return

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "results.html")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(self._rows_to_html(rows))
            messagebox.showinfo("Export", f"File '{output_path}' saved in the script folder")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _rows_to_html(self, rows):
        head = "<table border=1><thead><tr><th>Entry</th><th>Name</th><th>Item Level</th><th>Req Level</th></tr></thead><tbody>"
        body = []
        for r in rows:
            # escape HTML
            entry = html.escape(str(r[0]))
            name = html.escape(str(r[1]))
            itemlevel = html.escape(str(r[2]))
            req = html.escape(str(r[3]))
            body.append(f"<tr><td>{entry}</td><td>{name}</td><td>{itemlevel}</td><td>{req}</td></tr>")
        tail = "</tbody></table>"
        return f"<html><head><meta charset=\"utf-8\"><title>WOW DB Results</title></head><body><h2>Search Results</h2>{head}{''.join(body)}{tail}</body></html>"

    def on_quit(self):
        self.ency.close()
        self.root.quit()


def main():
    enc = Encyclopedia()
    try:
        enc.on_load()
    except Exception:
        return

    root = Tk()
    app = WOWDBApp(root, enc)
    root.geometry("800x600")
    root.mainloop()


if __name__ == "__main__":
    main()