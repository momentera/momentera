import datetime
from event_class import EventPlanner
from login_system import create_account, login, load_tasks, save_tasks, delete_account, change_password, user_exists, get_user_password, update_user_password
from voice_system import speak, load_voice_settings, save_voice_settings, configure_voice_settings

# 🌟 Demo event name constant
DEMO_EVENT = "birthday party"

def speak_menu(lines, settings):
    """
    Speaks a list of lines using the current voice settings.

    Args:
        lines (list of str): Messages to speak one by one.
        settings (dict): Voice configuration.

    Returns:
        None

    Logic:
        - Iterates through lines and speaks each one individually.
    """
    for line in lines:
        speak(line, settings)

def speak_input(prompt, settings):
    """
    Speaks a prompt and returns the user input.

    Args:
        prompt (str): The question or instruction to the user.
        settings (dict): Voice settings for text-to-speech.

    Returns:
        str: The user's input, stripped of leading/trailing spaces.
             Returns empty string if input is cancelled by user (Ctrl+D/Ctrl+C).

    Exceptions:
        - Catches EOFError and KeyboardInterrupt gracefully and speaks a cancellation message.
    """
    speak(prompt, settings)
    try:
        user_input = input(prompt)
    except (EOFError, KeyboardInterrupt):
                # Gracefully handle when user cancels input
        speak("⚠️ Input cancelled.", settings)
        return ""
    return user_input.strip()

def choose_event(planner):
    """
    Lets the user pick an event from existing ones.

    Args:
        planner (EventPlanner): The planner object containing events.

    Returns:
        str or None: The name of the selected event, or None if cancelled.

    Logic:
        - Lists all available events.
        - Keeps prompting until user types a valid event name or 'exit'.
    """
    if not planner.events:
        speak("❌ No events found. Please create one first.", planner.voice_settings)
        return None

    speak("📅 Available events:", planner.voice_settings)
    for name in planner.events:
        speak("- " + name, planner.voice_settings)

    while True:
        selected = speak_input("Enter event name: ", planner.voice_settings).strip().lower()
        if selected in planner.events:
            return selected
        # Retry or exit if invalid
        speak("❌ Event not found. Try again or type 'exit' to cancel.", planner.voice_settings)
        if selected == "exit":
            return None

def check_user_file():
    """
    Checks the integrity of the 'users.txt' file and ensures it's created if missing.

    Args:
        None

    Returns:
        None

    Logic:
        - If file is missing, creates it and speaks info message.
        - Warns if the file is empty or has corrupted lines.
    """
    voice_settings = {"enabled": True}
    try:
        with open("users.txt", "r") as file:
            lines = file.readlines()
            if len(lines) == 0:
                speak("⚠️ No users found. You need to create an account first.", voice_settings)
            else:
                for line in lines:
                    if ":" not in line:
                        # Warn about malformed user line
                        speak("⚠️ Warning: A line in users.txt might be broken.", voice_settings)
                        break
    except FileNotFoundError:
        # Create file if missing
        speak("🆕 users.txt file not found. It will be created when you register.", voice_settings)
        open("users.txt", "w").close()
    except:
        speak("❌ Failed to read user file.", voice_settings)

def welcome_and_choose_voice():
    """
    Greets the user and prompts them to enable or disable speech mode.

    Args:
        None

    Returns:
        dict: Initial voice settings dictionary with keys:
              enabled (bool), rate (int), volume (float), voice_index (int)

    Logic:
        - Shows full logo.
        - Asks if user wants speech mode.
        - Returns default voice settings with toggled enabled flag.
    """
    temp_voice_settings = {"enabled": True}
    show_logo_full(temp_voice_settings)
    ans = speak_input("Would you like to enable speech mode? (y/n): ", temp_voice_settings).strip().lower()
    # Convert answer to boolean flag
    voice_enabled = ans in ["y", "yes"]
    return {
        "enabled": voice_enabled,
        "rate": 150,
        "volume": 1.0,
        "voice_index": 0
    }

def show_logo_short(voice_settings=None):
    """
    Displays and speaks the short Momentera logo.

    Args:
        voice_settings (dict, optional): TTS settings.

    Returns:
        None
    """
    line = "\n📘 Momentera • Plan your moments"
    speak(line, voice_settings)

