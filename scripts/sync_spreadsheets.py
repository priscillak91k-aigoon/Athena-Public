import os
import json
import pandas as pd
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_PATH = "life_data/Symphony_Life_Data.xlsx"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Supabase credentials not found in .env")
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

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
        "Date": [datetime.now().strftime("%Y-%m-%d")],
        "Total Points Earned": [0],
        "Notes": ["Initialized gamification tracking."]
    }
    
    finances_data = {
        "Category": ["Gross Pay (28.5 hrs @ $24)", "PAYE Tax & ACC (M SL)", "Student Loan (12%)", "KiwiSaver (3%)", "Estimated Net Pay", "Remaining Buffer"],
        "Amount": ["$684.00", "-$108.20", "-$29.52", "-$20.52", "$525.76", "$525.76"],
        "Notes": ["Base Income", "Calculated annualized $35,568", "Over $438/wk threshold", "Minimum rate", "Take-home pay", "Available for expenses"]
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
    write_to_excel({
        "Routine & Points": df_routine,
        "Daily Logs": df_daily,
        "Finances": df_finances,
        "Ideas & Projects": df_ideas,
        "Contacts & Events": df_contacts
    })
    print("Spreadsheet successfully created!")

def write_to_excel(sheet_dict):
    """Safely write a dictionary of dataframes to the Excel file."""
    with pd.ExcelWriter(SPREADSHEET_PATH, engine='openpyxl') as writer:
        for sheet_name, df in sheet_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

def push_to_cloud():
    """Reads local Excel file and pushes JSON representations up to Supabase user_data."""
    if not os.path.exists(SPREADSHEET_PATH):
        print("Excel file not found. Initialize first.")
        return
        
    print("Reading local Excel data...")
    try:
        xls = pd.ExcelFile(SPREADSHEET_PATH)
        
        # Convert all sheets to JSON
        cloud_payload = {}
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # Format dates nicely to string to avoid JSON serialization errors
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].dt.strftime('%Y-%m-%d')
            
            # Use 'records' orient for array of objects cleanly ingestible by JS
            cloud_payload[sheet_name] = json.loads(df.to_json(orient="records", date_format='iso'))
            
        print("Pushing to Supabase (column: excel_payload)...")
        supabase = get_supabase_client()
        if not supabase: return
        
        payload_string = json.dumps(cloud_payload)
        
        supabase.table("user_data").update({
            "excel_payload": payload_string
        }).eq("id", 1).execute()
        
        print("Successfully synced local Excel data TO Cloud!")
    except Exception as e:
        print(f"Error pushing to cloud: {e}")

def pull_dashboard_points_from_cloud():
    """Pulls current web dashboard points and logs them into the Daily Logs sheet."""
    print("Pulling Daily Points from Supabase...")
    supabase = get_supabase_client()
    if not supabase: return
    
    try:
        db_response = supabase.table("user_data").select("dashboard_points").eq("id", 1).execute()
        if db_response.data and db_response.data[0].get("dashboard_points"):
            current_points = db_response.data[0]["dashboard_points"]
            print(f"Found {current_points} points in cloud for today. Updating Excel...")
            
            if os.path.exists(SPREADSHEET_PATH):
                xls = pd.ExcelFile(SPREADSHEET_PATH)
                df_daily = pd.read_excel(xls, sheet_name="Daily Logs")
                
                today = datetime.now().strftime("%Y-%m-%d")
                
                # Check if today exists in the sheet
                if today in df_daily['Date'].values:
                    # Update today's points
                    df_daily.loc[df_daily['Date'] == today, 'Total Points Earned'] = current_points
                else:
                    # Append new row
                    new_row = {"Date": today, "Total Points Earned": current_points, "Notes": "Pulled from Cloud."}
                    df_daily = pd.concat([df_daily, pd.DataFrame([new_row])], ignore_index=True)
                
                # We need to maintain the other sheets when writing back
                sheet_dict = {name: pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names if name != "Daily Logs"}
                sheet_dict["Daily Logs"] = df_daily
                
                write_to_excel(sheet_dict)
                print("Daily Logs successfully updated from Cloud!")
        else:
            print("No dashboard points found in cloud to sync.")
            
    except Exception as e:
        print(f"Error pulling from cloud: {e}")

if __name__ == "__main__":
    if not os.path.exists("life_data"):
        os.makedirs("life_data")
        
    print("--- Life Engine Sync Orchestrator ---")
    print("1: Initialize Local Spreadsheet")
    print("2: Push Local Spreadsheet to Cloud")
    print("3: Pull Dashboard Points to Local Spreadsheet")
    
    choice = input("Select an option (1-3): ")
    if choice == '1':
        initialize_spreadsheet()
    elif choice == '2':
        push_to_cloud()
    elif choice == '3':
        pull_dashboard_points_from_cloud()
    else:
        print("Invalid choice.")
