import tkinter as tk
import random
import time


class ReactionGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Reaction Speed Game")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.state = "idle"      # idle, waiting, go, early, result
        self.times = []          # all valid reaction times (ms)
        self.start_time = 0.0
        self.wait_job = None
        self.tick_job = None

        # Main clickable area
        self.area = tk.Frame(root, bg="#2c3e50", cursor="hand2")
        self.area.pack(fill="both", expand=True)

        self.title_label = tk.Label(
            self.area, text="Click to Start", font=("Arial", 28, "bold"),
            bg="#2c3e50", fg="white")
        self.title_label.pack(pady=(80, 10))

        self.sub_label = tk.Label(
            self.area, text="Click (or press SPACE) as soon as the screen turns GREEN",
            font=("Arial", 12), bg="#2c3e50", fg="#ecf0f1")
        self.sub_label.pack()

        # Live timer (updates in real time while the screen is green)
        self.timer_label = tk.Label(
            self.area, text="", font=("Consolas", 48, "bold"),
            bg="#2c3e50", fg="white")
        self.timer_label.pack(pady=30)

        # Stats bar
        self.stats_label = tk.Label(
            root, text=self.stats_text(), font=("Arial", 12),
            bg="#1a252f", fg="white", pady=10)
        self.stats_label.pack(fill="x")

        # Bind click and spacebar on everything
        for widget in (self.area, self.title_label, self.sub_label, self.timer_label):
            widget.bind("<Button-1>", self.on_press)
        root.bind("<space>", self.on_press)

    # ---------- helpers ----------
    def set_colors(self, color):
        for w in (self.area, self.title_label, self.sub_label, self.timer_label):
            w.config(bg=color)

    def stats_text(self):
        if not self.times:
            return "Attempts: 0   |   Best: --   |   Average: --"
        best = min(self.times)
        avg = sum(self.times) / len(self.times)
        return f"Attempts: {len(self.times)}   |   Best: {best:.0f} ms   |   Average: {avg:.0f} ms"

    @staticmethod
    def rating(ms):
        if ms < 200:
            return "Lightning fast! ⚡"
        if ms < 250:
            return "Excellent!"
        if ms < 300:
            return "Good"
        if ms < 400:
            return "Average"
        return "Keep practicing"

    # ---------- game flow ----------
    def on_press(self, event=None):
        if self.state in ("idle", "result", "early"):
            self.start_round()
        elif self.state == "waiting":
            self.too_early()
        elif self.state == "go":
            self.record_reaction()

    def start_round(self):
        self.state = "waiting"
        self.set_colors("#c0392b")  # red
        self.title_label.config(text="Wait for GREEN...")
        self.sub_label.config(text="Don't click yet!")
        self.timer_label.config(text="")
        delay_ms = int(random.uniform(1.5, 4.5) * 1000)
        self.wait_job = self.root.after(delay_ms, self.go_green)

    def go_green(self):
        self.state = "go"
        self.set_colors("#27ae60")  # green
        self.title_label.config(text="CLICK NOW!")
        self.sub_label.config(text="")
        self.start_time = time.perf_counter()
        self.update_timer()

    def update_timer(self):
        """Real-time millisecond counter shown while waiting for the click."""
        if self.state != "go":
            return
        elapsed_ms = (time.perf_counter() - self.start_time) * 1000
        self.timer_label.config(text=f"{elapsed_ms:.0f} ms")
        self.tick_job = self.root.after(10, self.update_timer)

    def record_reaction(self):
        reaction_ms = (time.perf_counter() - self.start_time) * 1000
        if self.tick_job:
            self.root.after_cancel(self.tick_job)
            self.tick_job = None

        self.state = "result"
        self.times.append(reaction_ms)
        self.set_colors("#2980b9")  # blue
        self.title_label.config(text=self.rating(reaction_ms))
        self.timer_label.config(text=f"{reaction_ms:.0f} ms")
        self.sub_label.config(text="Click (or press SPACE) to try again")
        self.stats_label.config(text=self.stats_text())

    def too_early(self):
        if self.wait_job:
            self.root.after_cancel(self.wait_job)
            self.wait_job = None
        self.state = "early"
        self.set_colors("#d35400")  # orange
        self.title_label.config(text="Too early!")
        self.timer_label.config(text="")
        self.sub_label.config(text="Wait for green. Click to try again")


if __name__ == "__main__":
    root = tk.Tk()
    ReactionGame(root)
    root.mainloop()