def show_logo_full(voice_settings=None):
    """
    Displays and speaks the full Momentera logo with tagline.

    Args:
        voice_settings (dict, optional): TTS configuration.

    Returns:
        None
    """
    logo = """
    📘 Momentera 
    Your event planning companion 
    Where moments become milestones. 
    """
    speak(logo, voice_settings)

def load_demo_data(planner):
    """
    Loads a predefined sample event for users to explore features quickly.

    Args:
        planner (EventPlanner): Main planner object.

    Returns:
        None

    Logic:
        - Creates a sample event with tasks, budget, reminder, and decorations.
        - Allows users to test the app without creating their own event first.
    """
    planner.create_event(DEMO_EVENT, "2024-08-15", "Celebrate Sarah's 30th!")
    planner.set_event_priority(DEMO_EVENT, "High")
    planner.set_event_category(DEMO_EVENT, "Personal")
    planner.set_or_edit_duration(DEMO_EVENT, "19:00", "23:00")
    planner.add_tasks(DEMO_EVENT, [
        {"task": "Book venue", "status": "Completed"},
        {"task": "Send invitations", "status": "Pending"},
        {"task": "Order cake", "status": "Pending"}
    ])
    planner.set_event_budget(DEMO_EVENT, 1500.00)
    planner.toggle_star_event(DEMO_EVENT)
    planner.set_reminder(DEMO_EVENT, 2)
    speak("✅ Demo event loaded! Explore the features freely.", planner.voice_settings)

def help_and_tour(planner):
    """
    Provides an introductory tour of Momentera's features with optional demo loading.

    Args:
        planner (EventPlanner): Main planner instance.

    Returns:
        None

    Logic:
        - Walks through main features via voice.
        - Optionally loads a demo event if user agrees.
    """
    info = [
        "✨ Welcome to Momentera!",
        "Here's a quick tour:",
        "🔹 'Create Event' to add events with names, dates, and notes.",
        "🔹 'View Event' to see all details of an event.",
        "🔹 'Edit Event' to change any event details like name, date, notes, tags, budget, etc.",
        "🔹 'Delete Event' to remove an event.",
        "🔹 Use 'Task Management' to add, view, complete, and delete tasks.",
        "🔹 Set 'Priority' and 'Category' for better organization.",
        "🔹 Manage 'Tags' to categorize events.",
        "🔹 Set 'Budget' for events and track expenses.",
        "🔹 Use 'Reminders' to get notified before events.",
        "🔹 'Search and Sort' events by various criteria.",
        "🔹 'Archive' old events to keep your list clean.",
        "🧪 Tip: Load demo data to see how it works!",
        "💬 Got ideas, feedback, or just want to say hi?",
        "We’d love to hear from you! Drop us a message at: momenteraconnect@gmail.com"
    ]
    speak_menu(info, planner.voice_settings)
    opt = speak_input("Would you like to load a sample event to explore? (y/n): ", planner.voice_settings)
    if opt.lower() == "y":
        load_demo_data(planner)

def about(voice_settings):
    """
    Displays and speaks the 'About Momentera' credits and creator details.

    Args:
        voice_settings (dict): TTS settings.

    Returns:
        None
    """
    lines = [
        "About Momentera",
        "Momentera is your calm, cozy event planning companion.",
        "Organize events, tasks, budgets, and reminders.",
        "Built with care to help you turn moments into milestones.",
        "Created by: Vivek, Prathmesh, Kushal, & Ishika"
    ]
    speak_menu(lines, voice_settings)

