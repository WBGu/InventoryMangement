import tkinter as tk
from tkinter import messagebox
from tksheet import Sheet
import subprocess
import os
import json
import shutil
from collections import Counter

# --- CONFIGURATION ---
# This is the path to the separate inventory data repository folder. Should have .git in it
DATA_REPO_PATH = r"C:\Users\weibi\Desktop\InventoryMangement\Inventory" 

# The name of the inventory file
FILENAME = "inventory.json"

# Derived Paths
LOCAL_FILE = os.path.join(os.getcwd(), FILENAME)
REMOTE_FILE = os.path.join(DATA_REPO_PATH, FILENAME)

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory System")
        self.root.geometry("1200x700")
        
        # Intercept the window close button (X)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load Inventory
        self.inventory = self.load_inventory()

        # --- Top Control Panel ---
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)

        # PULL BUTTON
        self.btn_pull = tk.Button(
            control_frame, 
            text="⬇ Pull Remote", 
            bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
            command=self.pull_inventory_data
        )
        self.btn_pull.pack(side="left", padx=(0, 5))

        # FINALIZE BUTTON
        self.btn_finalize = tk.Button(
            control_frame, 
            text="✔ Finalize Transaction (Save)", 
            bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
            command=self.finalize_transaction
        )
        self.btn_finalize.pack(side="left", padx=(5, 5))

        # PUSH BUTTON
        self.btn_push = tk.Button(
            control_frame, 
            text="⬆ Push to Git", 
            bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
            command=self.push_inventory_data
        )
        self.btn_push.pack(side="left", padx=(5, 5))
        
        
        # ADD ROWS BUTTON
        self.btn_add_rows = tk.Button(
            control_frame, 
            text="+ Add 10 Rows", 
            bg="#9E9E9E", fg="white", font=("Arial", 10, "bold"),
            command=self.add_more_rows
        )
        self.btn_add_rows.pack(side="left", padx=(5, 5))
        
        # COPY GRID BUTTON
        self.btn_copy = tk.Button(
            control_frame, 
            text="📋 Copy Grid", 
            bg="#673AB7", fg="white", font=("Arial", 10, "bold"),
            command=self.copy_grid_to_clipboard
        )
        self.btn_copy.pack(side="left", padx=(5, 5))
        
        # CLEAR GRID
        self.btn_add_rows = tk.Button(
            control_frame, 
            text="Clear Grid", 
            bg="#f74545", fg="white", font=("Arial", 10, "bold"),
            command=self.clear_grid
        )
        self.btn_add_rows.pack(side="left", padx=(5, 0))
        
        
        
        # Legend
        tk.Label(control_frame, text="Legend: ", font=("Arial", 10, "bold")).pack(side="left", padx=(40, 0))
        tk.Label(control_frame, text=" OK ", bg="#DFF0D8").pack(side="left", padx=2)
        tk.Label(control_frame, text=" Oversold ", bg="orange").pack(side="left", padx=2)
        tk.Label(control_frame, text=" Invalid ID ", bg="#FFCDD2").pack(side="left", padx=2)
        
        # --- Time Input Panel ---
        time_frame = tk.Frame(self.root)
        time_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Variables to store the inputs
        self.month_var = tk.StringVar()
        self.day_var = tk.StringVar()
        self.hour_var = tk.StringVar()
        self.minute_var = tk.StringVar()
        self.ampm_var = tk.StringVar()

        tk.Label(time_frame, text="Start Time: ", font=("Arial", 20, "bold")).pack(side="left")

        tk.Entry(time_frame, textvariable=self.month_var, width=5, font=("Arial", 20, "bold")).pack(side="left")
        tk.Label(time_frame, text="Month", font=("Arial", 20)).pack(side="left", padx=(2, 10))

        tk.Entry(time_frame, textvariable=self.day_var, width=5, font=("Arial", 20, "bold")).pack(side="left")
        tk.Label(time_frame, text="Day", font=("Arial", 20)).pack(side="left", padx=(2, 10))

        tk.Entry(time_frame, textvariable=self.hour_var, width=5, font=("Arial", 20, "bold")).pack(side="left")
        tk.Label(time_frame, text="Hour", font=("Arial", 20)).pack(side="left", padx=(2, 10))

        tk.Entry(time_frame, textvariable=self.minute_var, width=5, font=("Arial", 20, "bold")).pack(side="left")
        tk.Label(time_frame, text="Minute", font=("Arial", 20)).pack(side="left", padx=(2, 10))

        tk.Entry(time_frame, textvariable=self.ampm_var, width=5, font=("Arial", 20, "bold")).pack(side="left")
        tk.Label(time_frame, text="AM/PM", font=("Arial", 20)).pack(side="left", padx=(2, 10))

        # --- Sheet Setup ---
        self.sheet_frame = tk.Frame(self.root)
        self.sheet_frame.pack(fill="both", expand=True, padx=10, pady=10)

        headers = ["Buyer"] + ["Item ID"] * 10
        
        self.sheet = Sheet(self.sheet_frame,
                           headers=headers,
                           total_columns=11,
                           total_rows=15)
        
        self.sheet.enable_bindings(("single_select", "row_select", "column_width_resize", 
                                    "arrowkeys", "rc_select", "copy", "cut", "paste", 
                                    "delete", "undo", "edit_cell"))
        self.sheet.pack(fill="both", expand=True)

        # Bind events
        self.sheet.extra_bindings("end_edit_cell", func=self.validate_entire_sheet)
        self.sheet.extra_bindings("end_paste", func=self.validate_entire_sheet)
        
        
        #self.sheet.set_all_cell_sizes_to_text()
        self.sheet.set_column_widths([200] + [85] * 10)

    def on_closing(self):
        """Prompt the user before closing the application."""
        if messagebox.askyesno("Exit Confirmation", "Are you sure you want to exit?\nUnsaved work on the grid will be lost."):
            self.root.destroy()
            
    def add_more_rows(self):
        """Adds 10 empty rows to the bottom of the sheet."""
        for _ in range(10):
            self.sheet.insert_row() # Appends a row by default
        self.sheet.redraw()
        
    def copy_grid_to_clipboard(self):
        """Copies headers + data to clipboard as Tab-Separated Values (TSV)."""
        try:
            # Format as TSV (Tab Separated Values)
            clipboard_text = ""
            
            # Get Headers and Variables
            headers = self.sheet.headers()
            m = self.month_var.get()
            d = self.day_var.get()
            h = self.hour_var.get()
            mins = self.minute_var.get()
            ampm = self.ampm_var.get()
            
            clipboard_text += f"{m}\tMonth\t{d}\tDay\t{h}\tHour\t{mins}\tMinutes\t{ampm}\tAM/PM\n"
            
            # Add Headers
            clipboard_text += "\t".join([str(h) for h in headers]) + "\n"
            
            # Get Data
            data = self.sheet.get_sheet_data()
            
            # Add Rows
            for row in data:
                # Convert None to empty string
                clean_row = [str(x) if x is not None else "" for x in row]
                clipboard_text += "\t".join(clean_row) + "\n"
            
            # Push to Clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(clipboard_text)
            self.root.update()
            
            messagebox.showinfo("Success", "Grid copied to clipboard!\nYou can now Paste (Ctrl+V) into excel/sheets.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {e}")
    
    def clear_grid(self):
        """Clears the grid"""
        # Clear Sheet
        if not messagebox.askyesno("Clear Grid","This will clear the grid. Unsaved changes will be lost. Proceed?"):
            return
        self.sheet.set_sheet_data([["" for _ in range(11)] for _ in range(30)])

        
        
    def load_inventory(self):
        """
        Load the inventory from the local provided json file. If remote file is provided, copy that to local file.
        """
        if not os.path.exists(LOCAL_FILE):
            if os.path.exists(REMOTE_FILE):
                shutil.copy(REMOTE_FILE, LOCAL_FILE)
            else:
                return {}
        try:
            with open(LOCAL_FILE, 'r') as f:
                data = json.load(f)
                return {k.upper(): v for k, v in data.items()}
        except Exception as e:
            print(f"Load Error: {e}")
            return {}

    def save_inventory_locally(self):
        """
        Write local changes to the local json file. The local file will be changed, but not committed or pushed.
        """
        try:
            with open(LOCAL_FILE, 'w') as f:
                json.dump(self.inventory, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file: {e}")

    def finalize_transaction(self):
        """
        Updates inventory and ALERTS if items hit 0 stock.
        """
        # Tally Items
        all_data = self.sheet.get_sheet_data()
        transaction_counts = Counter()
        
        for row_data in all_data:
            for item in row_data[1:]: 
                item_str = str(item).strip().upper()
                if item_str:
                    transaction_counts[item_str] += 1
        
        if not transaction_counts:
            messagebox.showinfo("Info", "No items to finalize.")
            return

        # Validate before committing
        for item_id, qty_needed in transaction_counts.items():
            if item_id not in self.inventory:
                messagebox.showerror("Error", f"Item '{item_id}' is invalid.")
                return
            if qty_needed > self.inventory[item_id]:
                messagebox.showerror("Error", f"Item '{item_id}' is oversold.")
                return

        # Confirm
        confirm = messagebox.askyesno("Confirm", "Finalize transaction and update inventory?")
        if not confirm:
            return

        # Update Inventory & Track Zeros
        items_hit_zero = [] # List to track items that become out of stock

        for item_id, qty_used in transaction_counts.items():
            self.inventory[item_id] -= qty_used
            
            # Check if it is now exactly zero
            if self.inventory[item_id] == 0:
                items_hit_zero.append(item_id)
        
        self.save_inventory_locally()
        
        # Clear Sheet
        # self.sheet.set_sheet_data([["" for _ in range(11)] for _ in range(30)])
        # self.sheet.redraw()

        # Success Message + OUT OF STOCK WARNING
        success_msg = "Transaction Finalized Successfully!"
        
        if items_hit_zero:
            # Create a warning list string
            zero_list_str = "\n".join([f"• {item}" for item in items_hit_zero])
            warning_msg = f"{success_msg}\n\n The following items are now OUT OF STOCK:\n{zero_list_str}\n Change it on the platform!!"
            
            # Use warning for emphasis
            messagebox.showwarning("Stock Alert", warning_msg)
        else:
            messagebox.showinfo("Success", success_msg)

            
    def pull_inventory_data(self):
        """
        Forces the local data to match the remote Git repository exactly.
        Uses 'git reset --hard' instead of 'git pull' to overwrite local conflicts.
        """
        if not os.path.exists(DATA_REPO_PATH):
            messagebox.showerror("Error", f"Data Repo path not found:\n{DATA_REPO_PATH}")
            return

        # Forced actions on unsaved changes
        if not messagebox.askyesno("Force Update", "This will overwrite your local inventory with the version from Git.\nAny unsaved changes will be lost.\nProceed?"):
            return

        try:
            # Fetch all latest changes from the remote (without merging yet)
            fetch_result = subprocess.run(
                ["git", "fetch", "--all"], 
                cwd=DATA_REPO_PATH, 
                capture_output=True, 
                text=True
            )

            # FORCE Reset the repo to match origin/main
            reset_result = subprocess.run(
                ["git", "reset", "--hard", "origin/main"], 
                cwd=DATA_REPO_PATH, 
                capture_output=True, 
                text=True
            )
            
            if reset_result.returncode != 0:
                messagebox.showerror("Git Error", f"Reset failed:\n{reset_result.stderr}")
                return

            # Copy the fresh file from Data Repo to Script Folder
            if os.path.exists(REMOTE_FILE):
                shutil.copy(REMOTE_FILE, LOCAL_FILE)
                
                # Reload the data into the App memory
                self.inventory = self.load_inventory()
                
                # Re-validate the sheet (update colors based on new stock)
                self.validate_entire_sheet()
                
                messagebox.showinfo("Success", f"Inventory Force Updated!\nServer status: {reset_result.stdout}")
            else:
                messagebox.showerror("Error", "inventory.json missing from data repo.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def push_inventory_data(self):
        """
        git add, commit, push to the repo by calling a bash script.
        """
        try:
            shutil.copy(LOCAL_FILE, REMOTE_FILE)
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy inventory to repo: {e}")
            return

        bash_script_path = "./git_sync.sh"
        bat_script_path = "git_sync.bat"
        
        try:
            
            # Git Bash/Linux
            #result = subprocess.run(["bash", bash_script_path, DATA_REPO_PATH], capture_output=True, text=True)
            # Windows
            result = subprocess.run(["cmd.exe", "/c", bat_script_path, DATA_REPO_PATH], capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Git Push Success", result.stdout)
            else:
                messagebox.showerror("Git Push Error", result.stderr)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def validate_entire_sheet(self, event=None):
        """
        Validate every cell in the sheet against inventory to see if anything is invalid or oversold. 
        """
        try:
            all_data = self.sheet.get_sheet_data()
            item_counts = Counter()
            
            for row_data in all_data:
                for item in row_data[1:]: 
                    item_str = str(item).strip().upper()
                    if item_str:
                        item_counts[item_str] += 1
            
            for row_idx, row_data in enumerate(all_data):
                for col_idx in range(1, 11): 
                    raw_val = row_data[col_idx]
                    if raw_val is None: item_id = ""
                    else: item_id = str(raw_val).strip().upper()

                    if not item_id:
                        # Don't highlight if None
                        self.sheet.highlight_cells(row=row_idx, column=col_idx, bg=None, redraw=False)
                        continue

                    if item_id not in self.inventory:
                        # Invalid - Red
                        self.sheet.highlight_cells(row=row_idx, column=col_idx, bg="#FFCDD2", redraw=False)
                    elif item_counts[item_id] > self.inventory[item_id]:
                        # Oversold - Orange
                        self.sheet.highlight_cells(row=row_idx, column=col_idx, bg="orange", redraw=False)
                    else:
                        # OK - Green
                        self.sheet.highlight_cells(row=row_idx, column=col_idx, bg="#DFF0D8", redraw=False)
            
            self.sheet.redraw()
        except Exception:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()