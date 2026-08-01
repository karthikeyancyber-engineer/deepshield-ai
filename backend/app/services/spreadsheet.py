import csv
import os
from datetime import datetime


SPREADSHEET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
SPREADSHEET_PATH = os.path.join(SPREADSHEET_DIR, "user_logins.csv")


def ensure_spreadsheet():
    """Create the CSV file with headers if it doesn't exist."""
    os.makedirs(SPREADSHEET_DIR, exist_ok=True)
    if not os.path.exists(SPREADSHEET_PATH):
        with open(SPREADSHEET_PATH, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp",
                "Email",
                "Password",
                "Full Name",
                "Role",
                "User ID",
            ])


def _email_exists(email: str) -> bool:
    """Check if email already exists in the spreadsheet."""
    if not os.path.exists(SPREADSHEET_PATH):
        return False
    with open(SPREADSHEET_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Email", "").lower() == email.lower():
                return True
    return False


def save_login_to_spreadsheet(
    email: str,
    password: str,
    full_name: str,
    role: str,
    user_id: str,
):
    """Save login details only once per email. Skips if email already exists."""
    ensure_spreadsheet()
    if _email_exists(email):
        return
    with open(SPREADSHEET_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            email,
            password,
            full_name,
            role,
            user_id,
        ])
