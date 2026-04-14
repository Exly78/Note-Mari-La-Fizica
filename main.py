"""
Note Mari La Fizica - Bits, Qubits and Probability Simulator
Entry point. Builds the main window and the two tabs.
"""
import tkinter as tk
from tkinter import ttk

from app.bits_tab import BitsTab
from app.case_tab import CaseTab
from app.theme import apply_theme, COLORS


def main():
    root = tk.Tk()
    root.title("Note Mari La Fizica - Bits, Qubits & Probability")
    root.geometry("1180x820")
    root.minsize(1050, 760)
    root.configure(bg=COLORS["bg"])

    apply_theme(root)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    bits_tab = BitsTab(notebook)
    case_tab = CaseTab(notebook)

    notebook.add(bits_tab, text="  Bits & Qubits  ")
    notebook.add(case_tab, text="  Probability / Case Simulator  ")

    root.mainloop()


if __name__ == "__main__":
    main()
