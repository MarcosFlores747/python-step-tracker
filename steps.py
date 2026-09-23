"""
Program: steps.py
Author: Marcos
Date: 8/31/2026

An interactive weekly step tracker with a playful walking animation.
Built entirely with Python's standard library.
"""

import math
import random
import tkinter as tk
from tkinter import messagebox


class StepTrackerApp:
    """A lively desktop dashboard for logging a week of walking."""

    COLORS = {
        "background": "#F3F7F4",
        "surface": "#FFFFFF",
        "surface_alt": "#ECF3EE",
        "ink": "#18332B",
        "muted": "#6B7D76",
        "border": "#D9E5DD",
        "green": "#20A66A",
        "green_dark": "#137A4B",
        "mint": "#CFF3DF",
        "lime": "#C9F45D",
        "orange": "#FF9C59",
        "coral": "#FF6B6B",
        "sky": "#DDF5FF",
        "navy": "#173B57",
    }

    DAYS = (
        ("Sunday", "SUN"),
        ("Monday", "MON"),
        ("Tuesday", "TUE"),
        ("Wednesday", "WED"),
        ("Thursday", "THU"),
        ("Friday", "FRI"),
        ("Saturday", "SAT"),
    )

    COACHING_MESSAGES = (
        "Great rhythm—keep moving!",
        "Every step is a vote for your health.",
        "Strong pace! You've got this.",
        "A short walk still counts.",
        "Keep going—future you says thanks!",
    )

    def __init__(self, root):
        self.root = root
        self.root.title("Stride — Weekly Step Tracker")
        self.root.geometry("1120x700")
        self.root.minsize(920, 640)
        self.root.configure(bg=self.COLORS["background"])

        self.step_vars = {
            day: tk.StringVar(value="") for day, _short_name in self.DAYS
        }
        self.goal_var = tk.StringVar(value="70000")
        self.total_var = tk.StringVar(value="0")
        self.average_var = tk.StringVar(value="0")
        self.miles_var = tk.StringVar(value="0.0")
        self.calories_var = tk.StringVar(value="0")
        self.progress_var = tk.StringVar(value="0% of weekly goal")
        self.goal_hint_var = tk.StringVar(value="70,000 steps to go")
        self.coach_var = tk.StringVar(value="Choose a day, then start moving.")
        self.selected_day = "Monday"
        self.day_rows = {}
        self.day_entries = {}

        self.walk_phase = 0.0
        self.walker_x = 70.0
        self.celebrated = False
        self.confetti = []

        self._build_ui()
        self._bind_events()
        self._select_day("Monday")
        self._update_dashboard()
        self._animate()

    def _build_ui(self):
        accent = tk.Frame(self.root, bg=self.COLORS["green"], height=6)
        accent.grid(row=0, column=0, sticky="ew")

        shell = tk.Frame(self.root, bg=self.COLORS["background"])
        shell.grid(row=1, column=0, sticky="nsew", padx=28, pady=(18, 22))
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        shell.grid_columnconfigure(0, weight=3, uniform="main")
        shell.grid_columnconfigure(1, weight=2, uniform="main")
        shell.grid_rowconfigure(1, weight=1)

        self._build_header(shell)
        self._build_activity_panel(shell)
        self._build_week_panel(shell)

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=self.COLORS["background"])
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        header.grid_columnconfigure(0, weight=0)

        logo = tk.Label(
            header,
            text="S",
            bg=self.COLORS["green"],
            fg="white",
            width=3,
            pady=7,
            font=("Segoe UI", 14, "bold"),
        )
        logo.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 12))

        tk.Label(
            header,
            text="STRIDE",
            bg=self.COLORS["background"],
            fg=self.COLORS["green"],
            font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=1, sticky="sw")
        tk.Label(
            header,
            text="Your week in motion",
            bg=self.COLORS["background"],
            fg=self.COLORS["ink"],
            font=("Segoe UI", 24, "bold"),
        ).grid(row=1, column=1, sticky="nw")
        header.grid_columnconfigure(1, weight=1)

        goal = tk.Frame(
            header,
            bg=self.COLORS["surface"],
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
        )
        goal.grid(row=0, column=2, rowspan=2, sticky="e")
        tk.Label(
            goal,
            text="WEEKLY GOAL",
            bg=self.COLORS["surface"],
            fg=self.COLORS["muted"],
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(14, 4), pady=(8, 0))
        self.goal_entry = tk.Entry(
            goal,
            textvariable=self.goal_var,
            width=8,
            justify="right",
            bg=self.COLORS["surface"],
            fg=self.COLORS["ink"],
            insertbackground=self.COLORS["green"],
            relief="flat",
            highlightthickness=0,
            validate="key",
            validatecommand=(self.root.register(self._valid_steps), "%P"),
            font=("Segoe UI", 13, "bold"),
        )
        self.goal_entry.grid(row=1, column=0, padx=(14, 4), pady=(0, 8))
        tk.Label(
            goal,
            text="steps",
            bg=self.COLORS["surface"],
            fg=self.COLORS["muted"],
            font=("Segoe UI", 9),
        ).grid(row=1, column=1, padx=(0, 14), pady=(0, 8))

    def _build_activity_panel(self, parent):
        panel = tk.Frame(parent, bg=self.COLORS["background"])
        panel.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)

        activity = self._card(panel)
        activity.grid(row=0, column=0, sticky="nsew")
        activity.grid_columnconfigure(0, weight=1)
        activity.grid_rowconfigure(1, weight=1)

        activity_header = tk.Frame(activity, bg=self.COLORS["surface"])
        activity_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 10))
        activity_header.grid_columnconfigure(0, weight=1)
        tk.Label(
            activity_header,
            text="Walking studio",
            bg=self.COLORS["surface"],
            fg=self.COLORS["ink"],
            font=("Segoe UI", 15, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            activity_header,
            text="●  WALK IN PROGRESS",
            bg=self.COLORS["mint"],
            fg=self.COLORS["green_dark"],
            padx=10,
            pady=5,
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=1, sticky="e")

        self.scene = tk.Canvas(
            activity,
            height=258,
            bg=self.COLORS["sky"],
            bd=0,
            highlightthickness=0,
        )
        self.scene.grid(row=1, column=0, sticky="nsew", padx=1)
        self.scene.bind("<Configure>", self._draw_scene)

        coach_bar = tk.Frame(activity, bg=self.COLORS["surface"])
        coach_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(12, 14))
        coach_bar.grid_columnconfigure(1, weight=1)
        tk.Label(
            coach_bar,
            text="●",
            bg=self.COLORS["surface"],
            fg=self.COLORS["orange"],
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(0, 9))
        tk.Label(
            coach_bar,
            textvariable=self.coach_var,
            bg=self.COLORS["surface"],
            fg=self.COLORS["ink"],
            anchor="w",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=1, sticky="w")

        metrics = tk.Frame(panel, bg=self.COLORS["background"])
        metrics.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        for column in range(4):
            metrics.grid_columnconfigure(column, weight=1, uniform="metric")

        self._metric_card(metrics, 0, "TOTAL STEPS", self.total_var, self.COLORS["green"])
        self._metric_card(metrics, 1, "DAILY AVG", self.average_var, self.COLORS["orange"])
        self._metric_card(metrics, 2, "EST. MILES", self.miles_var, self.COLORS["navy"])
        self._metric_card(metrics, 3, "EST. CAL", self.calories_var, self.COLORS["coral"])

        progress_card = self._card(panel)
        progress_card.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        progress_card.grid_columnconfigure(0, weight=1)
        progress_top = tk.Frame(progress_card, bg=self.COLORS["surface"])
        progress_top.grid(row=0, column=0, sticky="ew", padx=18, pady=(11, 7))
        progress_top.grid_columnconfigure(0, weight=1)
        tk.Label(
            progress_top,
            textvariable=self.progress_var,
            bg=self.COLORS["surface"],
            fg=self.COLORS["ink"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            progress_top,
            textvariable=self.goal_hint_var,
            bg=self.COLORS["surface"],
            fg=self.COLORS["muted"],
            font=("Segoe UI", 9),
        ).grid(row=0, column=1, sticky="e")

        self.progress_track = tk.Frame(progress_card, bg=self.COLORS["surface_alt"], height=12)
        self.progress_track.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 13))
        self.progress_track.grid_propagate(False)
        self.progress_fill = tk.Frame(self.progress_track, bg=self.COLORS["green"])
        self.progress_fill.place(x=0, y=0, relheight=1, relwidth=0)

    def _build_week_panel(self, parent):
        card = self._card(parent)
        card.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        tk.Label(
            card,
            text="Log your week",
            bg=self.COLORS["surface"],
            fg=self.COLORS["ink"],
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 2))
        tk.Label(
            card,
            text="Select a day or type your step count directly.",
            bg=self.COLORS["surface"],
            fg=self.COLORS["muted"],
            font=("Segoe UI", 9),
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 9))

        days = tk.Frame(card, bg=self.COLORS["surface"])
        days.grid(row=2, column=0, sticky="nsew", padx=20)
        days.grid_columnconfigure(0, weight=1)
        for row, (day, short_name) in enumerate(self.DAYS):
            days.grid_rowconfigure(row, weight=1, uniform="days")
            self._day_row(days, row, day, short_name)

        quick_add = tk.Frame(card, bg=self.COLORS["surface_alt"])
        quick_add.grid(row=3, column=0, sticky="ew", padx=20, pady=(9, 8))
        quick_add.grid_columnconfigure(0, weight=1)
        tk.Label(
            quick_add,
            text="QUICK LOG TO SELECTED DAY",
            bg=self.COLORS["surface_alt"],
            fg=self.COLORS["muted"],
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(7, 5))

        for column, amount in enumerate((500, 1000, 2500)):
            button = self._button(
                quick_add,
                f"+{amount:,}",
                lambda value=amount: self._add_steps(value),
                self.COLORS["surface"],
                self.COLORS["ink"],
                self.COLORS["mint"],
            )
            button.configure(padx=10, pady=5)
            button.grid(
                row=1,
                column=column,
                sticky="ew",
                padx=(10 if column == 0 else 3, 10 if column == 2 else 3),
                pady=(0, 7),
            )
            quick_add.grid_columnconfigure(column, weight=1, uniform="quick")

        footer = tk.Frame(card, bg=self.COLORS["surface"])
        footer.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 13))
        footer.grid_columnconfigure(0, weight=1)
        tk.Label(
            footer,
            text="Tip: about 2,000 steps ≈ 1 mile",
            bg=self.COLORS["surface"],
            fg=self.COLORS["muted"],
            font=("Segoe UI", 8),
        ).grid(row=0, column=0, sticky="w")
        self._button(
            footer,
            "Clear week",
            self._clear_week,
            self.COLORS["surface_alt"],
            self.COLORS["muted"],
            self.COLORS["border"],
        ).grid(row=0, column=1, sticky="e")

    def _card(self, parent):
        return tk.Frame(
            parent,
            bg=self.COLORS["surface"],
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
        )

    def _metric_card(self, parent, column, label, variable, accent):
        card = self._card(parent)
        card.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=(0 if column == 0 else 5, 0 if column == 3 else 5),
        )
        tk.Frame(card, bg=accent, width=5).pack(side="left", fill="y")
        content = tk.Frame(card, bg=self.COLORS["surface"])
        content.pack(side="left", fill="both", expand=True, padx=10, pady=9)
        tk.Label(
            content,
            text=label,
            bg=self.COLORS["surface"],
            fg=self.COLORS["muted"],
            anchor="w",
            font=("Segoe UI", 7, "bold"),
        ).pack(fill="x")
        tk.Label(
            content,
            textvariable=variable,
            bg=self.COLORS["surface"],
            fg=self.COLORS["ink"],
            anchor="w",
            font=("Segoe UI", 16, "bold"),
        ).pack(fill="x", pady=(2, 0))

    def _day_row(self, parent, row, day, short_name):
        container = tk.Frame(
            parent,
            bg=self.COLORS["surface_alt"],
            highlightthickness=2,
            highlightbackground=self.COLORS["surface_alt"],
            cursor="hand2",
        )
        container.grid(row=row, column=0, sticky="nsew", pady=3)
        container.grid_columnconfigure(1, weight=1)
        self.day_rows[day] = container

        badge = tk.Label(
            container,
            text=short_name,
            bg=self.COLORS["mint"],
            fg=self.COLORS["green_dark"],
            width=5,
            pady=5,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        )
        badge.grid(row=0, column=0, padx=(7, 10), pady=4)

        name = tk.Label(
            container,
            text=day,
            bg=self.COLORS["surface_alt"],
            fg=self.COLORS["ink"],
            anchor="w",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        name.grid(row=0, column=1, sticky="ew")

        entry = tk.Entry(
            container,
            textvariable=self.step_vars[day],
            width=8,
            justify="right",
            bg=self.COLORS["surface"],
            fg=self.COLORS["ink"],
            insertbackground=self.COLORS["green"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
            highlightcolor=self.COLORS["green"],
            validate="key",
            validatecommand=(self.root.register(self._valid_steps), "%P"),
            font=("Segoe UI", 11, "bold"),
        )
        entry.grid(row=0, column=2, padx=(7, 5), pady=5, ipady=2)
        entry.bind("<FocusIn>", lambda _event, chosen=day: self._select_day(chosen))
        self.day_entries[day] = entry

        units = tk.Label(
            container,
            text="steps",
            bg=self.COLORS["surface_alt"],
            fg=self.COLORS["muted"],
            font=("Segoe UI", 8),
            cursor="hand2",
        )
        units.grid(row=0, column=3, padx=(0, 10))

        for widget in (container, badge, name, units):
            widget.bind("<Button-1>", lambda _event, chosen=day: self._focus_day(chosen))

    def _button(self, parent, text, command, background, foreground, active_background):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=background,
            fg=foreground,
            activebackground=active_background,
            activeforeground=foreground,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=16,
            pady=9,
            font=("Segoe UI", 9, "bold"),
        )

    def _bind_events(self):
        for variable in self.step_vars.values():
            variable.trace_add("write", self._update_dashboard)
        self.goal_var.trace_add("write", self._update_dashboard)

    @staticmethod
    def _valid_steps(value):
        return value == "" or (value.isdigit() and len(value) <= 6)

    @staticmethod
    def _number(value):
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return 0

    def _focus_day(self, day):
        self._select_day(day)
        self.day_entries[day].focus_set()

    def _select_day(self, day):
        self.selected_day = day
        for name, row in self.day_rows.items():
            selected = name == day
            row.configure(
                highlightbackground=(
                    self.COLORS["green"] if selected else self.COLORS["surface_alt"]
                )
            )
        self.coach_var.set(f"{day} selected—ready when you are!")

    def _add_steps(self, amount):
        variable = self.step_vars[self.selected_day]
        new_value = min(999999, self._number(variable.get()) + amount)
        variable.set(str(new_value))
        self.coach_var.set(f"Nice! Added {amount:,} steps to {self.selected_day}.")
        self._pulse_selected_row()

    def _pulse_selected_row(self):
        row = self.day_rows[self.selected_day]
        row.configure(bg=self.COLORS["mint"])
        self.root.after(180, lambda: row.configure(bg=self.COLORS["surface_alt"]))

    def _update_dashboard(self, *_args):
        total = sum(self._number(variable.get()) for variable in self.step_vars.values())
        goal = self._number(self.goal_var.get())
        average = round(total / 7)
        miles = total / 2000
        calories = round(total * 0.04)

        self.total_var.set(f"{total:,}")
        self.average_var.set(f"{average:,}")
        self.miles_var.set(f"{miles:,.1f}")
        self.calories_var.set(f"{calories:,}")

        if goal > 0:
            percent = total / goal
            visible_percent = min(100, round(percent * 100))
            self.progress_var.set(f"{visible_percent}% of weekly goal")
            remaining = max(0, goal - total)
            self.goal_hint_var.set(
                "Goal reached—amazing!" if remaining == 0 else f"{remaining:,} steps to go"
            )
            self.progress_fill.place(relwidth=min(1, percent))
            self.progress_fill.configure(
                bg=self.COLORS["lime"] if percent >= 1 else self.COLORS["green"]
            )
            if percent >= 1 and not self.celebrated:
                self.celebrated = True
                self.coach_var.set("Weekly goal crushed! Take a victory lap!")
                self._launch_confetti()
            elif percent < 1:
                self.celebrated = False
        else:
            self.progress_var.set("Set a weekly goal")
            self.goal_hint_var.set("Enter a goal above")
            self.progress_fill.place(relwidth=0)

    def _clear_week(self):
        if not any(variable.get() for variable in self.step_vars.values()):
            self.coach_var.set("Your week is already clear.")
            return
        if not messagebox.askyesno(
            "Clear this week?",
            "This will remove the step counts for all seven days.",
            parent=self.root,
        ):
            return
        for variable in self.step_vars.values():
            variable.set("")
        self._select_day("Monday")
        self.coach_var.set("Fresh week, fresh start. Let's move!")

    def _draw_scene(self, _event=None):
        canvas = self.scene
        width = max(canvas.winfo_width(), 500)
        height = max(canvas.winfo_height(), 258)
        canvas.delete("all")
        self.confetti.clear()

        canvas.create_rectangle(0, 0, width, height, fill=self.COLORS["sky"], outline="")
        canvas.create_oval(width - 92, 20, width - 42, 70, fill="#FFE38A", outline="")
        self._cloud(70, 48)
        self._cloud(width * 0.53, 72, scale=0.8)

        canvas.create_polygon(
            0,
            155,
            width * 0.2,
            95,
            width * 0.42,
            155,
            width * 0.66,
            102,
            width,
            155,
            fill="#AEDDBE",
            outline="",
        )
        canvas.create_polygon(
            0,
            170,
            width * 0.29,
            120,
            width * 0.58,
            170,
            width * 0.83,
            125,
            width,
            164,
            fill="#78C897",
            outline="",
        )
        canvas.create_rectangle(0, 166, width, height, fill="#BDE7C9", outline="")
        canvas.create_rectangle(0, 202, width, height, fill="#EAF0E8", outline="")
        canvas.create_line(0, 202, width, 202, fill="#9FC7A8", width=2)
        canvas.create_line(0, 236, width, 236, fill="white", width=3, dash=(18, 15))

        self._tree(35, 125, 0.85)
        self._tree(width - 60, 130, 0.72)
        self._draw_walker()

    def _cloud(self, x, y, scale=1.0):
        canvas = self.scene
        fill = "#FFFFFF"
        canvas.create_oval(x, y, x + 44 * scale, y + 23 * scale, fill=fill, outline="")
        canvas.create_oval(
            x + 20 * scale,
            y - 10 * scale,
            x + 58 * scale,
            y + 23 * scale,
            fill=fill,
            outline="",
        )
        canvas.create_oval(
            x + 40 * scale,
            y,
            x + 77 * scale,
            y + 23 * scale,
            fill=fill,
            outline="",
        )

    def _tree(self, x, y, scale):
        canvas = self.scene
        canvas.create_rectangle(
            x - 4 * scale,
            y + 25 * scale,
            x + 4 * scale,
            202,
            fill="#8C674A",
            outline="",
        )
        canvas.create_oval(
            x - 25 * scale,
            y,
            x + 25 * scale,
            y + 48 * scale,
            fill="#2FA96E",
            outline="",
        )

    def _draw_walker(self):
        canvas = self.scene
        canvas.delete("walker")
        x = self.walker_x
        phase = self.walk_phase
        bounce = abs(math.sin(phase * 2)) * 3
        shoulder_y = 132 - bounce
        hip_y = 167 - bounce
        leg_swing = math.sin(phase) * 19
        arm_swing = -math.sin(phase) * 17

        canvas.create_oval(
            x - 24,
            195,
            x + 24,
            202,
            fill="#9DBBA7",
            outline="",
            tags="walker",
        )
        for offset in (28, 40, 52):
            canvas.create_line(
                x - offset,
                146 + (offset % 3) * 5,
                x - offset + 12,
                146 + (offset % 3) * 5,
                fill="#72B892",
                width=3,
                tags="walker",
            )

        canvas.create_line(
            x,
            hip_y,
            x - leg_swing,
            198 - abs(leg_swing) * 0.08,
            fill=self.COLORS["navy"],
            width=7,
            capstyle="round",
            tags="walker",
        )
        canvas.create_line(
            x,
            hip_y,
            x + leg_swing,
            198 - abs(leg_swing) * 0.08,
            fill="#265876",
            width=7,
            capstyle="round",
            tags="walker",
        )
        canvas.create_line(
            x - leg_swing,
            198 - abs(leg_swing) * 0.08,
            x - leg_swing + 9,
            198 - abs(leg_swing) * 0.08,
            fill=self.COLORS["ink"],
            width=5,
            capstyle="round",
            tags="walker",
        )
        canvas.create_line(
            x + leg_swing,
            198 - abs(leg_swing) * 0.08,
            x + leg_swing + 9,
            198 - abs(leg_swing) * 0.08,
            fill=self.COLORS["ink"],
            width=5,
            capstyle="round",
            tags="walker",
        )

        canvas.create_line(
            x,
            shoulder_y + 5,
            x + arm_swing,
            159 - bounce,
            fill="#D78A62",
            width=6,
            capstyle="round",
            tags="walker",
        )
        canvas.create_line(
            x,
            shoulder_y + 5,
            x - arm_swing,
            159 - bounce,
            fill="#F0AA7F",
            width=6,
            capstyle="round",
            tags="walker",
        )
        canvas.create_line(
            x,
            shoulder_y,
            x,
            hip_y,
            fill=self.COLORS["green"],
            width=15,
            capstyle="round",
            tags="walker",
        )
        canvas.create_arc(
            x - 13,
            shoulder_y - 8,
            x + 13,
            shoulder_y + 12,
            start=0,
            extent=180,
            fill=self.COLORS["lime"],
            outline="",
            tags="walker",
        )
        canvas.create_oval(
            x - 11,
            shoulder_y - 35,
            x + 11,
            shoulder_y - 13,
            fill="#F0AA7F",
            outline="",
            tags="walker",
        )
        canvas.create_arc(
            x - 12,
            shoulder_y - 39,
            x + 12,
            shoulder_y - 16,
            start=0,
            extent=180,
            fill=self.COLORS["ink"],
            outline="",
            tags="walker",
        )
        canvas.create_oval(
            x + 5,
            shoulder_y - 28,
            x + 7,
            shoulder_y - 26,
            fill=self.COLORS["ink"],
            outline="",
            tags="walker",
        )

    def _animate(self):
        self.walk_phase += 0.18
        self.walker_x += 2.4
        width = max(self.scene.winfo_width(), 500)
        if self.walker_x > width + 35:
            self.walker_x = -35
            self.coach_var.set(random.choice(self.COACHING_MESSAGES))
        self._draw_walker()

        self._animate_confetti()
        self.root.after(35, self._animate)

    def _launch_confetti(self):
        width = max(self.scene.winfo_width(), 500)
        palette = (
            self.COLORS["green"],
            self.COLORS["lime"],
            self.COLORS["orange"],
            self.COLORS["coral"],
            self.COLORS["navy"],
        )
        for _piece in range(70):
            x = random.randint(8, int(width - 8))
            y = random.randint(-150, -8)
            size = random.randint(4, 8)
            item = self.scene.create_rectangle(
                x,
                y,
                x + size,
                y + size * 1.5,
                fill=random.choice(palette),
                outline="",
                tags="confetti",
            )
            self.confetti.append(
                (item, random.uniform(-0.8, 0.8), random.uniform(2, 4))
            )

    def _animate_confetti(self):
        if not self.confetti:
            return
        remaining = []
        height = max(self.scene.winfo_height(), 258)
        for item, drift, speed in self.confetti:
            coordinates = self.scene.coords(item)
            if not coordinates:
                continue
            self.scene.move(item, drift, speed)
            if coordinates[1] <= height:
                remaining.append((item, drift, speed))
            else:
                self.scene.delete(item)
        self.confetti = remaining


def main():
    root = tk.Tk()
    StepTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
