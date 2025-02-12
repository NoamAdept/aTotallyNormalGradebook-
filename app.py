import curses
import os
import random
import string
# =============================================================================
# Configuration & Global Data
# =============================================================================
SECRET_FILE_PATH = "secret_number.txt"
ADMIN_USERNAME = "admin"


# Starting DEFCON level (displayed in the UI)
DEFCON_LEVEL = 4

# Global variable to track the last complaint submitted (vulnerable to format string exploit)
last_complaint = "No complaints submitted."

# Global variable used by the leak function
leaked_digits = 0

# Sample course list for the gradebook UI
courses = [
    {"course": "BIOLOGY 2", "grade": "F"},
    {"course": "ENGLISH 11B", "grade": "A"},
    {"course": "WORLD HISTORY 11B", "grade": "B"},
    {"course": "GEOMETRY 2", "grade": "D"},
]

# Sample student grade database (displayed in admin view)
student_grades = {
    "Alice": {"BIOLOGY 2": "A", "ENGLISH 11B": "B", "WORLD HISTORY 11B": "A", "GEOMETRY 2": "B"},
    "Bob": {"BIOLOGY 2": "C", "ENGLISH 11B": "A", "WORLD HISTORY 11B": "B", "GEOMETRY 2": "C"},
    "Charlie": {"BIOLOGY 2": "B", "ENGLISH 11B": "C", "WORLD HISTORY 11B": "A", "GEOMETRY 2": "A"},
}

# =============================================================================
# Utility Functions
# =============================================================================

ADMIN_PASSWORD = "".join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=12))

# Generate a random secret phone number
SECRET_PHONE_NUMBER = f"555-{random.randint(1000, 9999)}"

def save_secret_number():
    """Save the secret number to a file."""
    with open(SECRET_FILE_PATH, "w") as f:
        f.write(SECRET_PHONE_NUMBER)

save_secret_number()        
def get_secret_number():
    """Read and return the secret phone number from a file."""
    try:
        with open(SECRET_FILE_PATH, "r") as f:
            return f.read().strip()
    except Exception:
        return "UNKNOWN"

def leak_number():
    """
    Leak the next digit of the secret number.
    
    (For demonstration purposes only; this prints directly to stdout.)
    """
    global leaked_digits
    secret_number = get_secret_number()
    # Start leaking from index 3 (as in the original code) until the end
    if leaked_digits < len(secret_number) - 3:
        leaked_digit = secret_number[3 + leaked_digits]
        leaked_digits += 1
        print(f"💀 Leaked digit: {leaked_digit}")
    else:
        print("🚫 No more digits to leak!")

def execute_shellcode():
    """Simulate shellcode execution by opening a shell."""
    os.system("/bin/sh")  # DANGEROUS: This will open a shell if executed

# =============================================================================
# Core Application Functions
# =============================================================================
def dial_number(stdscr):
    """
    Simulate dialing a phone number.
    
    If the input is too long (simulating a buffer overflow), the input is passed
    to eval()—a dangerous vulnerability that allows arbitrary Python code execution.
    A maximum of 8 exploit attempts is allowed before locking the connection.
    """
    correct_number = get_secret_number()
    max_exploit_attempts = 8
    exploit_attempts = 0

    while exploit_attempts < max_exploit_attempts:
        stdscr.clear()
        stdscr.addstr(2, 5, "📞 WarGames Dial-Up System", curses.A_BOLD)
        stdscr.addstr(3, 5, "---------------------------------")
        attempts_left = max_exploit_attempts - exploit_attempts
        stdscr.addstr(5, 5, f"Enter a phone number to connect (Attempts left: {attempts_left})")
        stdscr.addstr(7, 5, "Dial: 555-____ ")
        stdscr.refresh()

        curses.echo()
        input_number = stdscr.getstr(7, 14, 50).decode("utf-8")
        curses.noecho()

        # If input length is too long, trigger the eval() vulnerability
        if len(input_number) > 12:
            stdscr.clear()
            stdscr.addstr(9, 5, "📡 Buffer Overflow Triggered! Deducting an attempt...", curses.A_BOLD)
            stdscr.refresh()
            curses.napms(1000)  # brief delay

            try:
                # DANGEROUS: Directly evaluate user input!
                result = eval(input_number)
                stdscr.addstr(11, 5, f"✅ Eval result: {result}", curses.A_BOLD)
            except Exception as e:
                stdscr.addstr(11, 5, f"⚠️ Eval error: {str(e)}", curses.A_BOLD)

            stdscr.refresh()
            stdscr.getch()
            exploit_attempts += 1

            if exploit_attempts >= max_exploit_attempts:
                stdscr.clear()
                stdscr.addstr(5, 5, "❌ Too many failed exploit attempts! Connection locked.", curses.A_BOLD)
                stdscr.refresh()
                stdscr.getch()
                exit(1)
            continue

        # Normal execution: build full phone number and compare it
        full_number = f"555-{input_number}"
        if full_number == correct_number:
            stdscr.addstr(9, 5, "✅ Connected to: Gradebook System!", curses.A_BOLD)
            stdscr.refresh()
            stdscr.getch()
            return
        else:
            stdscr.addstr(9, 5, "🚫 No Response. Try another number...", curses.A_BOLD)
            stdscr.refresh()
            stdscr.getch()

