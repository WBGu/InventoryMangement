# Inventory Management

A Python-based GUI for managing inventory via an Excel-like grid. 
This system is designed with a dual-repository architecture, separating the application code from high-frequency inventory data updates to maintain a clean Git history.

## Features

* **Interactive Grid:** Excel-like interface powered by `tksheet` for fast data entry.
* **Real-Time Validation:** Automatically highlights cells:
    * **Green:** Valid Item ID and in stock.
    * **Orange:** Oversold (entered quantity exceeds available stock).
    * **Red:** Invalid Item ID (does not exist in inventory).
* **Git Integration:** Built-in buttons to force-pull fresh inventory data from a remote repository and push updated data back.
* **Transaction Finalization:** Tallies grid items, deducts them from the master inventory, and alerts the user if any items hit zero stock.
* **Clipboard Export:** Easily copy the grid data (along with a customizable start time) as Tab-Separated Values (TSV) to paste directly into Google Docs or Excel.

---

## Project Structure

This system requires two separate folders (repositories):

1.  **The Application Repo (Code)**
    * `inventory_app.py` - The main Python GUI application.
    * `Start_Inventory.bat` - Windows launcher to start the application.
	* `Start_Inventory.sh` - bash script to start the application.
    * `git_sync.bat` - Windows script to handle Git commits and pushes.
	* `./git_sync.sh` - bash script to bandle Git commits and pushes
    * `README.md` - This file.

2.  **The Data Repo (Inventory)**
    * `inventory.json` - The JSON dictionary tracking item IDs and quantities.
    * *(Must be a designated Git repository with a remote origin set).*

---

## Prerequisites & Installation

1.  **Install Python:** Ensure Python 3.x is installed and added to your system PATH.
2.  **Install Git:** Ensure Git for Windows is installed and accessible via the command prompt.
3.  **Install Dependencies:** Open your terminal or command prompt and run:
    ```bash
    pip install tksheet
    ```

---

## Configuration

Before running the application, you must link the App to your Data Repo.

1.  Open `inventory_app.py` in a text editor.
2.  Locate the configuration section at the top of the file.
3.  Update the `DATA_REPO_PATH` variable to point to the exact file path of your Data Repo.
    ```python
    # Example:
    DATA_REPO_PATH = r"C:\Users\YourName\Documents\InventoryDataRepo"
    ```

---

## Usage Guide

### Starting the App
Double-click the **`start_inventory.bat`** file. This will automatically open the Python GUI.

### Daily Workflow
1.  **Pull Data:** Click `Pull Remote` at the start of your session to ensure you have the latest `inventory.json` from the server. *(Note: This does a hard reset to match the server exactly).*
2.  **Enter Time:** Fill in the "Start Time" slots (Month, Day, Hour, Minute, AM/PM) for your records.
3.  **Input Data:** Scan or type Item IDs into the grid under the respective Buyer. 
4.  **Copy Grid (Optional):** Click `Copy Grid` to copy the session's data to your clipboard for reporting in spreadsheets.
5.  **Finalize:** Click `Finalize Transaction` to officially deduct the items from your local `inventory.json`. The grid will clear for the next batch.
6.  **Push Data:** Click `Push to Git` to commit your local changes and push them back to the remote server.
---

## Troubleshooting

* **App won't open:** Check the command prompt window launched by `start_inventory.bat`. If it says "ModuleNotFoundError," ensure you ran `pip install tksheet`.
* **Git Push/Pull Fails:** Ensure your Data Repo is a valid Git repository (`git init`), has a remote origin set (`git remote add origin <URL>`), and you have the proper authentication/permissions to push to it.
* **Cells remain white:** Ensure your `DATA_REPO_PATH` is correct and that `inventory.json` exists in that folder.