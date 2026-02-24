import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_PATH = "life_data/Symphony_Life_Data.xlsx"

def initialize_spreadsheet():
    """Create the initial spreadsheet with all required tabs and template data."""
    if os.path.exists(SPREADSHEET_PATH):
        print(f"{SPREADSHEET_PATH} already exists. Skipping initialization.")
        return

    print(f"Creating new Life Data spreadsheet at {SPREADSHEET_PATH}...")
    
    # Template Data
    routine_data = {
        "Task Category": ["Cleaning", "Cleaning", "Cleaning", "Household", "Health", "Household"],
        "Task Name": [
            "Dishes",
            "Put stuff away",
            "Make boys' bed",
            "Catch up on washing (hang outside)",
            "3-Day Longevity Home Workout Split",
            "Pick up Quinn poop from lawn"
        ],
        "Points Value": [1, 1, 1, 3, 5, 2]
    }
    
    daily_logs_data = {
        "Date": ["2026-02-25"],
        "Total Points Earned": [0],
        "Notes": ["Initialized gamification tracking."]
    }
    
    finances_data = {
        "Category": ["Income", "Groceries", "Utilities", "Savings", "Miscellaneous"],
        "Amount": [0, 0, 0, 0, 0],
        "Notes": ["", "", "", "", ""]
    }
    
    ideas_data = {
        "Project/Idea": ["Caravan track vehicle"],
        "Status": ["To Do"],
        "Cost Estimate": ["TBD"],
        "Notes": ["Look into logistics of hiring, dropping off, and picking up track vehicle."]
    }
    
    contacts_data = {
        "Name": ["Parker", "Tash", "Sarah"],
        "Relationship": ["Family", "Family", "Family"],
        "Birth Date": ["", "", ""],
        "Notes": ["", "", ""]
    }

    # Create DataFrames
    df_routine = pd.DataFrame(routine_data)
    df_daily = pd.DataFrame(daily_logs_data)
    df_finances = pd.DataFrame(finances_data)
    df_ideas = pd.DataFrame(ideas_data)
    df_contacts = pd.DataFrame(contacts_data)

    # Write to Excel with multiple sheets
    with pd.ExcelWriter(SPREADSHEET_PATH, engine='openpyxl') as writer:
        df_routine.to_excel(writer, sheet_name="Routine & Points", index=False)
        df_daily.to_excel(writer, sheet_name="Daily Logs", index=False)
        df_finances.to_excel(writer, sheet_name="Finances", index=False)
        df_ideas.to_excel(writer, sheet_name="Ideas & Projects", index=False)
        df_contacts.to_excel(writer, sheet_name="Contacts & Events", index=False)
        
    print("Spreadsheet successfully created!")

if __name__ == "__main__":
    if not os.path.exists("life_data"):
        os.makedirs("life_data")
    initialize_spreadsheet()