# --- Event Management Menu ---
def event_management_menu(planner, demo_mode):
    """
    Provides event-related actions like creating, editing, tagging, reminders, archiving, etc.

    Args:
        planner (EventPlanner): The planner instance.
        demo_mode (bool): If True, uses a preset demo event instead of user input.

    Returns:
        None

    Logic:
        - Includes sub-menus for core actions, preferences (tags, priority), and timeline/reminders.
        - Handles invalid input with voice feedback.
    """
    show_logo_short(planner.voice_settings)
    while True:
        menu_primary = [
            "\n🗓️ Event Central",
            "1. Core Event Actions",
            "2. Event Organization & Preferences",
            "3. Event Timeline & Reminders",
            "0. Back to Main Menu",
        ]
        speak_menu(menu_primary, planner.voice_settings)
        choice = speak_input("Choose an option: ", planner.voice_settings)

        if choice == "1":
            menu_core = [
                "\n➡️ Core Event Actions",
                "1. Create New Event",
                "2. View All Events",
                "3. View Event Details",
                "4. Modify Existing Event",
                "5. Remove Event",
                "6. Manage Archive",
                "0. Back to Event Central",
            ]
            speak_menu(menu_core, planner.voice_settings)
            choice_core = speak_input("Choose an option: ", planner.voice_settings)
            if choice_core == "1": planner.create_event()
            elif choice_core == "2": planner.view_all_events()
            elif choice_core == "3": planner.view_event(DEMO_EVENT if demo_mode else None)
            elif choice_core == "4": planner.edit_event(DEMO_EVENT if demo_mode else None)
            elif choice_core == "5": planner.delete_event(DEMO_EVENT if demo_mode else None)
            elif choice_core == "6": planner.manage_event_archive()
            elif choice_core == "0": continue
            else: speak("❌ Invalid choice.", planner.voice_settings)

        elif choice == "2":
            menu_org = [
                "\n✨ Event Organization & Preferences",
                "1. Set Event Priority",
                "2. Assign Event Category",
                "3. Manage Event Tags",
                "4. Mark as Important (Pin)",
                "5. Mark as Favorite (Star)",
                "0. Back to Event Central",
            ]
            speak_menu(menu_org, planner.voice_settings)
            choice_org = speak_input("Choose an option: ", planner.voice_settings)
            if choice_org == "1": planner.set_event_priority(DEMO_EVENT if demo_mode else None)
            elif choice_org == "2": planner.set_event_category(DEMO_EVENT if demo_mode else None)
            elif choice_org == "3":
                menu_tags = [
                    "\n🏷️ Event Tag Management",
                    "1. Add Tag to Event",
                    "2. Remove Tag from Event",
                    "0. Back to Event Organization & Preferences"
                ]
                speak_menu(menu_tags, planner.voice_settings)
                choice_tags = speak_input("Choose an option: ", planner.voice_settings)
                if choice_tags == "1": planner.add_tag(DEMO_EVENT if demo_mode else None)
                elif choice_tags == "2": planner.remove_tag(DEMO_EVENT if demo_mode else None)
                elif choice_tags == "0": continue
                else: speak("❌ Invalid choice.", planner.voice_settings)
            elif choice_org == "4": planner.toggle_pin_event(DEMO_EVENT if demo_mode else None)
            elif choice_org == "5": planner.toggle_star_event(DEMO_EVENT if demo_mode else None)
            elif choice_org == "0": continue
            else: speak("❌ Invalid choice.", planner.voice_settings)

        elif choice == "3":
            menu_timeline = [
                "\n⏰ Event Timeline & Reminders",
                "1. Set/Edit Event Duration",
                "2. Schedule Reminder",
                "3. View Upcoming Events",
                "4. Countdown to Event",
                "0. Back to Event Central",
            ]
            speak_menu(menu_timeline, planner.voice_settings)
            choice_timeline = speak_input("Choose an option: ", planner.voice_settings)
            if choice_timeline == "1": planner.set_or_edit_duration(DEMO_EVENT if demo_mode else None)
            elif choice_timeline == "2": planner.set_reminder(DEMO_EVENT if demo_mode else None)
            elif choice_timeline == "3": planner.upcoming_events()
            elif choice_timeline == "4": planner.countdown_to_event(DEMO_EVENT if demo_mode else None)
            elif choice_timeline == "0": continue
            else: speak("❌ Invalid choice.", planner.voice_settings)

        elif choice == "0":
            break
        else:
            speak("❌ Invalid choice.", planner.voice_settings)

