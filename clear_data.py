import os
import glob # This import is correct

def delete_files(patterns):
    """Deletes files matching the given glob patterns."""
    for pattern in patterns:
        files = glob.glob(pattern)
        for f in files:
            try:
                if os.path.isfile(f):
                    os.remove(f)
                    print(f"Deleted file: {f}")
            except OSError as e:
                print(f"Error deleting file {f}: {e}")

def clear_all_data():
    """
    Clears all project data.
    
    - Deletes SQLite database files.
    - Deletes CSV data files.
    - Deletes other data files like .pkl or .json.
    """
    print("Starting data clearing process...")

    # Add file patterns for data files you want to delete.
    # For example, if you have .db, .csv, .json, or .pkl files.
    file_patterns_to_delete = [
        "*.db",          # For SQLite databases
        "data/*.csv",    # For CSV files in a 'data' directory
    ]

    delete_files(file_patterns_to_delete)
    print("Data clearing process finished.")

if __name__ == "__main__":
    clear_all_data()