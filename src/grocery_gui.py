"""
grocery_gui.py
Menu Builder window — built with tkinter (stdlib, no extra install needed).

Replaced appJar, which is unmaintained and broken on Python 3.13+.
tkinter ships with every standard Python installation on Windows, macOS,
and Linux (python3-tk package on Debian/Ubuntu).

Layout (three columns):
  Left   — scrollable recipe list + tag-filter entry + action buttons
  Middle — random suggestion panel
  Right  — current week's menu + remove button
"""

__author__ = 'Joe'

import random
import tkinter as tk
from tkinter import ttk


def recipeGUI(selected_items: list, recipe_collection) -> bool:
    """
    Display the Menu Builder window (blocks until the user closes it).

    Parameters
    ----------
    selected_items    : mutable list; chosen recipe names are appended here.
    recipe_collection : RecipeCollection with timestamps already applied.

    Returns
    -------
    bool : True if the user wants to post to Todoist, False otherwise.
    """

    # ------------------------------------------------------------------ data
    all_recipe_names: list = recipe_collection.get_recipe_names([])
    all_recipe_names = [n for n in all_recipe_names if not n.startswith("No recipes")]
    suggest_pool = list(all_recipe_names)

    # ------------------------------------------------------------------ root window
    root = tk.Tk()
    root.title("Menu Builder")
    root.configure(bg="#e8f4f8")
    root.resizable(True, True)
    root.minsize(900, 550)

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TButton",        font=("Helvetica", 11), padding=4)
    style.configure("Accent.TButton", font=("Helvetica", 11, "bold"),
                    foreground="white", background="#e07b00")
    style.configure("TCheckbutton",   background="#ffffff", font=("Helvetica", 11))
    style.configure("TEntry",         font=("Helvetica", 11), padding=4)
    style.configure("Header.TLabel",  font=("Helvetica", 12, "bold"),
                    background="#e07b00", foreground="white", padding=6, anchor="center")
    style.configure("Sub.TLabel",     font=("Helvetica", 11), background="#e8f4f8")

    # ================================================================== LEFT — recipe list
    left_frame = tk.Frame(root, bg="#e8f4f8", padx=8, pady=8)
    left_frame.grid(row=0, column=0, sticky="nsew", padx=(8, 4), pady=8)

    ttk.Label(left_frame, text="Recipes", style="Header.TLabel").pack(fill="x")

    filter_frame = tk.Frame(left_frame, bg="#e8f4f8")
    filter_frame.pack(fill="x", pady=(6, 0))
    ttk.Label(filter_frame, text="Filter by tag:", style="Sub.TLabel").pack(side="left")
    tag_var = tk.StringVar()
    ttk.Entry(filter_frame, textvariable=tag_var, width=20).pack(side="left", padx=4)

    list_outer = tk.Frame(left_frame, bg="#ffffff", relief="sunken", bd=1)
    list_outer.pack(fill="both", expand=True, pady=6)

    canvas = tk.Canvas(list_outer, bg="#ffffff", highlightthickness=0)
    scrollbar = ttk.Scrollbar(list_outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    inner_frame = tk.Frame(canvas, bg="#ffffff")
    canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>",      lambda e: canvas.itemconfig(canvas_window, width=e.width))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    check_vars: dict = {}
    check_widgets: dict = {}

    def _populate_checklist(names: list) -> None:
        for w in inner_frame.winfo_children():
            w.destroy()
        check_vars.clear()
        check_widgets.clear()
        for name in sorted(names):
            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(inner_frame, text=name, variable=var,
                                bg="#ffffff", activebackground="#ddeeff",
                                font=("Helvetica", 11), anchor="w")
            cb.pack(fill="x", padx=4, pady=1)
            check_vars[name] = var
            check_widgets[name] = cb

    _populate_checklist(all_recipe_names)

    def _filter_recipes():
        tags = tag_var.get().split()
        filtered = recipe_collection.get_recipe_names(tags)
        _populate_checklist([n for n in filtered if not n.startswith("No recipes")])

    def _show_not_recent():
        not_recent = recipe_collection.get_recipe_names(["not-recently-used"])
        _populate_checklist([n for n in not_recent if not n.startswith("No recipes")])
        tag_var.set("")

    btn_row = tk.Frame(left_frame, bg="#e8f4f8")
    btn_row.pack(fill="x")
    ttk.Button(btn_row, text="Add Selected",    command=lambda: _add_selected()).pack(side="left", padx=2)
    ttk.Button(btn_row, text="Show Not Recent", command=_show_not_recent).pack(side="left", padx=2)
    ttk.Button(btn_row, text="Filter",          command=_filter_recipes).pack(side="left", padx=2)

    # ================================================================== MIDDLE — suggestion
    mid_frame = tk.Frame(root, bg="#e8f4f8", padx=8, pady=8)
    mid_frame.grid(row=0, column=1, sticky="nsew", padx=4, pady=8)

    ttk.Label(mid_frame, text="Random Suggestion", style="Header.TLabel").pack(fill="x")

    suggestion_var = tk.StringVar(value=random.choice(suggest_pool) if suggest_pool else "—")
    tk.Label(mid_frame, textvariable=suggestion_var, bg="#ff9f4a", fg="white",
             wraplength=200, font=("Helvetica", 12, "bold"),
             padx=8, pady=12).pack(fill="x", pady=8)

    def _new_suggestion():
        if suggest_pool:
            suggestion_var.set(random.choice(suggest_pool))

    def _add_suggestion():
        name = suggestion_var.get()
        if name and name != "—":
            _append_to_menu(name)

    ttk.Button(mid_frame, text="New Suggestion", command=_new_suggestion).pack(fill="x", pady=2)
    ttk.Button(mid_frame, text="Add Suggestion", command=_add_suggestion).pack(fill="x", pady=2)

    # ================================================================== RIGHT — current menu
    right_frame = tk.Frame(root, bg="#e8f4f8", padx=8, pady=8)
    right_frame.grid(row=0, column=2, sticky="nsew", padx=(4, 8), pady=8)

    ttk.Label(right_frame, text="Current Menu", style="Header.TLabel").pack(fill="x")

    menu_outer = tk.Frame(right_frame, bg="#ffffff", relief="sunken", bd=1)
    menu_outer.pack(fill="both", expand=True, pady=6)

    menu_canvas = tk.Canvas(menu_outer, bg="#ffffff", highlightthickness=0)
    menu_sb = ttk.Scrollbar(menu_outer, orient="vertical", command=menu_canvas.yview)
    menu_canvas.configure(yscrollcommand=menu_sb.set)
    menu_sb.pack(side="right", fill="y")
    menu_canvas.pack(side="left", fill="both", expand=True)

    menu_inner = tk.Frame(menu_canvas, bg="#ffffff")
    menu_win = menu_canvas.create_window((0, 0), window=menu_inner, anchor="nw")

    menu_inner.bind("<Configure>",  lambda e: menu_canvas.configure(scrollregion=menu_canvas.bbox("all")))
    menu_canvas.bind("<Configure>", lambda e: menu_canvas.itemconfig(menu_win, width=e.width))

    menu_vars: dict = {}
    menu_widgets: dict = {}

    def _append_to_menu(name: str) -> None:
        display = name
        while display in menu_vars:
            display += "*"
        selected_items.append(display)
        var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(menu_inner, text=display, variable=var,
                            bg="#ffffff", activebackground="#ffe8cc",
                            font=("Helvetica", 11), anchor="w")
        cb.pack(fill="x", padx=4, pady=1)
        menu_vars[display] = var
        menu_widgets[display] = cb
        menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))

    def _remove_selected_from_menu():
        for name in [n for n, v in menu_vars.items() if v.get()]:
            selected_items.remove(name)
            menu_widgets[name].destroy()
            del menu_vars[name]
            del menu_widgets[name]

    ttk.Button(right_frame, text="Remove Selected", command=_remove_selected_from_menu).pack(fill="x")

    # ================================================================== BOTTOM — options + quit buttons
    btn_frame = tk.Frame(root, bg="#e8f4f8")
    btn_frame.grid(row=1, column=0, columnspan=3, pady=(0, 8))

    todoist_var = tk.BooleanVar(value=True)

    def _quit_no_save():
        selected_items.clear()
        todoist_var.set(False)
        root.destroy()

    def _save_and_quit():
        for i in range(len(selected_items)):
            selected_items[i] = selected_items[i].strip("*")
        root.destroy()

    ttk.Button(btn_frame, text="Quit (don't save)", command=_quit_no_save).pack(side="left", padx=12)
    ttk.Button(btn_frame, text="Save and Quit",     command=_save_and_quit,
               style="Accent.TButton").pack(side="left", padx=12)

    # Todoist checkbox — checked by default, sits to the right of the save button
    tk.Checkbutton(
        btn_frame, text="Post to Todoist",
        variable=todoist_var,
        bg="#e8f4f8", activebackground="#e8f4f8",
        font=("Helvetica", 11),
    ).pack(side="left", padx=20)

    # ================================================================== helpers
    def _add_selected():
        for name, var in check_vars.items():
            if var.get():
                _append_to_menu(name)
                var.set(False)

    # ================================================================== grid weights
    root.columnconfigure(0, weight=3)
    root.columnconfigure(1, weight=2)
    root.columnconfigure(2, weight=2)
    root.rowconfigure(0, weight=1)

    root.mainloop()
    return todoist_var.get()