# --- Task Management Menu ---
def task_management_menu(planner, demo_mode):
    """
    Manages tasks within an event — creation, editing, viewing, sorting, and workflow.

    Args:
        planner (EventPlanner): The planner object managing data.
        demo_mode (bool): Uses a demo event if set to True.

    Returns:
        None

    Logic:
        - Contains 2 sections: Core Operations (add/edit/delete) and Workflow (status, deadlines, archive).
    """
    show_logo_short(planner.voice_settings)
    while True:
        menu_primary = [
            "\n✔️ Task Manager",
            "1. Core Task Operations",
            "2. Task Workflow & Analysis",
            "0. Back to Main Menu",
        ]
        speak_menu(menu_primary, planner.voice_settings)
        choice = speak_input("Choose an option: ", planner.voice_settings)

        if choice == "1":
            menu_core = [
                "\n➡️ Core Task Operations",
                "1. Add New Tasks",
                "2. View Current Tasks",
                "3. Edit Task Details",
                "4. Delete Task",
                "0. Back to Task Manager",
            ]
            speak_menu(menu_core, planner.voice_settings)
            choice_core = speak_input("Choose an option: ", planner.voice_settings)
            if choice_core == "1": planner.add_tasks(DEMO_EVENT if demo_mode else None)
            elif choice_core == "2": planner.view_tasks(DEMO_EVENT if demo_mode else None)
            elif choice_core == "3": planner.edit_task(DEMO_EVENT if demo_mode else None)
            elif choice_core == "4": planner.delete_task(DEMO_EVENT if demo_mode else None)
            elif choice_core == "0": continue
            else: speak("❌ Invalid choice.", planner.voice_settings)

        elif choice == "2":
            menu_workflow = [
                "\n⚙️ Task Workflow & Analysis",
                "1. Update Task Progress",
                "2. Archive Task",
                "3. View Archived Tasks",
                "4. Restore Archived Task",
                "5. View Pending Tasks (Next 3 Days)",
                "6. Sort Tasks",
                "0. Back to Task Manager",
            ]
            speak_menu(menu_workflow, planner.voice_settings)
            choice_workflow = speak_input("Choose an option: ", planner.voice_settings)
            if choice_workflow == "1": planner.mark_task_progress(DEMO_EVENT if demo_mode else None)
            elif choice_workflow == "2": planner.archive_task(DEMO_EVENT if demo_mode else None)
            elif choice_workflow == "3": planner.view_archived_tasks(DEMO_EVENT if demo_mode else None)
            elif choice_workflow == "4": planner.restore_archived_task(DEMO_EVENT if demo_mode else None)
            elif choice_workflow == "5": planner.check_task_deadlines()
            elif choice_workflow == "6": planner.sort_tasks(DEMO_EVENT if demo_mode else None)
            elif choice_workflow == "0": continue
            else: speak("❌ Invalid choice.", planner.voice_settings)

        elif choice == "0":
            break
        else:
            speak("❌ Invalid choice.", planner.voice_settings)

# --- Budget Management Menu ---
def budget_menu(planner, demo_mode):
    """
    Handles event and task budgets — setting, editing, viewing summaries.

    Args:
        planner (EventPlanner): The planner object.
        demo_mode (bool): If True, operates on a default demo event.

    Returns:
        None

    Logic:
        - Offers separate controls for event budgets and task-specific budgets.
        - Also shows budget summaries for tracking.
    """
    show_logo_short(planner.voice_settings)
    while True:
        menu = [
            "\n💰 Budget Manager",
            "1. Manage Event Budgets",
            "2. Manage Task Budgets",
            "3. View Budget Summaries",
            "0. Back to Main Menu"
        ]
        speak_menu(menu, planner.voice_settings)
        choice = speak_input("Choose an option: ", planner.voice_settings)

        if choice == "1":
            menu_event_budget = [
                "\n💸 Event Budget Control",
                "1. Set Event Budget",
                "2. Edit Event Budget",
                "3. View All Event Budgets",
                "0. Back to Budget Manager"
            ]
            speak_menu(menu_event_budget, planner.voice_settings)
            choice_event_budget = speak_input("Choose an option: ", planner.voice_settings)
            if choice_event_budget == "1": planner.set_event_budget(DEMO_EVENT if demo_mode else None)
            elif choice_event_budget == "2": planner.edit_event_budget(DEMO_EVENT if demo_mode else None)
            elif choice_event_budget == "3": planner.view_all_event_budgets()
            elif choice_event_budget == "0": continue
            else: speak("❌ Invalid choice.", planner.voice_settings)

        elif choice == "2":
            menu_task_budget = [
                "\n🏷️ Task Budget Allocation",
                "1. Assign Budget to Task",
                "2. View Task Budgets Only",
                "0. Back to Budget Manager"
            ]
            speak_menu(menu_task_budget, planner.voice_settings)
            choice_task_budget = speak_input("Choose an option: ", planner.voice_settings)
            if choice_task_budget == "1": planner.assign_budget_to_task(DEMO_EVENT if demo_mode else None)
            elif choice_task_budget == "2": planner.view_task_budgets_only(DEMO_EVENT if demo_mode else None)
            elif choice_task_budget == "0": continue
            else: speak("❌ Invalid choice.", planner.voice_settings)

        elif choice == "3":
            menu_summary = [
                "\n📊 Budget Insights",
                "1. View Event Budget Summary",
                "0. Back to Budget Manager"
            ]
            speak_menu(menu_summary, planner.voice_settings)
            choice_summary = speak_input("Choose an option: ", planner.voice_settings)
            if choice_summary == "1": planner.view_event_budget_summary(DEMO_EVENT if demo_mode else None)
            elif choice_summary == "0": continue
            else: speak("❌ Invalid choice.", planner.voice_settings)

        elif choice == "0":
            break
        else:
            speak("❌ Invalid choice.", planner.voice_settings)

