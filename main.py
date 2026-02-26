# os module lets us check if files exist on disk
import os
# hashlib lets us hash passwords (one-way encryption)
import hashlib
# json lets us save/load data as .json files (like a mini database)
import json

# This is the file where we'll store everything
STORAGE_FILE = "storage.json"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def save_storage(data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_storage():
    with open(STORAGE_FILE, "r") as f:
        return json.load(f)


# First-time setup: ask user to create a master password
def setup_master_password():
    print("=== First Time Setup ===")

    # Keep asking until both entries match
    while True:
        master = input("Create a master password: ")
        confirm = input("Confirm master password: ")
        if master == confirm:
            break  # exit the loop — passwords match!
        print("Passwords do not match. Try again.\n")

    # Build the data structure to save
    # We store the HASH, never the plain password
    data = {
        "master_hash": hash_password(master),
        "passwords": {}  # empty dict — no saved passwords yet
    }

    save_storage(data)
    print("Master password created successfully!\n")
    return data


# Verify master password — returns True if correct, False if not
def verify_master_password(data):
    print("=== Password Manager Login ===")

    # Give the user 3 attempts
    # range(3) gives us: 0, 1, 2
    for attempt in range(3):
        master = input("Enter master password: ")

        # Hash what they typed, compare with stored hash
        # We NEVER compare plain passwords — always compare hashes
        if hash_password(master) == data["master_hash"]:
            print("Access granted!\n")
            return True  # correct password!

        # Calculate remaining attempts: on attempt 0 → 2 left, attempt 1 → 1 left, attempt 2 → 0 left
        remaining = 2 - attempt
        print(f"Incorrect password. {remaining} attempt(s) remaining.")

    print("Too many failed attempts. Exiting.")
    return False  # all 3 attempts failed


# Add a new password entry
def add_password(data):
    print("=== Add Password ===")

    # .strip() removes leading/trailing spaces
    # .lower() converts to lowercase so "Google" and "google" are the same site
    site = input("Enter site/service name: ").strip().lower()
    username = input("Enter username or email: ").strip()
    password = input("Enter password: ")

    # data["passwords"] is a dict — we add a new key (site name)
    # with a value that is another dict (username + password)
    data["passwords"][site] = {
        "username": username,
        "password": password
    }

    # Save to file so it persists — without this, data is lost when program closes
    save_storage(data)

    print(f"Password for '{site}' saved!\n")


# Look up a single site and show its credentials
def view_password(data):
    print("=== View Password ===")
    site = input("Enter site name: ").strip().lower()

    # Check if the site key exists in the passwords dict
    if site in data["passwords"]:
        entry = data["passwords"][site]  # entry is a dict: {username, password}
        print(f"\n  Site:     {site}")
        print(f"  Username: {entry['username']}")
        print(f"  Password: {entry['password']}\n")
    else:
        # site not found — tell the user instead of crashing
        print(f"No entry found for '{site}'.\n")


# Show all saved site names (without passwords)
def list_sites(data):
    print("=== Saved Sites ===")

    # Check if the passwords dict is empty
    if not data["passwords"]:
        print("No passwords saved yet.\n")
        return  # exit the function early — nothing to show

    # enumerate() gives us a counter alongside each item
    # enumerate(["a","b"], 1) → (1,"a"), (2,"b")
    for i, site in enumerate(data["passwords"], 1):
        print(f"  {i}. {site}")
    print()  # blank line for spacing


# Delete a saved password entry
def delete_password(data):
    print("=== Delete Password ===")

    # First show the list so user knows what exists
    list_sites(data)

    # If there's nothing to delete, list_sites already told them — just return
    if not data["passwords"]:
        return

    site = input("Enter site name to delete: ").strip().lower()

    if site in data["passwords"]:
        # Ask for confirmation before deleting — safety check
        confirm = input(f"Are you sure you want to delete '{site}'? (y/n): ").strip().lower()
        if confirm == "y":
            # del removes a key from a dictionary permanently
            del data["passwords"][site]
            save_storage(data)  # save the updated data to file
            print(f"'{site}' deleted.\n")
        else:
            print("Cancelled.\n")  # user changed their mind
    else:
        print(f"No entry found for '{site}'.\n")


# The main menu — loops until user chooses to exit
def show_menu(data):
    while True:
        print("=== Password Manager ===")
        print("  1. Add password")
        print("  2. View password")
        print("  3. List all sites")
        print("  4. Delete password")
        print("  5. Exit")

        # .strip() removes extra spaces the user might type
        choice = input("Choose an option (1-5): ").strip()

        # Check what the user picked
        if choice == "1":
            add_password(data)
        elif choice == "2":
            view_password(data)
        elif choice == "3":
            list_sites(data)
        elif choice == "4":
            delete_password(data)
        elif choice == "5":
            print("Goodbye!")
            break  # exit the while loop → program ends
        else:
            # Anything other than 1-5
            print("Invalid option. Try again.\n")


# --- MAIN PROGRAM ---
if os.path.exists(STORAGE_FILE):
    data = load_storage()
    if verify_master_password(data):
        show_menu(data)  # password correct → show menu
else:
    data = setup_master_password()
    show_menu(data)  # just created account → show menu
