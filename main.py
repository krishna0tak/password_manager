# os module lets us check if files exist on disk
import os
# hashlib lets us hash passwords (one-way encryption)
import hashlib
# json lets us save/load data as .json files (like a mini database)
import json
# getpass hides password input so it's not visible as you type
import getpass
# secrets generates cryptographically secure random characters
import secrets
# string gives us character sets: letters, digits, punctuation
import string

# This is the file where we'll store everything
STORAGE_FILE = "storage.json"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Generate a strong random password
# secrets is safer than random — designed for security-sensitive tasks
def generate_password(length=16):
    # Build a pool of all possible characters
    chars = string.ascii_letters + string.digits + string.punctuation
    # Pick 'length' characters randomly from the pool
    return "".join(secrets.choice(chars) for _ in range(length))


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
        # getpass.getpass() hides the text as you type (shows nothing)
        master = getpass.getpass("Create a master password: ")
        confirm = getpass.getpass("Confirm master password: ")
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
        master = getpass.getpass("Enter master password: ")

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

    # Offer to generate a password or enter manually
    choice = input("Generate a strong password? (y/n): ").strip().lower()
    if choice == "y":
        length = input("Length? (press Enter for 16): ").strip()
        length = int(length) if length.isdigit() else 16
        password = generate_password(length)
        print(f"Generated: {password}")
    else:
        # getpass hides the password as the user types it
        password = getpass.getpass("Enter password: ")

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


# Update an existing password entry
def update_password(data):
    print("=== Update Password ===")
    list_sites(data)

    if not data["passwords"]:
        return

    site = input("Enter site name to update: ").strip().lower()

    if site not in data["passwords"]:
        print(f"No entry found for '{site}'.\n")
        return

    print(f"Updating '{site}' — press Enter to keep current value.")

    # Show current username and allow changing it
    current_user = data["passwords"][site]["username"]
    new_user = input(f"New username [{current_user}]: ").strip()
    if new_user:  # only update if user typed something
        data["passwords"][site]["username"] = new_user

    # Offer generate or manual for new password
    choice = input("Generate a new strong password? (y/n): ").strip().lower()
    if choice == "y":
        length = input("Length? (press Enter for 16): ").strip()
        length = int(length) if length.isdigit() else 16
        new_pass = generate_password(length)
        print(f"Generated: {new_pass}")
        data["passwords"][site]["password"] = new_pass
    else:
        new_pass = getpass.getpass("New password (press Enter to keep current): ")
        if new_pass:  # only update if user typed something
            data["passwords"][site]["password"] = new_pass

    save_storage(data)
    print(f"'{site}' updated!\n")


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
        print("  4. Update password")
        print("  5. Delete password")
        print("  6. Exit")

        # .strip() removes extra spaces the user might type
        choice = input("Choose an option (1-6): ").strip()

        # Check what the user picked
        if choice == "1":
            add_password(data)
        elif choice == "2":
            view_password(data)
        elif choice == "3":
            list_sites(data)
        elif choice == "4":
            update_password(data)
        elif choice == "5":
            delete_password(data)
        elif choice == "6":
            print("Goodbye!")
            break  # exit the while loop → program ends
        else:
            # Anything other than 1-6
            print("Invalid option. Try again.\n")


# --- MAIN PROGRAM ---
# This guard means: only run if this file is executed directly
# If another file imports this one, the code below won't run automatically
if __name__ == "__main__":
    if os.path.exists(STORAGE_FILE):
        data = load_storage()
        if verify_master_password(data):
            show_menu(data)  # password correct → show menu
    else:
        data = setup_master_password()
        show_menu(data)  # just created account → show menu
