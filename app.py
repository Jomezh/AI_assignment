import tkinter as tk
from tkinter import ttk, messagebox

from recommender import (
    RecommendationEngine, UserProfile, load_menu,
    get_student_history, log_order,
    get_student_allergies, set_student_allergies,
)

DIET_OPTIONS = ["Vegetarian", "Non-Vegetarian"]
HEALTH_GOAL_OPTIONS = ["Balanced Diet", "High Protein", "Low Calorie"]
ALLERGY_OPTIONS = ["Dairy", "Nuts", "Seafood", "Gluten"]


class ScrollableFrame(tk.Frame):
    """A frame with a vertical scrollbar; put content in .body."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.vscroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.body = tk.Frame(self.canvas)

        self.body.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.body, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vscroll.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        delta = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(delta, "units")


class CafeteriaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Cafeteria Food Recommendation System")
        self.geometry("600x600")
        self.minsize(480, 400)
        self.resizable(True, True)

        self.engine = RecommendationEngine()
        self.menu_items = load_menu()

        self.student_id_var = tk.StringVar(value="student_001")
        self.diet_var = tk.StringVar(value=DIET_OPTIONS[0])
        self.goal_var = tk.StringVar(value=HEALTH_GOAL_OPTIONS[0])
        self.allergy_vars = {a: tk.BooleanVar(value=False) for a in ALLERGY_OPTIONS}

        self.content_area = tk.Frame(self)
        self.content_area.pack(side="top", fill="both", expand=True)

        self.nav_bar = tk.Frame(self, bg="#e0e0e0", height=50)
        self.nav_bar.pack(side="bottom", fill="x")
        self.nav_bar.pack_propagate(False)

        self.show_home_screen()

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def clear_nav(self):
        for widget in self.nav_bar.winfo_children():
            widget.destroy()

    # -------------------------------------------------------------- Screen 1
    def show_home_screen(self):
        self.clear_content()
        self.clear_nav()

        frame = tk.Frame(self.content_area)
        frame.pack(expand=True)

        tk.Label(
            frame, text="Smart Cafeteria\nFood Recommendation System",
            font=("Segoe UI", 18, "bold"), justify="center"
        ).pack(pady=30)

        tk.Label(frame, text="Student ID", font=("Segoe UI", 10, "bold")).pack()
        tk.Entry(frame, textvariable=self.student_id_var, width=25,
                  justify="center").pack(pady=(2, 15))

        tk.Label(
            frame,
            text="Get a personalized recommendation based on your\n"
                 "preferences, dietary needs, and past orders.",
            font=("Segoe UI", 10), justify="center", fg="#555"
        ).pack(pady=5)

        tk.Button(
            frame, text="Start", width=20, height=2,
            bg="#2e7d32", fg="white", font=("Segoe UI", 11, "bold"),
            command=self.show_preference_screen
        ).pack(pady=25)

        tk.Button(self.nav_bar, text="Exit", width=10,
                  command=self.destroy).pack(side="right", padx=15, pady=8)

    # -------------------------------------------------------------- Screen 2
    def show_preference_screen(self):
        self.clear_content()
        self.clear_nav()

        # Pre-load stored allergy profile for this student and reset the
        # checkbox variables to reflect it (editable from here on).
        stored_allergies = set(get_student_allergies(self.student_id_var.get()))
        for a, var in self.allergy_vars.items():
            var.set(a in stored_allergies)

        scroll = ScrollableFrame(self.content_area)
        scroll.pack(fill="both", expand=True)
        frame = tk.Frame(scroll.body, padx=30, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Enter Your Preferences",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 15))

        history = get_student_history(self.student_id_var.get())
        hist_text = ", ".join(history) if history else "No past orders on record"
        tk.Label(frame, text=f"Order history for {self.student_id_var.get()}:",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(frame, text=hist_text, font=("Segoe UI", 9), fg="#555",
                 wraplength=500, justify="left").pack(anchor="w", pady=(0, 15))

        tk.Label(frame, text="Dietary Preference", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        diet_frame = tk.Frame(frame)
        diet_frame.pack(anchor="w", pady=(0, 12))
        for opt in DIET_OPTIONS:
            tk.Radiobutton(diet_frame, text=opt, variable=self.diet_var, value=opt).pack(side="left", padx=5)

        tk.Label(frame, text="Health Goal", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Combobox(frame, textvariable=self.goal_var, values=HEALTH_GOAL_OPTIONS,
                     state="readonly", width=30).pack(anchor="w", pady=(0, 12))

        tk.Label(frame, text="Allergy Information", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(
            frame,
            text="(Pre-filled from your saved profile. Uncheck to remove, "
                 "check to add a new allergy -- changes are saved.)",
            font=("Segoe UI", 8), fg="#777"
        ).pack(anchor="w")
        allergy_frame = tk.Frame(frame)
        allergy_frame.pack(anchor="w", pady=(4, 12))
        for a in ALLERGY_OPTIONS:
            tk.Checkbutton(allergy_frame, text=a, variable=self.allergy_vars[a]).pack(side="left", padx=4)

        tk.Button(self.nav_bar, text="Back", width=10,
                  command=self.show_home_screen).pack(side="left", padx=15, pady=8)
        tk.Button(self.nav_bar, text="Recommend", width=15, bg="#2e7d32", fg="white",
                  font=("Segoe UI", 10, "bold"),
                  command=self.generate_recommendations).pack(side="right", padx=15, pady=8)

    # -------------------------------------------------------------- Logic
    def generate_recommendations(self):
        allergies = [a for a, var in self.allergy_vars.items() if var.get()]

        # Persist the current checkbox state as the new allergy profile,
        # whether it added, removed, or left allergies unchanged.
        set_student_allergies(self.student_id_var.get(), allergies)

        if not allergies:
            allergies = ["None"]

        history = get_student_history(self.student_id_var.get())
        user = UserProfile(
            diet_preference=self.diet_var.get(),
            health_goal=self.goal_var.get(),
            allergies=allergies,
            order_history=history,
        )
        results = self.engine.recommend(user, top_n=3)
        self.show_recommendation_screen(results)

    # -------------------------------------------------------------- Screen 3
    def show_recommendation_screen(self, results):
        self.clear_content()
        self.clear_nav()

        scroll = ScrollableFrame(self.content_area)
        scroll.pack(fill="both", expand=True)
        frame = tk.Frame(scroll.body, padx=30, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Recommended Meals", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 15))

        if not results:
            tk.Label(frame, text="No suitable food found. Try adjusting your allergy filters.",
                     fg="red").pack(pady=20)
        else:
            for r in results:
                f = r["food"]
                card = tk.Frame(frame, relief="groove", borderwidth=1, padx=12, pady=10)
                card.pack(fill="x", pady=6)

                tk.Label(card, text=f["name"], font=("Segoe UI", 12, "bold")).pack(anchor="w")
                tk.Label(card, text=f"Calories: {f['calories']}   |   Protein: {f['protein']} g   |   Score: {r['score']}",
                         font=("Segoe UI", 9), fg="#333").pack(anchor="w", pady=(2, 4))
                for reason in r["reasons"]:
                    tk.Label(card, text=reason, font=("Segoe UI", 9), fg="#2e7d32").pack(anchor="w")

                tk.Button(
                    card, text="Confirm & Order", bg="#1565c0", fg="white",
                    font=("Segoe UI", 9, "bold"),
                    command=lambda name=f["name"]: self.confirm_order(name)
                ).pack(anchor="e", pady=(6, 0))

        tk.Button(self.nav_bar, text="Back", width=10,
                  command=self.show_preference_screen).pack(side="left", padx=15, pady=8)
        tk.Button(self.nav_bar, text="Exit", width=10,
                  command=self.destroy).pack(side="right", padx=15, pady=8)

    def confirm_order(self, food_name: str):
        """Actuator: logs the chosen order into persistent history."""
        log_order(self.student_id_var.get(), food_name)
        messagebox.showinfo(
            "Order Confirmed",
            f"'{food_name}' has been logged to your order history.\n"
            "Future recommendations will take this into account."
        )


if __name__ == "__main__":
    app = CafeteriaApp()
    app.mainloop()