# --- Search & Sort Menu ---
def search_sort_menu(planner, demo_mode):
    """
    Allows searching events and sorting tasks/events using various filters.

    Args:
        planner (EventPlanner): The planner instance.
        demo_mode (bool): Flag for demo-based task sorting.

    Returns:
        None

    Logic:
        - Search options: name, tag, keyword, date, starred.
        - Sort options: for both events and tasks.
    """
    show_logo_short(planner.voice_settings)
    while True:
        menu = [
            "\n🔍 Search & Sort",
            "1. Search Events",
            "2. Sort Events",
            "3. Sort Tasks",
            "0. Back to Main Menu"
        ]
        speak_menu(menu, planner.voice_settings)
        choice = speak_input("Choose an option: ", planner.voice_settings)
        if choice == "1": planner.search_events()
        elif choice == "2": planner.sort_events()
        elif choice == "3": planner.sort_tasks(DEMO_EVENT if demo_mode else None)
        elif choice == "0": break
        else: speak("❌ Invalid choice.", planner.voice_settings)

# --- Settings Menu ---
def settings_menu(planner, user, voice_settings):
    """
    Menu for app settings — voice, help, demo data, about, and account options.

    Args:
        planner (EventPlanner): Main planner object.
        user (str): Logged-in user.
        voice_settings (dict): Voice TTS config.

    Returns:
        bool: True to stay in settings, False to log out or exit.

    Logic:
        - Includes loading demo data and changing voice or password.
        - Offers return to login or deletion of account.
    """
    while True:
        show_logo_short(planner.voice_settings)
        menu = [
            "\n⚙️ Settings",
            "1. Configure Voice Settings",
            "2. Help & Tour",
            "3. Load Demo Data",
            "4. About Momentera",
            "5. Account Settings",
            "0. Back to Main Menu"
        ]
        speak_menu(menu, voice_settings)
        choice = speak_input("Choose an option: ", voice_settings)
        if choice == "1":
            configure_voice_settings(voice_settings)
        elif choice == "2":
            help_and_tour(planner)
        elif choice == "3":
            load_demo_data(planner)
        elif choice == "4":
            about(voice_settings)
        elif choice == "5":
            account_settings_menu(planner, user)
        elif choice == "0":
            break
        else:
            speak("❌ Invalid choice.", voice_settings)

# --- Account Settings Menu ---
def account_settings_menu(planner, user):
    """
    Submenu for managing the user account — change password, logout, delete account.

    Args:
        planner (EventPlanner): Current planner instance.
        user (str): Logged-in username.

    Returns:
        bool: True to stay in app, False to return to login screen.

    Logic:
        - Logout saves current tasks and exits to login.
        - Account deletion prompts and removes user data if confirmed.
    """
    while True:
        show_logo_short(planner.voice_settings)
        menu = [
            "\n👤 Account Settings",
            "1. Change Password",
            "2. Logout & Save",
            "3. Delete Account",
            "0. Back to Settings"
        ]
        speak_menu(menu, planner.voice_settings)
        choice = speak_input("Choose an option: ", planner.voice_settings)
        if choice == "1": change_password(user, planner.voice_settings)
        elif choice == "2":
            save_tasks(user, planner.events, planner.voice_settings)
            speak("🔒 Logged out. Goodbye, " + user + "!", planner.voice_settings)
            return False # Signal to go back to login
        elif choice == "3":
            if delete_account(user, planner.voice_settings):
                speak("Account deleted. Exiting.", planner.voice_settings)
                exit()
        elif choice == "0":
            break
        else:
            speak("❌ Invalid choice.", planner.voice_settings)
    return True # Stay in settings

