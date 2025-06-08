from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk

def plot_bar_chart(parent_frame, habit_names, completed_counts, uncompleted_counts):
    # Clear previous chart
    for widget in parent_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(8, 4))
    x = range(len(habit_names))
    width = 0.35

    ax.bar([i - width/2 for i in x], completed_counts, width, label='Wykonano', color='green')
    ax.bar([i + width/2 for i in x], uncompleted_counts, width, label='Nie wykonano', color='red')
    ax.set_xticks(list(x))
    ax.set_xticklabels(habit_names, rotation=45, ha='right')
    ax.set_ylabel('Liczba dni')
    ax.set_title('Statystyki nawyków')
    ax.legend()

    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)