def display_gradebook(stdscr):
    """Display the gradebook UI with course titles and grades."""
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdscr.bkgd(" ", curses.color_pair(1))
    stdscr.clear()
    stdscr.addstr(1, 5, f"DEFCON LEVEL: {DEFCON_LEVEL}", curses.A_BOLD | curses.A_BLINK)
    stdscr.addstr(3, 5, "COURSE TITLE", curses.A_BOLD)
    stdscr.addstr(3, 30, "GRADE", curses.A_BOLD)
    stdscr.addstr(4, 5, "-----------------------------")
    for i, course in enumerate(courses):
        stdscr.addstr(6 + (i * 2), 5, course["course"])
        stdscr.addstr(6 + (i * 2), 30, course["grade"])
    stdscr.addstr(16, 5, "Press 'c' to submit a grade complaint, 'l' to login, or 'q' to quit.", curses.A_BOLD)
    stdscr.refresh()

def submit_complaint(stdscr):
    """
    Allow a user to submit a grade complaint.
    
    This function intentionally uses unsafe string formatting (a format string
    vulnerability) when printing the complaint summary.
    """
    global last_complaint
    stdscr.clear()
    stdscr.addstr(5, 5, "Submit a Grade Complaint Form:", curses.A_BOLD)
    stdscr.addstr(7, 5, "Enter your complaint below and press Enter:", curses.A_DIM)
    stdscr.refresh()

    curses.echo()
    complaint_text = stdscr.getstr(9, 5, 100).decode("utf-8")
    curses.noecho()

    # Vulnerable storage of user input
    last_complaint = complaint_text
    stdscr.clear()
    stdscr.addstr(5, 5, "Complaint Submitted!", curses.A_BOLD)

    try:
        summary = last_complaint % globals()
    except Exception as e:
        summary = f"Error in formatting: {e}"
    stdscr.addstr(7, 5, "Complaint Summary: " + summary, curses.A_BOLD)
    stdscr.addstr(10, 5, "Press any key to return to the gradebook.")
    stdscr.refresh()
    stdscr.getch()

def login_admin(stdscr):
    """Prompt the user for admin credentials and, on success, display the admin dashboard."""
    global DEFCON_LEVEL
    stdscr.clear()
    stdscr.addstr(5, 5, "Admin Login:", curses.A_BOLD)
    stdscr.addstr(7, 5, "Enter username: ", curses.A_DIM)
    stdscr.refresh()

    curses.echo()
    username_attempt = stdscr.getstr(7, 22, 50).decode("utf-8")
    curses.noecho()

    stdscr.addstr(9, 5, "Enter password: ", curses.A_DIM)
    stdscr.refresh()

    curses.echo()
    password_attempt = stdscr.getstr(9, 22, 50).decode("utf-8")
    curses.noecho()

    if username_attempt == ADMIN_USERNAME and password_attempt == ADMIN_PASSWORD:
        DEFCON_LEVEL = 4  # Adjust DEFCON level upon successful login
        show_admin_dashboard(stdscr)
    else:
        stdscr.addstr(11, 5, "Access Denied! Incorrect username or password.", curses.A_BOLD)
        stdscr.refresh()
        stdscr.getch()

def show_admin_dashboard(stdscr):
    """
    Display the admin dashboard with options to view the student database,
    leak a secret digit, or logout.
    """
    stdscr.clear()
    stdscr.addstr(2, 5, "ADMIN ACCESS GRANTED!", curses.A_BOLD)
    stdscr.addstr(3, 5, "------------------------------")
    stdscr.addstr(5, 5, f"DEFCON LEVEL: {DEFCON_LEVEL}", curses.A_BOLD | curses.A_BLINK)
    stdscr.addstr(7, 5, "Press 's' to view student grades, 'k' to leak a secret digit, or 'q' to logout.", curses.A_BOLD)
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord("s"):
            show_student_database(stdscr)
        elif key == ord("k"):
            stdscr.clear()
            # Instead of printing to stdout, display the leaked digit on screen
            secret_number = get_secret_number()
            global leaked_digits
            if leaked_digits < len(secret_number) - 3:
                leaked_digit = secret_number[3 + leaked_digits]
                leaked_digits += 1
                stdscr.addstr(5, 5, f"💀 Leaked digit: {leaked_digit}", curses.A_BOLD)
            else:
                stdscr.addstr(5, 5, "🚫 No more digits to leak!", curses.A_BOLD)
            stdscr.addstr(7, 5, "Press any key to return to the admin panel.")
            stdscr.refresh()
            stdscr.getch()
            stdscr.clear()
            show_admin_dashboard(stdscr)
            return
        elif key == ord("q"):
            break

def show_student_database(stdscr):
    """Display the student grades database."""
    stdscr.clear()
    stdscr.addstr(2, 5, "STUDENT GRADES DATABASE", curses.A_BOLD)
    stdscr.addstr(3, 5, "----------------------------------")
    row = 5
    for student, grades in student_grades.items():
        stdscr.addstr(row, 5, f"Student: {student}", curses.A_BOLD)
        row += 1
        for course, grade in grades.items():
            stdscr.addstr(row, 7, f"{course}: {grade}")
            row += 1
        row += 1
        stdscr.addstr(4, 5, "🏆 CONGRATULATIONS! YOU WIN! SHALL WE PLAY A GAME?🏆", curses.A_BOLD | curses.A_BLINK)
    stdscr.addstr(row, 5, "Press any key to return to the admin panel.")
    stdscr.refresh()
    stdscr.getch()

# =============================================================================
# Main Application Loop
# =============================================================================
def main(stdscr):
    curses.curs_set(0)
    # Require dialing before accessing the gradebook
    dial_number(stdscr)

    while True:
        display_gradebook(stdscr)
        key = stdscr.getch()

        if key == ord("q"):
            break
        elif key == ord("c"):
            submit_complaint(stdscr)
        elif key == ord("l"):
            login_admin(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)

