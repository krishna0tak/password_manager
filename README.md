# Password Manager

A command-line password manager built in Python. Stores credentials locally and protected by a master password.

## Features

- Master password with SHA-256 hashing (never stored in plain text)
- Add, view, list, update, and delete passwords
- Auto-generate strong random passwords
- Password input is hidden as you type (using `getpass`)
- All data saved locally in `storage.json`

## Usage

```
py main.py
```

**First run:** Create a master password  
**Subsequent runs:** Enter master password to unlock (3 attempts max)

## Menu Options

| Option | Description |
|--------|-------------|
| 1 | Add a new password |
| 2 | View a password |
| 3 | List all saved sites |
| 4 | Update an existing password |
| 5 | Delete a password |
| 6 | Exit |

## Security Notes

- `storage.json` is **gitignored** — your passwords are never pushed to GitHub
- Passwords are stored in plain text inside `storage.json` — do not share that file
- The master password is hashed with SHA-256 before saving
