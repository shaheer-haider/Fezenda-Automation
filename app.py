from datetime import datetime
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import filedialog, messagebox
from threading import Thread
from main import run_bot
from tkcalendar import DateEntry


def main():
    status = open("status.txt", "r").read().strip().replace("\n", "")
    if status == "running":
        return "Bot is already running"

    elif status != "stopped":
        return "Bot is failed due to unknown error, check logs"

    Thread(target=run_bot).start()

    return "Bot started successfully"


class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.bot_thread = None
        self.title("Fazenda Automation")

        # Variables to store date and file path
        self.last_run_date = tk.StringVar()
        self.source_cnpj_file = tk.StringVar()

        # Create widgets
        storeData = json.load(open("store.json"))
        print(storeData["last_run"] is not None and storeData["last_run"] != "")

        if storeData["last_run"] is not None and storeData["last_run"] != "":
            print(storeData["last_run"])
            last_time_run_datetime  = datetime.strptime(storeData["last_run"], "%m/%d/%Y")

            self.label_last_run = tk.Label(self, text="Last Run:")
            self.entry_last_run = DateEntry(
                self,
                selectmode = 'day', 
                day=last_time_run_datetime.day,
                month=last_time_run_datetime.month,
                year=last_time_run_datetime.year,
            )

        self.label_source_file = tk.Label(self, text="Source CNPJ File:")
        self.entry_source_file = tk.Entry(self, textvariable=self.source_cnpj_file, state='readonly')
        self.button_browse_file = tk.Button(self, text="Browse", command=self.browse_file)
        self.button_run = tk.Button(self, text="Run", command=self.run_function)

        # Layout widgets
        if storeData["last_run"] is not None and storeData["last_run"] != "":
            self.label_last_run.grid(row=0, column=0, padx=5, pady=5, sticky="e")
            self.entry_last_run.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.label_source_file.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_source_file.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.button_browse_file.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.button_run.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.source_cnpj_file.set(filename)

    def run_function(self):
        if self.bot_thread:
            if self.bot_thread.is_alive():
                messagebox.showerror("Error", "Bot is already running.")
                return
                
        
        last_run = None
        storeData = json.load(open("store.json"))
        if storeData["last_run"] is not None and storeData["last_run"] != "":
            selected_date_str = datetime.strftime(self.entry_last_run.get_date(), "%m/%d/%Y")
            selected_date = datetime.strptime(selected_date_str, "%m/%d/%Y")
            last_run = selected_date
            storeData["last_run"] = selected_date_str
        else:
            last_run = None
        
        if last_run:    
            
            current_date = datetime.now()
            if last_run > current_date:
                messagebox.showwarning("Warning", "Last run date cannot be in the future.")
                return

        source_file = self.source_cnpj_file.get()
        if source_file:
            if storeData["last_run"] is not None and storeData["last_run"] != "":
                json.dump(storeData, open("store.json", "w"))
                

                print("Last Run:", self.entry_last_run.get_date())
        
            print("Source CNPJ File Path:", source_file)
            self.bot_thread = Thread(target=run_bot, args=[source_file, last_run])
            self.bot_thread.start()
            
            storeData["last_run"] = datetime.now().strftime("%m/%d/%Y")
            json.dump(storeData, open("store.json", "w"))

            # run_bot(source_file, last_run)
        else:
            messagebox.showwarning("Warning", "Please select a source CNPJ file.")
            

if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