# --- Main Menu ---
def main_menu(planner, user, voice_settings, demo_mode):
    """
    Displays the main navigation menu after login.

    Args:
        planner (EventPlanner): Main planner object containing event/task data.
        user (str): Logged in username.
        voice_settings (dict): Current voice configuration.
        demo_mode (bool): Flag to indicate if using a demo event.

    Returns:
        bool: True if staying in menu, False if user logs out or exits.

    Logic:
        - Routes user to sub-menus like Event Manager, Task Manager, Budgets, etc.
        - Supports logout, saving, and exiting cleanly.
    """
    stay_in_menu = True
    while stay_in_menu:
        show_logo_full(voice_settings),    
        menu = [
            "1. Manage Events",
            "2. Manage Tasks",
            "3. Manage Budgets",
            "4. Search & Sort",
            "5. Export Data",
            "6. Settings",
            "0. Exit"
        ]
        speak_menu(menu, voice_settings)
        choice = speak_input("Choose an option: ", voice_settings)

        if choice == "1":
            event_management_menu(planner, demo_mode)
        elif choice == "2":
            task_management_menu(planner, demo_mode)
        elif choice == "3":
            budget_menu(planner, demo_mode)
        elif choice == "4":
            search_sort_menu(planner, demo_mode)
        elif choice == "5":
            planner.export_to_file()
        elif choice == "6":
            stay_in_settings = settings_menu(planner, user, voice_settings)
            if not stay_in_settings:
                stay_in_menu = False  # Exit menu if logout chosen
        elif choice == "0":
            save_tasks(user, planner.events, voice_settings)
            speak("👋 Exiting Momentera. Goodbye!", voice_settings)
            stay_in_menu = False  # Exit menu on exit
        else:
            speak("❌ Invalid choice.", voice_settings)

    return stay_in_menu  # Return False if logout/exiting occurred

def main(voice_settings):
    """
    Entry point of the Momentera app. Handles login, account creation, voice settings, and main menu.

    Args:
        voice_settings (dict): Current voice configuration (enabled, rate, voice ID, etc.)

    Returns:
        None

    Logic:
        - Displays the main welcome screen.
        - Allows login, account creation, or configuring voice.
        - If login is successful, loads the user's tasks and opens the main menu.
    """
    
    check_user_file()
    demo_mode = False

    while True:
        show_logo_short(voice_settings)
        speak_menu([
            "\n🔐 Welcome! Choose an option:",
            "1. Log In",
            "2. Create Account",
            "3. Configure Voice Settings",
            "0. Exit"
        ], voice_settings)

        choice = speak_input("Choose an option: ", voice_settings)

        if choice == "1":
            user = login(voice_settings)
            if user:
                planner = load_tasks(user, voice_settings)
                planner.voice_settings = voice_settings
                speak("✅ Login successful. Welcome back, " + user + "!", voice_settings)
                main_menu(planner, user, voice_settings, demo_mode)
            else:
                speak("❌ Login attempt failed. Please try again.", voice_settings)

        elif choice == "2":
            user = create_account(voice_settings)
            if user:
                planner = load_tasks(user, voice_settings)
                planner.voice_settings = voice_settings
                speak("✅ Account created and logged in as " + user + ".", voice_settings)
                main_menu(planner, user, voice_settings, demo_mode)

        elif choice == "3":
            new_settings = configure_voice_settings("default_user", voice_settings)
            if new_settings:
                voice_settings.update(new_settings)
                save_voice_settings("default_user", voice_settings)

        elif choice == "0":
            speak("👋 Goodbye!", voice_settings)
            break

        else:
            speak("❌ Invalid option.", voice_settings)

if __name__ == "__main__":
    voice_settings = welcome_and_choose_voice()
    main(voice_settings)