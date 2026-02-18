import tkinter as tk
from tkinter import messagebox
from tksheet import Sheet
import subprocess
import os
import json
import shutil
from collections import Counter

# --- CONFIGURATION ---
# UPDATE THIS PATH to your separate Data Repo folder
DATA_REPO_PATH = r"C:\Users\weibi\Desktop\InventoryMangement\Inventory" 

# The name of the file
FILENAME = "inventory.json"

# Derived Paths
LOCAL_FILE = os.path.join(os.getcwd(), FILENAME)
REMOTE_FILE = os.path.join(DATA_REPO_PATH, FILENAME)

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory System - POS View")
        self.root.geometry("1200x700")
        
        # Load Inventory
        self.inventory = self.load_inventory()

        # --- Top Control Panel ---
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)

        # 1. PULL BUTTON
        self.btn_pull = tk.Button(
            control_frame, 
            text="⬇ Pull Remote", 
            bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
            command=self.pull_inventory_data
        )
        self.btn_pull.pack(side="left", padx=(0, 5))

        # 2. FINALIZE BUTTON
        self.btn_finalize = tk.Button(
            control_frame, 
            text="✔ Finalize Transaction (Save)", 
            bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
            command=self.finalize_transaction
        )
        self.btn_finalize.pack(side="left", padx=(5, 5))

        # 3. PUSH BUTTON
        self.btn_push = tk.Button(
            control_frame, 
            text="⬆ Push to Git", 
            bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
            command=self.push_inventory_data
        )
        self.btn_push.pack(side="left", padx=(5, 0))
        
        # Legend
        tk.Label(control_frame, text="Legend: ", font=("Arial", 10, "bold")).pack(side="left", padx=(40, 0))
        tk.Label(control_frame, text=" OK ", bg="#DFF0D8").pack(side="left", padx=2)
        tk.Label(control_frame, text=" Oversold ", bg="orange").pack(side="left", padx=2)
        tk.Label(control_frame, text=" Invalid ID ", bg="#FFCDD2").pack(side="left", padx=2)

        # --- Sheet Setup ---
        self.sheet_frame = tk.Frame(self.root)
        self.sheet_frame.pack(fill="both", expand=True, padx=10, pady=10)

        headers = ["Buyer"] + ["Item ID"] * 10
        
        self.sheet = Sheet(self.sheet_frame,
                           headers=headers,
                           total_columns=11,
                           total_rows=30)
        
        self.sheet.enable_bindings(("single_select", "row_select", "column_width_resize", 
                                    "arrowkeys", "rc_select", "copy", "cut", "paste", 
                                    "delete", "undo", "edit_cell"))
        self.sheet.pack(fill="both", expand=True)

        # Bind events
        self.sheet.extra_bindings("end_edit_cell", func=self.validate_entire_sheet)
        self.sheet.extra_bindings("end_paste", func=self.validate_entire_sheet)
        
        self.sheet.set_all_cell_sizes_to_text()

    def load_inventory(self):
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
        try:
            with open(LOCAL_FILE, 'w') as f:
                json.dump(self.inventory, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file: {e}")

    def finalize_transaction(self):
        """
        Updates inventory and ALERTS if items hit 0 stock.
        """
        # 1. Tally Items
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

        # 2. Validate before committing
        for item_id, qty_needed in transaction_counts.items():
            if item_id not in self.inventory:
                messagebox.showerror("Error", f"Item '{item_id}' is invalid.")
                return
            if qty_needed > self.inventory[item_id]:
                messagebox.showerror("Error", f"Item '{item_id}' is oversold.")
                return

        # 3. Confirm
        confirm = messagebox.askyesno("Confirm", "Finalize transaction and update inventory?")
        if not confirm:
            return

        # 4. Update Inventory & Track Zeros
        items_hit_zero = [] # List to track items that become out of stock

        for item_id, qty_used in transaction_counts.items():
            self.inventory[item_id] -= qty_used
            
            # Check if it is now exactly zero
            if self.inventory[item_id] == 0:
                items_hit_zero.append(item_id)
        
        self.save_inventory_locally()
        
        # 5. Clear Sheet
        self.sheet.set_sheet_data([["" for _ in range(11)] for _ in range(30)])
        self.sheet.redraw()

        # 6. Success Message + OUT OF STOCK WARNING
        success_msg = "Transaction Finalized Successfully!"
        
        if items_hit_zero:
            # Create a warning list string
            zero_list_str = "\n".join([f"• {item}" for item in items_hit_zero])
            warning_msg = f"{success_msg}\n\n The following items are now OUT OF STOCK:\n{zero_list_str}"
            
            # Use showwarning for emphasis
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

        # Warning: This is a destructive action for unsaved changes
        if not messagebox.askyesno("Force Update", "This will overwrite your local inventory with the version from Git.\nAny unsaved changes will be lost.\nProceed?"):
            return

        try:
            # 1. Fetch all latest changes from the remote (without merging yet)
            fetch_result = subprocess.run(
                ["git", "fetch", "--all"], 
                cwd=DATA_REPO_PATH, 
                capture_output=True, 
                text=True
            )

            # 2. FORCE Reset the repo to match origin/main
            # Note: If your branch is 'master', change 'origin/main' to 'origin/master'
            reset_result = subprocess.run(
                ["git", "reset", "--hard", "origin/main"], 
                cwd=DATA_REPO_PATH, 
                capture_output=True, 
                text=True
            )
            
            if reset_result.returncode != 0:
                messagebox.showerror("Git Error", f"Reset failed:\n{reset_result.stderr}")
                return

            # 3. Copy the fresh file from Data Repo to Script Folder
            if os.path.exists(REMOTE_FILE):
                shutil.copy(REMOTE_FILE, LOCAL_FILE)
                
                # 4. Reload the data into the App memory
                self.inventory = self.load_inventory()
                
                # 5. Re-validate the sheet (update colors based on new stock)
                self.validate_entire_sheet()
                
                messagebox.showinfo("Success", f"Inventory Force Updated!\nServer status: {reset_result.stdout}")
            else:
                messagebox.showerror("Error", "inventory.json missing from data repo.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def push_inventory_data(self):
        try:
            shutil.copy(LOCAL_FILE, REMOTE_FILE)
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy inventory to repo: {e}")
            return

        script_path = "./git_sync.sh"
        try:
            result = subprocess.run(["bash", script_path, DATA_REPO_PATH], capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Git Push Success", result.stdout)
            else:
                messagebox.showerror("Git Push Error", result.stderr)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def validate_entire_sheet(self, event=None):
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
                        self.sheet.highlight_cells(row=row_idx, column=col_idx, bg=None, redraw=False)
                        continue

                    if item_id not in self.inventory:
                        self.sheet.highlight_cells(row=row_idx, column=col_idx, bg="#FFCDD2", redraw=False)
                    elif item_counts[item_id] > self.inventory[item_id]:
                        self.sheet.highlight_cells(row=row_idx, column=col_idx, bg="orange", redraw=False)
                    else:
                        self.sheet.highlight_cells(row=row_idx, column=col_idx, bg="#DFF0D8", redraw=False)
            
            self.sheet.redraw()
        except Exception:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()