import ast
from voice_system import speak
from event_class import EventPlanner

# Filename used to store usernames and passwords in plain text.
USER_FILE = "users.txt"

def speak_always(text, voice_settings):
    """
    Always speaks and prints a message based on voice settings.

    Args:
        text (str): Message to output.
        voice_settings (dict): Current TTS settings.

    Returns:
        None
    """
    print(text)
    if voice_settings["enabled"]:
        speak(text, voice_settings)


def speak_input(prompt, voice_settings):
    """
    Speaks a prompt and reads user input from the terminal.

    Args:
        prompt (str): The message to speak and show.
        voice_settings (dict): TTS configuration.

    Returns:
        str: Trimmed input entered by the user.
    """
    if voice_settings["enabled"]:
        speak(prompt, voice_settings)
    return input(prompt)

# ----- Helper Functions for User File Operations -----

def read_user_file():
    """
    Reads and returns all lines from the user file.

    Returns:
        list of str: Lines of the user file. Empty list if not found or error.

    Exceptions:
        - Creates file if not found.
        - Logs warnings if file access fails.
    """
    try:
        with open(USER_FILE, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        speak_always("User file not found. Creating a new one.", {"enabled": True})
        try:
            open(USER_FILE, 'w').close()
        except:
            speak_always("❌ Failed to create user file.", {"enabled": True})
        return []
    except IOError:
        speak_always("❌ Error accessing user file.", {"enabled": True})
        return []

def write_user_file(lines):
    """
    Writes a list of lines to the user file.

    Args:
        lines (list of str): Lines to write.

    Returns:
        None

    Exceptions:
        - Catches and logs I/O errors.
    """
    try:
        with open(USER_FILE, 'w', encoding="UTF-8") as file:
            file.writelines(lines)
    except IOError:
        speak_always("Error saving user data.")

def user_exists(username):
    """
    Checks if a username already exists in the user file.

    Args:
        username (str): Username to check.

    Returns:
        bool: True if username found, else False.
    """
    lines = read_user_file()
    for line in lines:
        stored_username = line.strip().split(":")[0]
        if stored_username == username:
            return True
    return False

def get_user_password(username):
    """
    Retrieves the stored password for a username.

    Args:
        username (str): Username to search for.

    Returns:
        str or None: Password if found, None otherwise.

    Exceptions:
        - Skips and warns on malformed lines.
    """
    lines = read_user_file()
    for line in lines:
        parts = line.strip().split(":")
        if len(parts) != 2:
            speak_always("⚠️ Warning: Corrupted line in user file. Skipping.", {"enabled": True})
            continue

        stored_username, stored_password = parts
        if stored_username == username:
            return stored_password

    return None

def save_user(username, password):
    """
    Adds a new user to the user file.

    Args:
        username (str): New username.
        password (str): Password for the new user.

    Returns:
        None
    """
    lines = read_user_file()
    lines.append(f"{username}:{password}\n")
    write_user_file(lines)

def update_user_password(username, new_password):
    """
    Updates the stored password for a user.

    Args:
        username (str): Existing user.
        new_password (str): New password to store.

    Returns:
        None
    """
    lines = read_user_file()
    updated_lines = []

    for line in lines:
        parts = line.strip().split(":")
        if len(parts) != 2:
            speak_always("⚠️ Warning: Corrupted line in user file. Skipping.", {"enabled": True})
            continue

        stored_username, _ = parts
        if stored_username == username:
            updated_lines.append(f"{username}:{new_password}\n")
        else:
            updated_lines.append(line)

    write_user_file(updated_lines)

def remove_user(username):
    """
    Deletes a user and their credentials from the file.

    Args:
        username (str): Username to delete.

    Returns:
        None
    """
    lines = read_user_file()
    updated_lines = []

    for line in lines:
        parts = line.strip().split(":")
        if len(parts) != 2:
            speak_always("⚠️ Warning: Corrupted line in user file. Skipping.", {"enabled": True})
            continue

        stored_username, _ = parts
        if stored_username != username:
            updated_lines.append(line)

    write_user_file(updated_lines)

# ----- Account Management Functions -----

def create_account(voice_settings):
    """
    Handles new account creation: asks for username and password.

    Args:
        voice_settings (dict): TTS settings.

    Returns:
        str or None: Username if successful, None on error.

    Logic:
        - Verifies unique username.
        - Saves to file if successful.
    """
    username = speak_input("Enter username: ", voice_settings).strip()
    if not username:
        speak_always("❌ Username cannot be empty.", voice_settings)
        return None
    
    if user_exists(username):
        speak_always("❌ Username already exists.", voice_settings)
        return None

    password = speak_input("Enter password: ", voice_settings).strip()
    if not password:
        speak_always("❌ Password cannot be empty.", voice_settings)
        return None

    save_user(username, password)
    speak_always("✅ Account created successfully!", voice_settings)
    speak_always("Auto logging you in.", voice_settings)
    return username

def login(voice_settings):
    """
    Handles login flow including optional password reset.

    Args:
        voice_settings (dict): TTS settings.

    Returns:
        str or None: Logged in username or None on failure.

    Logic:
        - Validates credentials.
        - Supports fallback to password reset.
    """
    username = speak_input("Enter username: ", voice_settings).strip()
    if not user_exists(username):
        speak_always("Invalid username.", voice_settings)
        return None

    password = speak_input("Enter password: ", voice_settings).strip()
    stored_password = get_user_password(username)

    if stored_password is None:
        speak_always("Could not retrieve password.", voice_settings)
        choice = speak_input("Would you like to reset your password? (y/n): ", voice_settings).strip().lower()
        if choice in ["y", "yes"]:
            success = reset_password(username, voice_settings)
            if success:
                speak_always("You can now log in with your new password.", voice_settings)
            return None
        else:
            speak_always("Login cancelled.", voice_settings)
            return None

    if stored_password == password:
        speak_always("Login successful!", voice_settings)
        return username
    else:
        speak_always("Invalid password.", voice_settings)
        return None

def reset_password(username, voice_settings):
    """
    Resets password for a user after confirmation.

    Args:
        username (str): Existing username.
        voice_settings (dict): TTS settings.

    Returns:
        bool: True if reset successful, False otherwise.

    Logic:
        - Checks if user exists.
        - Prompts for new password.
    """
    speak_always("Attempting password recovery...", voice_settings)

    if not user_exists(username):
        speak_always("Username not found.", voice_settings)
        return False

    confirm = speak_input("User exists, but password is not retrievable. Reset password? (y/n): ", voice_settings).strip().lower()
    if confirm not in ["y", "yes"]:
        speak_always("Password reset cancelled.", voice_settings)
        return False

    new_password = speak_input("Enter new password: ", voice_settings).strip()
    if not new_password:
        speak_always("New password cannot be empty.", voice_settings)
        return False

    update_user_password(username, new_password)
    speak_always("Password reset successfully.", voice_settings)
    return True

def change_password(username, voice_settings):
    """
    Changes a user’s password after verifying the old one.

    Args:
        username (str): User to update.
        voice_settings (dict): TTS settings.

    Returns:
        bool: True if changed successfully, False otherwise.
    """
    if not user_exists(username):
        speak_always("User not found.", voice_settings)
        return False

    old_password = speak_input("Enter your old password: ", voice_settings).strip()
    if not old_password:
        speak_always("Old password cannot be empty.", voice_settings)
        return False

    stored_password = get_user_password(username)
    if stored_password is None:
        speak_always("Could not verify old password.", voice_settings)
        return reset_password(username, voice_settings)

    if stored_password != old_password:
        speak_always("Invalid old password.", voice_settings)
        return False

    new_password = speak_input("Enter your new password: ", voice_settings).strip()
    if not new_password:
        speak_always("New password cannot be empty.", voice_settings)
        return False

    update_user_password(username, new_password)
    speak_always("Password changed successfully!", voice_settings)
    return True

def delete_account(username, voice_settings):
    """
    Deletes a user account after verifying the password.

    Args:
        username (str): Username to delete.
        voice_settings (dict): TTS settings.

    Returns:
        bool: True if deleted, False if cancelled or failed.
    """
    if not user_exists(username):
        speak_always("User not found.", voice_settings)
        return False

    password = speak_input("Enter your password to confirm deletion: ", voice_settings).strip()
    if not password:
        speak_always("Password cannot be empty. Account not deleted.", voice_settings)
        return False

    stored_password = get_user_password(username)
    if stored_password is None:
        speak_always("Could not verify password.", voice_settings)
        return False

    if stored_password != password:
        speak_always("Invalid password. Account not deleted.", voice_settings)
        return False

    remove_user(username)
    speak_always("Account deleted successfully!", voice_settings)
    return True

def logout(voice_settings):
    """
    Handles logging out with spoken feedback.

    Args:
        voice_settings (dict): TTS config.

    Returns:
        None
    """
    speak_always("Logged out successfully!", voice_settings)
    return None

# ----- Task Management -----

def load_tasks(username, voice_settings):
    """
    Loads tasks from disk and reconstructs an EventPlanner instance.

    Args:
        username (str): Username whose tasks to load.
        voice_settings (dict): Voice feedback configuration.

    Returns:
        EventPlanner: Planner instance populated with events/tasks.

    Exceptions:
        - Handles missing or malformed data gracefully.
    """
    planner = EventPlanner(voice_settings)  # Initializes with empty events by default
    tasks_file = f"{username}_tasks.txt"

    try:
        with open(tasks_file, 'r') as file:
            lines = file.readlines()

        current_event = None
        reading_archived = False

        for line in lines:
            line = line.strip()
            try:
                if line.startswith("=== Event:"):
                    current_event = line.replace("=== Event:", "").replace("===", "").strip()
                    planner.events[current_event] = {
                        "date": "", "notes": "", "tags": [], "tasks": [],
                        "pinned": False, "starred": False, "reminder_days": 0,
                        "start_time": "", "end_time": "", "category": "",
                        "priority": "Medium", "budget": 0,
                        "recurrence": {"enabled": False},
                        "archived_tasks": []
                    }
                    reading_archived = False

                elif line.startswith("Date:"):
                    planner.events[current_event]["date"] = line.split(":", 1)[1].strip()

                elif line.startswith("Notes:"):
                    planner.events[current_event]["notes"] = line.split(":", 1)[1].strip()

                elif line.startswith("Tags:"):
                    tag_line = line.split(":", 1)[1].strip()
                    planner.events[current_event]["tags"] = [tag.strip() for tag in tag_line.split(",") if tag.strip()]

                elif line.startswith("Pinned:"):
                    planner.events[current_event]["pinned"] = line.split(":", 1)[1].strip() == "True"

                elif line.startswith("Starred:"):
                    planner.events[current_event]["starred"] = line.split(":", 1)[1].strip() == "True"

                elif line.startswith("Reminder Days:"):
                    try:
                        planner.events[current_event]["reminder_days"] = int(line.split(":", 1)[1].strip())
                    except ValueError:
                        planner.events[current_event]["reminder_days"] = 0

                elif line.startswith("StartTime:"):
                    planner.events[current_event]["start_time"] = line.split(":", 1)[1].strip()

                elif line.startswith("EndTime:"):
                    planner.events[current_event]["end_time"] = line.split(":", 1)[1].strip()

                elif line.startswith("Category:"):
                    planner.events[current_event]["category"] = line.split(":", 1)[1].strip()

                elif line.startswith("Priority:"):
                    planner.events[current_event]["priority"] = line.split(":", 1)[1].strip()

                elif line.startswith("Budget:"):
                    try:
                        planner.events[current_event]["budget"] = float(line.split(":", 1)[1].strip())
                    except ValueError:
                        planner.events[current_event]["budget"] = 0

                elif line.startswith("Recurrence:"):
                    try:
                        rec = line.split(":", 1)[1].strip()
                        planner.events[current_event]["recurrence"] = ast.literal_eval(rec)
                    except (ValueError, SyntaxError):
                        planner.events[current_event]["recurrence"] = {"enabled": False}

                elif line.startswith("ArchivedTasks:"):
                    reading_archived = True

                elif line.startswith("Tasks:"):
                    reading_archived = False

                elif line.startswith("-") and "||" in line:
                    parts = line.strip().split("||")
                    try:
                        status = parts[0].split(":")[1].strip()
                        task = parts[1].strip()
                        task_obj = {"task": task, "status": status}
                        if reading_archived:
                            planner.events[current_event]["archived_tasks"].append(task_obj)
                        else:
                            planner.events[current_event]["tasks"].append(task_obj)
                    except Exception as e:
                        speak_always(f"⚠️ Failed to parse task line: {line}", voice_settings)
                        continue

            except Exception as e:
                speak_always(f"⚠️ Error parsing line: {line}. Skipping.", voice_settings)
                continue

        return planner

    except FileNotFoundError:
        speak_always(f"Task file for {username} not found.", voice_settings)
        return planner  # Return an empty planner instead of None

    except IOError:
        speak_always(f"Error loading task file for {username}.", voice_settings)
        return planner  # Return an empty planner instead of None

def save_tasks(username, events, voice_settings):
    """
    Saves all events and tasks to a user-specific file.

    Args:
        username (str): User whose data is being saved.
        events (dict): Dictionary of all user events.
        voice_settings (dict): Voice settings.

    Returns:
        None

    Exceptions:
        - Logs failure to write.
    """
    tasks_file = f"{username}_tasks.txt"
    try:
        with open(tasks_file, 'w', encoding="UTF-8") as file:
            for event_name, event_data in events.items():
                file.write(f"=== Event: {event_name}\n")
                file.write(f"Date: {event_data['date']}\n")
                file.write(f"Notes: {event_data['notes']}\n")
                file.write(f"Tags: {', '.join(event_data['tags'])}\n")
                file.write(f"Pinned: {event_data['pinned']}\n")
                file.write(f"Starred: {event_data['starred']}\n")
                file.write(f"Reminder: {event_data['reminder_days']}\n")
                file.write(f"StartTime: {event_data['start_time']}\n")
                file.write(f"EndTime: {event_data['end_time']}\n")
                file.write(f"Category: {event_data['category']}\n")
                file.write(f"Priority: {event_data['priority']}\n")
                file.write(f"Budget: {event_data['budget']}\n")
                file.write(f"Recurrence: {str(event_data['recurrence'])}\n")
                file.write(f"ArchivedTasks:\n")
                for task in event_data['archived_tasks']:
                    file.write(f"- Task: {task['task']} || Status: {task['status']}\n")
                file.write(f"Tasks:\n")
                for task in event_data['tasks']:
                    file.write(f"- Task: {task['task']} || Status: {task['status']}\n")
        speak_always(f"Tasks saved successfully for {username}.", voice_settings)
    except IOError:
        speak_always(f"Error saving task file for {username}.", voice_settings)
