import tkinter as tk
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import json
from threading import Thread
from time import sleep
from main import run_bot

def run_bot_thread(source_file, last_run):
    while True:
        is_bot_completed = run_bot(source_file, last_run)
        if is_bot_completed:
            break
        else:
            sleep(60*5)

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.bot_thread = None
        self.title("Fazenda Automation")

        # Variables to store date and file path
        self.fetch_all = tk.BooleanVar(value=False)
        self.last_run_date = tk.StringVar()
        self.source_cnpj_file = tk.StringVar()

        # Create widgets
        self.label_fetch_all = tk.Label(self, text="Fetch All:")
        self.checkbox_fetch_all = tk.Checkbutton(self, variable=self.fetch_all, onvalue=True, offvalue=False, command=self.toggle_last_run_input)

        self.label_last_run = tk.Label(self, text="Last Run:")
        self.entry_last_run = DateEntry(self, state='normal')
        
        self.label_source_file = tk.Label(self, text="Source CNPJ File:")
        self.entry_source_file = tk.Entry(self, textvariable=self.source_cnpj_file, state='readonly')
        self.button_browse_file = tk.Button(self, text="Browse", command=self.browse_file)
        self.button_run = tk.Button(self, text="Run", command=self.run_function)

        # Layout widgets
        self.label_fetch_all.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.checkbox_fetch_all.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.label_last_run.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_last_run.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.label_source_file.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_source_file.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.button_browse_file.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.button_run.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

    def toggle_last_run_input(self):
        if self.fetch_all.get():
            # Disable last run input and set a date in 2000
            self.entry_last_run.configure(state='disabled')
        else:
            # Enable last run input
            self.entry_last_run.configure(state='normal')

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.source_cnpj_file.set(filename)

    def run_function(self):
        if self.bot_thread:
            if self.bot_thread.is_alive():
                messagebox.showerror("Error", "Bot's Thread is already running.")
                return

        if self.fetch_all.get():
            last_run = datetime(2000, 1, 1)
        else:
            selected_date = self.entry_last_run.get_date()
            last_run = datetime(selected_date.year, selected_date.month, selected_date.day)
        
        current_date = datetime.now()
        if last_run > current_date:
            messagebox.showwarning("Warning", "Last run date cannot be in the future.")
            return

        source_file = self.source_cnpj_file.get()
        if source_file:
            self.bot_thread = Thread(target=run_bot_thread, args=[source_file, last_run])
            self.bot_thread.start()
        else:
            messagebox.showwarning("Warning", "Please select a source CNPJ file.")

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
