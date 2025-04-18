import datetime
from voice_system import speak

class EventPlanner:
    """
    Main class for managing events, tasks, reminders, categories, budgets, and recurrence.

    Responsibilities:
        - Create, edit, delete, view events and tasks.
        - Handle task progress, reminders, sorting, priorities, and archiving.
        - Support features like tagging, countdown, budgets, search/sort, and exporting.

    Attributes:
        events (dict): Stores all active event data.
        archived_events (dict): Stores archived events separately.
        voice_settings (dict): Voice output settings for TTS feedback.

    Methods:
        Includes 60+ functions for input handling, validation, data mutation, and voice interaction.
        Grouped logically into:
            - Helper input and speech methods
            - Event operations
            - Task operations
            - Budget and reminders
            - Search, sort, and export
    """
    def __init__(self, voice_settings=None):
        self.events = {}
        self.archived_events = {}
        if voice_settings is not None:
            self.voice_settings = voice_settings
        else:
            self.voice_settings = {"enabled": False}  # Default to disabled if not provided

    def _speak(self, text):
        """
        Outputs text to console and optionally speaks it aloud if voice mode is enabled.

        Args:
            text (str): The message to display and speak.

        Returns:
            None

        Logic:
            - Always prints the message.
            - Uses the speak function from voice_system if voice is enabled.

        Exceptions:
            - Relies on external pyttsx3 engine. Any voice-related exceptions are handled there.
        """
        print(text)  # Always print
        if self.voice_settings.get("enabled"):
            speak(text, self.voice_settings)

    def _input_valid(self, prompt, data_type, extra_check=None, max_retries=5):
        """
        Handles validated input from the user for various data types like date, time, float, and int.

        Args:
            prompt (str): The input prompt for the user.
            data_type (str): One of "date", "time", "float", or "int".
            extra_check (function, optional): A validation function for additional checks.
            max_retries (int): Number of allowed invalid attempts before returning None.

        Returns:
            Depends on data_type:
                - str (for 'date' or 'time')
                - float or int
                - None if all attempts fail

        Logic:
            - Repeatedly prompts until valid input is entered or retries exhausted.
            - Applies type conversion and optional extra validation logic.

        Exceptions:
            - Catches ValueError for conversion issues.
        """
        attempts = 0
        while attempts < max_retries:
            user_input = input(prompt).strip()
            if not user_input:
                self._speak("❌ Input cannot be empty.")
                attempts += 1
                continue
            try:
                if data_type == "date":
                    datetime.datetime.strptime(user_input, "%Y-%m-%d")
                    return user_input
                elif data_type == "time":
                    datetime.datetime.strptime(user_input, "%H:%M")
                    return user_input
                elif data_type == "float":
                    value = float(user_input)
                    if extra_check and not extra_check(value):
                        self._speak("❌ Invalid number.")
                        attempts += 1
                        continue
                    return value
                elif data_type == "int":
                    value = int(user_input)
                    if extra_check and not extra_check(value):
                        self._speak("❌ Invalid number.")
                        attempts += 1
                        continue
                    return value
            except ValueError:
                self._speak("❌ Invalid " + data_type + " format.")
            attempts += 1
        self._speak("❌ Too many invalid attempts.")
        return None

    def _input_valid_date(self, prompt):
        """
        Prompts user for a future-valid date input in YYYY-MM-DD format.

        Args:
            prompt (str): Message shown to the user.

        Returns:
            str: A valid date string or 'No end' if 'none' is entered.

        Logic:
            - Uses _input_valid() to check date format.
            - Ensures date is not in the past unless 'none' is typed.
            - If 'none' is entered, returns 'No end' (for recurrence).

        Exceptions:
            - Handles ValueError if date parsing fails.
        """
        while True:
            user_input = self._input_valid(prompt, "date")
            if user_input:
                if user_input.lower() == "none":
                    return "No end"
                input_date = datetime.datetime.strptime(user_input, "%Y-%m-%d").date()
                today = datetime.datetime.now().date()
                if input_date < today:
                    self._speak("❌ The date cannot be in the past. Please enter a future date.")
                    continue
                return user_input

    def _input_valid_time(self, prompt):
        """
        Prompts user for a valid time in HH:MM 24-hour format.

        Args:
            prompt (str): The prompt message.

        Returns:
            str: Valid time string or None after max retries.

        Logic:
            - Calls _input_valid() with 'time' type.
        """
        return self._input_valid(prompt, "time")

    def _input_valid_float(self, prompt):
        """
        Prompts user for a non-negative float value.

        Args:
            prompt (str): Message shown to user.

        Returns:
            float: Parsed float value >= 0, or None after failures.

        Logic:
            - Uses _input_valid with type 'float' and lambda check >= 0.
            """
        return self._input_valid(prompt, "float", extra_check=lambda x: x >= 0)

    def _input_valid_int(self, prompt, extra_check=None):
        """
        Prompts user for an integer input, optionally validated by extra_check.

        Args:
            prompt (str): Prompt for the user.
            extra_check (function, optional): Custom validation function (returns True/False).

        Returns:
            int: Validated integer, or None after invalid attempts.

        Logic:
            - Delegates to _input_valid().
            - Default check ensures non-negative integer if no custom check given.
        """
        return self._input_valid(prompt, "int", extra_check=extra_check or (lambda x: x >= 0))

    def get_priority(self, prompt="Priority (Low/Medium/High): "):
        """
        Asks user to choose a priority level.

        Args:
            prompt (str): Prompt shown to user.

        Returns:
            str: One of "Low", "Medium", or "High". Defaults to "Medium" on repeated invalid input.

        Logic:
            - Accepts case-insensitive inputs.
            - Caps attempts to 3 before defaulting.
        """
        # Max attempts for valid input
        max_attempts = 3
        attempts = 0
    
        while attempts < max_attempts:
            value = input(prompt).strip().capitalize()
            if value in ["Low", "Medium", "High"]:
                return value
            self._speak("❌ Invalid priority. Please enter 'Low', 'Medium', or 'High'.")
            attempts += 1
    
        # If the user exceeds max attempts, default to 'Medium'
        self._speak(f"❌ Invalid input multiple times. Defaulting to 'Medium'. You can change it later.")
        return "Medium"  # Default value

    def get_status(self, prompt="Status (Pending/In Progress/Completed): "):
        """
        Prompts the user to choose a task status.

        Args:
            prompt (str): Input message.

        Returns:
            str: One of "Pending", "In Progress", "Completed". Defaults to "Pending".

        Logic:
            - Repeats prompt for up to 3 attempts before returning default.
        """
        # Max attempts for valid input
        max_attempts = 3
        attempts = 0
    
        while attempts < max_attempts:
            value = input(prompt).strip().title()
            if value in ["Pending", "In Progress", "Completed"]:
                return value
            self._speak("❌ Invalid status. Please enter 'Pending', 'In Progress', or 'Completed'.")
            attempts += 1
    
        # If the user exceeds max attempts, default to 'Pending'
        self._speak(f"❌ Invalid input multiple times. Defaulting to 'Pending'. You can change it later.")
        return "Pending"  # Default value

    def get_recurrence(self):
        """
        Allows the user to define if an event is recurring and configures its frequency.

        Args:
            None

        Returns:
            dict: Recurrence settings with keys:
                - enabled (bool)
                - frequency (str)
                - interval (int)
                - until (str)

        Logic:
            - Asks whether event is recurring.
            - Collects frequency, interval, and optional end date.
            - Uses default values if invalid input is entered.
        """
        recurrence = {"enabled": False}

        is_recurring = self.ask_yes_no("Make this a recurring event?")
        if not is_recurring:
            return recurrence

        valid_freqs = ["daily", "weekly", "monthly", "yearly"]
        max_attempts = 3
        attempts = 0

        while attempts < max_attempts:
            freq = input("Frequency (daily/weekly/monthly/yearly): ").strip().lower()
            if freq in valid_freqs:
                break
            self._speak("❌ Invalid frequency. Please enter a valid option.")
            attempts += 1
        else:
            self._speak("⚠️ Too many invalid attempts. Defaulting to 'weekly'.")
            freq = "weekly"

        interval = input("Repeat every how many units? (e.g., every 1 week): ").strip()
        if not interval.isdigit() or int(interval) < 1:
            self._speak("❌ Invalid interval. Defaulting to 1.")
            interval = 1
        else:
            interval = int(interval)

        # Use the helper method for the recurrence end date
        until = self._input_valid_date("End date for recurrence (YYYY-MM-DD) or type 'none': ")

        if until.lower() == "none" or until == "":
            until = "No end"

        recurrence = {
            "enabled": True,
            "frequency": freq,
            "interval": interval,
            "until": until or "No end"
        }

        return recurrence

    def get_tags(self, prompt="Add tags (comma separated or leave blank): "):
        """
        Collects tags from user input and formats them.

        Args:
            prompt (str): Prompt message.

        Returns:
            list: A list of lowercase tags as strings.

        Logic:
            - Splits input by commas, strips whitespace, and removes blanks.
        """
        tag_input = input(prompt).strip().lower()
        return [t.strip().lower() for t in tag_input.split(",") if t.strip()]

    def _get_event(self, name=None):
        """
        Retrieves an event by name, prompting user if name is not provided.

        Args:
            name (str, optional): Name of the event. If None, prompts user for it.

        Returns:
            tuple: (event_name (str), event_data (dict)) if found, else (None, None)

        Logic:
            - Converts input to lowercase and checks if it exists in events.
            - If not found or empty, gives voice feedback and returns None.
        """
        name = name or input("Enter event name: ").strip().lower()
        if not name:
            self._speak("❌ Event name cannot be empty.")
            return None, None
        if name not in self.events:
            self._speak("❌ Event not found.")
            return None, None
        return name, self.events[name]

    def ask_yes_no(self, prompt):
        """
        Asks the user a yes/no question.

        Args:
            prompt (str): Prompt text without (y/n) suffix.

        Returns:
            bool: True if user says yes, False for no.

        Logic:
            - Accepts 'y', 'yes', 'n', 'no' (case-insensitive).
            - Repeats until a valid input is received.
        """
        while True:
            ans = input(prompt + " (y/n): ").strip().lower()
            if ans in ["y", "yes"]:
                return True
            elif ans in ["n", "no"]:
                return False
            else:
                self._speak("❌ Please enter y or n.")

    def add_months(self, date, months):
        """
        Adds a number of months to a given date, handling month overflow and leap years.

        Args:
            date (datetime.date): The starting date.
            months (int): Number of months to add.

        Returns:
            datetime.date: Adjusted date.

        Logic:
            - Calculates new month and year.
            - Adjusts for last valid day in target month.
        """
        
        month = date.month - 1 + months
        year = date.year + month // 12
        month = month % 12 + 1

        # Handle days of the month
        day = min(date.day, [
            31,
            29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
            31, 30, 31, 30, 31, 31, 30, 31, 30, 31
        ][month - 1])

        try:
            # Try to return the adjusted date
            return datetime.date(year, month, day)
        except ValueError:
            # If the day is invalid (like adding months to a February 30th), return the last valid day of the month
            return datetime.date(year, month, day)

    def add_years(self, date, years):
        """
        Adds years to a given date, handling leap years safely.

        Args:
            date (datetime.date): Original date.
            years (int): Years to add.

        Returns:
            datetime.date: Resulting date.

        Logic:
            - Uses replace() for new year.
            - If Feb 29 becomes invalid, defaults to Feb 28.
        """
        try:
            # Try to adjust the year directly
            return date.replace(year=date.year + years)
        except ValueError:
            # Handle the case where the new year is a leap year but the original date was Feb 29
            return date.replace(month=2, day=28, year=date.year + years)

    def create_event(self, name=None, date=None, notes=None):
        """
        Creates a new event with all attributes like tags, reminder, duration, priority, and budget.

        Args:
            name (str, optional): Event name. If None, prompts user.
            date (str, optional): Event date. If None, prompts user.
            notes (str, optional): Event notes. If None, prompts user.

        Returns:
            None

        Logic:
            - Collects user input for all event fields.
            - Validates date format and ensures it's not a duplicate name.
            - Initializes nested tasks and recurrence dicts.
            - Stores event in the events dictionary.

        Exceptions:
            - Handles bad input through built-in validations.
        """
        name = name or input("Enter event name: ").strip().lower()
        if not name:
            self._speak("❌ Event name cannot be empty.")
            return
        if name in self.events:
            self._speak("❌ Event already exists.")
            return

        date = date or self._input_valid_date("Enter event date (YYYY-MM-DD): ").strip()
        notes = notes or input("Enter event notes: ").strip().lower()
        tags = self.get_tags()
        pinned = self.ask_yes_no("Pin this event?")
        starred = self.ask_yes_no("Star this event?")
        reminder_days = self._input_valid_int("Remind how many days before event? (0 for none, max 365): ", extra_check=lambda x: 0 <= x <= 365)

        category = input("Enter category (optional): ").strip().lower()
        priority = self.get_priority()
        budget = self._input_valid_float("Enter budget (or 0): ")

        set_duration = self.ask_yes_no("Set start/end time now?")
        start_time = self._input_valid_time("Start time (HH:MM): ") if set_duration else ""
        end_time = self._input_valid_time("End time (HH:MM): ") if set_duration else ""
        recurrence = self.get_recurrence()

        self.events[name] = {
            "date": date,
            "notes": notes,
            "tags": tags,
            "category": category,
            "priority": priority,
            "budget": budget,
            "pinned": pinned,
            "starred": starred,
            "reminder_days": reminder_days,
            "start_time": start_time,
            "end_time": end_time,
            "recurrence": recurrence,
            "tasks": [],
            "archived_tasks": []
        }
        self._speak("🎉 Event created!")

    def view_event(self, name=None):
        """
        Displays detailed information about a single event, including its tasks and metadata.

        Args:
            name (str, optional): Event name. If None, prompts user.

        Returns:
            None

        Logic:
            - Retrieves and prints all key-value fields for the event.
            - Includes recurrence, tags, notes, reminders, and tasks if present.
        """
        name, e = self._get_event(name)
        if not e:
            return
        lines = [
            f"\n📅 Event: {name}",
            f"Date: {e['date']}",
            f"Notes: {e['notes'] or '(No notes)'}",
            f"Tags: {', '.join(e['tags']) or '(No tags)'}",
            f"Category: {e.get('category', '-')}",
            f"Priority: {e.get('priority', 'Medium')}",
            f"Start Time: {e.get('start_time', '-')}",
            f"End Time: {e.get('end_time', '-')}",
            f"Pinned: {'📌 Yes' if e.get('pinned') else 'No'}",
            f"Starred: {'⭐ Yes' if e.get('starred') else 'No'}",
            f"Reminder Days: {e.get('reminder_days', 0)}",
            f"Budget: ₹{e.get('budget', 0)}"
        ]
        if e["recurrence"].get("enabled"):
            lines.append(f"Recurring: {e['recurrence']['frequency'].capitalize()} every {e['recurrence']['interval']} until {e['recurrence'].get('until', 'No end')}")
        lines.append("Tasks:")
        if e["tasks"]:
            for i, task in enumerate(e["tasks"], 1):
                lines.append(str(i) + ". " + task["task"] + " - " + task.get("status", "Pending"))
        else:
            lines.append("No tasks yet.")
        for line in lines:
            self._speak(line)

    def view_all_events(self):
        """
        Displays brief summaries of all existing events.

        Args:
            None

        Returns:
            None

        Logic:
            - Iterates through the events dictionary and prints name, date, and priority.
            - Skips any entries with read/access issues.
        """
        if not self.events:
            self._speak("No events available.")
            return

        self._speak("Here are your events:")
        for name in self.events:
            try:
                _, event = self._get_event(name)
                if event:
                    details = "Event Name: " + name.capitalize()
                    details += ", Date: " + event.get("date", "N/A")
                    details += ", Priority: " + event.get("priority", "N/A")
                    self._speak(details)
            except Exception as e:
                self._speak("⚠️ Error reading event: " + name)

    def delete_event(self, name=None):
        """
        Deletes an event after user confirmation.

        Args:
            name (str, optional): Event name. If None, prompts user.

        Returns:
            None

        Logic:
            - Confirms with user before deletion.
            - Deletes from the events dictionary if exists.
        """
        name = name or input("Enter event name to delete: ").strip().lower()
        if name in self.events:
            if self.ask_yes_no("Are you sure you want to delete this event?"):
                del self.events[name]
                self._speak("🗑️ Event deleted.")
            else:
                self._speak("❌ Deletion cancelled.")
        else:
            self._speak("❌ Event not found.")

    def edit_event(self, name=None):
        """
        Allows the user to edit various fields of an existing event.

        Args:
            name (str, optional): Event name to edit. If None, prompts for name.

        Returns:
            None

        Logic:
            - Provides menu of editable fields (name, notes, category, etc.).
            - Updates the event dictionary accordingly.
        """
        name, e = self._get_event(name)
        if not e:
            return
        while True:
            options = [
                "\n🛠️ Edit Event: " + name,
                "1. Name", "2. Date", "3. Notes", "4. Tags", "5. Category", "6. Priority",
                "7. Reminder", "8. Budget", "9. Duration", "10. Pin", "11. Star", "12. Recurrence", "0. Done"
            ]
            for line in options:
                self._speak(line)
            choice = input("Choose option: ")

            if choice == "1":
                new_name = input("New name: ").strip().lower()
                if not new_name:
                    self._speak("❌ Event name cannot be empty.")
                elif new_name in self.events:
                    self._speak("❌ Event with that name already exists.")
                else:
                    self.events[new_name] = self.events.pop(name)
                    name = new_name
                    e = self.events[name]
            elif choice == "2":
                e["date"] = self._input_valid_date("New date: ")
            elif choice == "3":
                e["notes"] = input("New notes: ").strip().lower()

            elif choice == "4":
                tag_action = input("Add or Remove tag? (a/r): ").lower()
                if tag_action == "a":
                    tag = input("Enter tag to add: ").strip().lower()
                    if tag:
                        e["tags"].append(tag)
                        self._speak("🏷️ Tag added.")
                elif tag_action == "r":
                    tag = input("Enter tag to remove: ").strip().lower()
                    if tag in e["tags"]:
                        e["tags"].remove(tag)
                        self._speak("🏷️ Tag removed.")
                    else:
                        self._speak("❌ Tag not found.")
                else:
                    self._speak("❌ Invalid action. Enter 'a' to add or 'r' to remove.")

            elif choice == "5":
                e["category"] = input("New category: ").strip()
            elif choice == "6":
                self.set_event_priority(name)
            elif choice == "7":
                e["reminder_days"] = self._input_valid_int("Days before to remind (max 365): ", extra_check=lambda x: 0 <= x <= 365)
            elif choice == "8":
                e["budget"] = self._input_valid_float("New budget: ")
            elif choice == "9":
                self.set_or_edit_duration(name)
            elif choice == "10":
                self.toggle_pin_event(name)
            elif choice == "11":
                self.toggle_star_event(name)
            elif choice == "12":
                e["recurrence"] = self.get_recurrence()
            elif choice == "0":
                break
            else:
                self._speak("❌ Invalid choice.")

    def toggle_pin_event(self, name=None):
        """
        Toggles the pinned status of an event.

        Args:
            name (str, optional): Event name. If None, prompts user.

        Returns:
            None

        Logic:
            - Switches boolean value of 'pinned' key in event.
            - Provides feedback after toggle.
        """
        name = name or input("Enter event name: ").strip().lower()
        if name in self.events:
            self.events[name]["pinned"] = not self.events[name].get("pinned", False)
            self._speak("📌 Pin status toggled.")
        else:
            self._speak("❌ Event not found.")

    def toggle_star_event(self, name=None):
        """
        Toggles the starred (favorite) status of an event.

        Args:
            name (str, optional): Event name. If None, prompts user.

        Returns:
            None

        Logic:
            - Updates 'starred' field in the event dict.
            - Provides spoken and printed confirmation.
        """
        name = name or input("Enter event name: ").strip().lower()
        if name in self.events:
            self.events[name]["starred"] = not self.events[name].get("starred", False)
            self._speak("⭐ Star status toggled.")
        else:
            self._speak("❌ Event not found.")

    def set_event_priority(self, name=None, priority=None):
        """
        Sets or updates the priority of a specific event.

        Args:
            name (str, optional): Event name. If None, prompts user.
            priority (str, optional): Priority level (Low/Medium/High). If None, prompts user.

        Returns:
            None

        Logic:
            - Retrieves or prompts event and sets priority field.
        """
        name, e = self._get_event(name)
        if not e:
            return
    
        # If priority is not provided, call get_priority to handle user input
        if priority is None:
            priority = self.get_priority("Priority (Low/Medium/High): ")
    
        self.events[name]["priority"] = priority
        self._speak("✅ Priority updated.")

    def set_or_edit_duration(self, name=None, start=None, end=None):
        """
        Sets or edits the start and end time of an event.

        Args:
            name (str, optional): Event name. If None, prompts.
            start (str, optional): Start time in HH:MM. If None, prompts.
            end (str, optional): End time in HH:MM. If None, prompts.

        Returns:
            None

        Logic:
            - Prompts for start and end time if not provided.
            - Validates that end is after start.
        """
        name, e = self._get_event(name)
        if not e:
            return

        start = self._input_valid_time("Start time (HH:MM): ")
        end = self._input_valid_time("End time (HH:MM): ")

        # Ensure end time is not before start time
        start_time = datetime.datetime.strptime(start, "%H:%M").time()
        end_time = datetime.datetime.strptime(end, "%H:%M").time()

        if end_time <= start_time:
            self._speak("❌ End time cannot be earlier than or equal to start time. Please enter valid times.")
            return

        self.events[name]["start_time"] = start
        self.events[name]["end_time"] = end
        self._speak("⏱️ Duration updated.")

    def set_event_category(self, name=None, category=None):
        """
        Assigns a category label to an event.

        Args:
            name (str, optional): Event name.
            category (str, optional): New category. If None, prompts user.

        Returns:
            None

        Logic:
            - Updates event dictionary with category.
        """
        name, e = self._get_event(name)
        if not e:
            return
        if category is None:
            category = input("Enter category: ").strip().lower()
        self.events[name]["category"] = category
        self._speak("✅ Category set.")

    def add_tag(self, name=None):
        """
        Adds a tag to a specific event.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Prompts user for tag and adds to the tag list if not already present.
        """
        name = name or input("Enter event name: ").strip()
        if name in self.events:
            tag = input("Enter tag to add: ").strip().lower()
            if tag not in [t.lower() for t in self.events[name]["tags"]]:
                self.events[name]["tags"].append(tag)

    def remove_tag(self, name=None):
        """
        Removes a tag from an event’s tag list.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Prompts for tag to remove and confirms if it exists.
        """
        name = name or input("Enter event name: ").strip().lower()
        if name in self.events:
            self._speak("Current tags: " + ", ".join(self.events[name]["tags"]))
            tag = input("Enter tag to remove: ").strip().lower()
            if tag in self.events[name]["tags"]:
                self.events[name]["tags"].remove(tag)
                self._speak("🏷️ Tag removed.")
            else:
                self._speak("❌ Tag not found.")
        else:
            self._speak("❌ Event not found.")

    def manage_event_archive(self):
        """
        Manages archiving, viewing, and restoring archived events.

        Args:
            None

        Returns:
            None

        Logic:
            - Handles archive/unarchive actions from a user-driven menu.
            - Transfers data between events and archived_events dictionaries.
        """
        options = ["\n📦 Archive Manager", "1. Archive Event", "2. View Archived", "3. Restore Archived", "0. Back"]
        for line in options:
            self._speak(line)
        choice = input("Choose: ")
        if choice == "1":
            name = input("Enter event name to archive: ").strip().lower()
            if name in self.events:
                self.archived_events[name] = self.events.pop(name)
                self._speak("📦 Event archived.")
            else:
                self._speak("❌ Event not found.")
        elif choice == "2":
            if not self.archived_events:
                self._speak("📭 No archived events.")
            else:
                for name in self.archived_events:
                    self._speak("- " + name)
        elif choice == "3":
            name = input("Enter archived event name to restore: ").strip().lower()
            if name in self.archived_events:
                if name in self.events:
                    self._speak("❌ Cannot restore. An event with this name already exists.")
                    return
                self.events[name] = self.archived_events.pop(name)
                self._speak("✅ Restored.")
            else:
                self._speak("❌ Not found.")

        elif choice == "0":
            return
        else:
            self._speak("❌ Invalid.")

    def add_tasks(self, name=None, task_list=None):
        """
        Adds one or more tasks to an event.

        Args:
            name (str, optional): Event name. If None, prompts.
            task_list (list of dict, optional): Batch task data. If None, user adds a single task interactively.

        Returns:
            None

        Logic:
            - Allows manual or batch task creation.
            - Ensures task deadline doesn't exceed event date (unless recurring).
            - Each task includes: task, deadline, priority, status, budget.
        """
        name, e = self._get_event(name)
        if not e:
            return
    
        if task_list is not None:
            for task in task_list:
                task_obj = {
                    "task": task.get("task", ""),
                    "deadline": task.get("deadline", ""),
                    "priority": task.get("priority", "Medium"),
                    "status": task.get("status", "Pending"),
                    "budget": task.get("budget", 0)
                }
                self.events[name]["tasks"].append(task_obj)
            msg = "✅ Tasks added."
            self._speak(msg)
        else:
            task_text = input("Task description: ").strip().lower()
        
            # Get and validate deadline
            deadline = self._input_valid_date("Deadline (YYYY-MM-DD or blank): ")
            if deadline:
                try:
                    task_date = datetime.datetime.strptime(deadline, "%Y-%m-%d").date()
                    event_date = datetime.datetime.strptime(e["date"], "%Y-%m-%d").date()
                    # Check that deadline is on or before event date, unless event is recurring
                    if not e.get("recurrence", {}).get("enabled", False) and task_date > event_date:
                        self._speak("❌ Deadline must be on or before event date unless event is recurring.")
                        deadline = ""  # Reset so task still adds but with no deadline
                except ValueError:
                    self._speak("⚠️ Invalid deadline format. Skipping deadline.")
                    deadline = ""  # Reset in case of an invalid date

            # Get other task details
            priority = self.get_priority("New priority (Low/Medium/High): ")
            status = self.get_status()
            budget = self._input_valid_float("Enter task budget (or 0): ")

            task = {
                "task": task_text,
                "deadline": deadline,
                "priority": priority,
                "status": status,
                "budget": budget
            }

            self.events[name]["tasks"].append(task)
            self._speak("✅ Task added.")

    def view_tasks(self, name=None):
        """
        Displays all tasks for a selected event, with an option to hide completed ones.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Prompts user whether to show/hide completed tasks.
            - Displays tasks with status, deadline, priority, and budget.
        """
        name, e = self._get_event(name)
        if not e:
            return
        tasks = self.events[name]["tasks"]
        if not tasks:
            self._speak("📭 No tasks found.")
            return

        hide = self.ask_yes_no("Hide completed tasks?")

        self._speak(f"📋 Tasks for {name}")
        for i, task in enumerate(tasks, 1):
            if hide and task.get("status") == "Completed":
                continue
            line = f"{i}. {task['task']}, Status: {task.get('status', 'Pending')}, Deadline: {task.get('deadline', '-')}, Priority: {task.get('priority', 'Medium')}, Budget: ₹{task.get('budget', 0)}"
            self._speak(line)

    def edit_task(self, name=None):
        """
        Edits the details of a selected task from an event.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Displays a list of tasks and allows editing fields like description, deadline, status, priority, budget.
            - Optionally deletes the task.
        """
        name, e = self._get_event(name)
        if not e:
            return
        tasks = self.events[name]["tasks"]
        if not tasks:
            self._speak("📭 No tasks to edit.")
            return

        for i, task in enumerate(tasks, 1):
            self._speak(f"{i}. {task['task']}")

        index_input = input("Choose task number: ").strip()
        if not index_input.isdigit():
            self._speak("❌ Please enter a number.")
            return

        index = int(index_input) - 1
        if index < 0 or index >= len(tasks):
            self._speak("❌ Invalid task number.")
            return

        task = tasks[index]
        while True:
            self._speak(f"Editing: {task['task']}")
            self._speak("1. Description\n2. Deadline\n3. Priority\n4. Status\n5. Budget\n6. Delete Task\n0. Done")
            opt = input("Choose: ")

            if opt == "1":
                task["task"] = input("New description: ").strip().lower()

            elif opt == "2":
                deadline = self._input_valid_date("New deadline (YYYY-MM-DD): ")
                if deadline:
                    try:
                        task_date = datetime.datetime.strptime(deadline, "%Y-%m-%d").date()
                        event_date = datetime.datetime.strptime(e["date"], "%Y-%m-%d").date()
                        if not e.get("recurrence", {}).get("enabled", False) and task_date > event_date:
                            self._speak("❌ Deadline must be on or before event date unless event is recurring.")
                            deadline = ""  # Clear it if invalid
                    except Exception:
                        self._speak("⚠️ Could not validate deadline. Skipping deadline.")
                        deadline = ""
                task["deadline"] = deadline

            elif opt == "3":
                task["priority"] = self.get_priority("New priority (Low/Medium/High): ")
            elif opt == "4":
                task["status"] = self.get_status()
            elif opt == "5":
                budget = self._input_valid_float("New budget: ")
                if budget is not None:
                    task["budget"] = budget
            elif opt == "6":
                confirm = self.ask_yes_no("Delete this task?")
                if confirm:
                    tasks.pop(index)
                    self._speak("🗑️ Task deleted.")
                    break
            elif opt == "0":
                break
            else:
                self._speak("❌ Invalid option.")

    def archive_task(self, name=None):
        """
        Archives a selected task from an event into the event’s archived_tasks list.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Moves task from 'tasks' list to 'archived_tasks'.
        """
        name, e = self._get_event(name)
        if not e:
            return

        tasks = e["tasks"]
        if not tasks:
            self._speak("📭 No tasks to archive.")
            return

        for i, task in enumerate(tasks, 1):
            self._speak(str(i) + ". " + task["task"] + " - " + task["status"])

        index_input = input("Which task to archive? ").strip()
        if not index_input.isdigit():
            self._speak("❌ Please enter a number.")
            return
        index = int(index_input) - 1
        if index < 0 or index >= len(tasks):
            self._speak("❌ Invalid task number.")
            return
        t = tasks.pop(index)
        e["archived_tasks"].append(t)
        self._speak("📦 Task archived.")

    def view_archived_tasks(self, name=None):
        """
        Displays all archived tasks for a selected event.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Iterates through archived_tasks list and prints task info.
        """
        name, e = self._get_event(name)
        if not e:
            return

        archived = e["archived_tasks"]
        if not archived:
            self._speak("📭 No archived tasks.")
            return

        self._speak("🗃️ Archived Tasks:")
        for i, t in enumerate(archived, 1):
            self._speak(str(i) + ". " + t["task"] + " - " + t.get("status", "Pending"))

    def restore_archived_task(self, name=None):
        """
        Restores a previously archived task back to active tasks.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Moves task from 'archived_tasks' back to 'tasks'.
        """
        name, e = self._get_event(name)
        if not e:
            return

        archived = e["archived_tasks"]
        if not archived:
            self._speak("📭 No archived tasks.")
            return

        for i, t in enumerate(archived, 1):
            self._speak(str(i) + ". " + t["task"])

        index_input = input("Restore which task? ").strip()
        if not index_input.isdigit():
            self._speak("❌ Please enter a number.")
            return
        index = int(index_input) - 1
        if index < 0 or index >= len(archived):
            self._speak("❌ Invalid task number.")
            return
        task = archived.pop(index)
        e["tasks"].append(task)
        self._speak("✅ Task restored.")

    def delete_task(self, name=None):
        """
        Deletes a specific task from an event after user confirmation.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Prompts user to choose and confirm task deletion.
        """
        name, e = self._get_event(name)
        if not e:
            return
        tasks = self.events[name]["tasks"]
        if not tasks:
            self._speak("📭 No tasks to delete.")
            return

        for i, task in enumerate(tasks, 1):
            self._speak(f"{i}. {task['task']}")

        index_input = input("Which task to delete? ").strip()
        if not index_input.isdigit():
            self._speak("❌ Please enter a number.")
            return
        index = int(index_input) - 1
        if index < 0 or index >= len(tasks):
            self._speak("❌ Invalid task number.")
            return
        confirm = self.ask_yes_no("Are you sure?")
        if confirm:
            tasks.pop(index)
            self._speak("🗑️ Task deleted.")

    def mark_task_progress(self, name=None):
        """
        Updates the status of a task (Pending, In Progress, Completed).

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Lets user choose a task and set a new status.
        """
        name, e = self._get_event(name)
        if not e:
            return
        tasks = self.events[name]["tasks"]
        if not tasks:
            self._speak("📭 No tasks available.")
            return

        for i, t in enumerate(tasks, 1):
            self._speak(f"{i}. {t['task']} - {t['status']}")

        index_input = input("Choose task number: ").strip()
        if not index_input.isdigit():
            self._speak("❌ Please enter a number.")
            return
        index = int(index_input) - 1
        if index < 0 or index >= len(tasks):
            self._speak("❌ Invalid task number.")
            return
        status = input("New status (Pending/In Progress/Completed): ").title().strip()
        if status in ["Pending", "In Progress", "Completed"]:
            tasks[index]["status"] = status
            self._speak("✅ Status updated.")
        else:
            self._speak("❌ Invalid status.")

    def sort_tasks(self, name=None):
        """
        Sorts tasks (active or archived) of an event based on selected criteria.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Sorts based on:
                1. Deadline
                2. Priority
                3. Completed last
                4. Budget (descending)
            - Displays confirmation after sorting.
        """
        name, e = self._get_event(name)
        if not e:
            return

        self._speak("\n🗃️ Sort which tasks?")
        self._speak("1. Active Tasks\n2. Archived Tasks")
        task_type = input("Choose: ").strip()

        if task_type == "1":
            task_list = e["tasks"]
        elif task_type == "2":
            task_list = e["archived_tasks"]
        else:
            self._speak("❌ Invalid option.")
            return

        if not task_list:
            self._speak("📭 No tasks to sort.")
            return

        self._speak("\n🔃 Sort Tasks By:")
        self._speak("1. Deadline (soonest first)\n2. Priority (High first)\n3. Completed last\n4. Budget (high to low)")

        option = input("Choose: ").strip()

        def by_deadline(t):
            deadline = t.get("deadline", "")
            if not deadline:
                # Handle cases where there is no deadline at all
                return datetime.datetime.max

            try:
                # Attempt to parse the date
                return datetime.datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                # Log or speak feedback to inform the user
                self._speak(f"⚠️ Invalid deadline format for task '{t.get('task', '')}'. Using default placeholder.")
        
                # Return a clear placeholder for invalid dates
                return None  # Or return datetime.min, datetime(9999, 12, 31), etc.

        def by_priority(t):
            order = {"High": 0, "Medium": 1, "Low": 2}
            return order.get(t.get("priority", "Medium"), 1)

        def by_completed(t):
            return t.get("status") == "Completed"

        def by_budget(t):
            return -t.get("budget", 0)

        sorters = {
            "1": by_deadline,
            "2": by_priority,
            "3": by_completed,
            "4": by_budget
        }

        if option not in sorters:
            self._speak("❌ Invalid choice.")
            return

        task_list.sort(key=sorters[option])
        self._speak("✅ Tasks sorted.")


    def search_events(self):
        """
        Searches for events using different filters: name, tag, keyword, date, or starred.

        Args:
            None

        Returns:
            None

        Logic:
            - Prompts user for search type and keyword/date.
            - Displays matching event names.
        """
        self._speak("Search Options")
        self._speak("1. By name")
        self._speak("2. By tag")
        self._speak("3. By keyword")
        self._speak("4. By date")
        self._speak("5. Starred only")
        option = input("Choose: ").strip()

        found = []
        for name, e in self.events.items():
            if option == "1":
                keyword = input("Enter event name: ").lower().strip()
                if keyword in name.lower():
                    found.append(name)
            elif option == "2":
                tag = input("Enter tag: ").strip().lower()
                if tag in [t.lower() for t in e["tags"]]:
                    found.append(name)
            elif option == "3":
                keyword = input("Enter keyword: ").lower()
                if keyword in name.lower() or keyword in e["notes"].lower():
                    found.append(name)
            elif option == "4":
                date = self._input_valid_date("Enter date (YYYY-MM-DD): ")
                if date == e["date"]:
                    found.append(name)
            elif option == "5":
                if e.get("starred"):
                    found.append(name)

        if found:
            self._speak("Here are your matching events.")
            for name in found:
                self._speak(name)
        else:
            self._speak("No matches found.")

    def sort_events(self):
        """
        Sorts all events based on name, date, priority, or pin/star status.

        Args:
            None

        Returns:
            None

        Logic:
            - Provides 5 sort options:
                1. Name (A-Z)
                2. Date (earliest first)
                3. Priority (High first)
                4. Starred first
                5. Pinned first
            - Displays sorted event list after applying sorting key.
        """
        self._speak("Sort Options")
        self._speak("1. By name (A-Z)")
        self._speak("2. By date")
        self._speak("3. By priority")
        self._speak("4. Starred first")
        self._speak("5. Pinned first")
        option = input("Choose: ").strip()

        def by_date(e):
            try:
                return datetime.datetime.strptime(self.events[e].get("date", ""), "%Y-%m-%d")
            except ValueError:
                print(f"⚠️ Invalid date format for event {e}: {self.events[e].get('date', '')}")
                return datetime.datetime(9999, 12, 31)
            except KeyError:
                print(f"⚠️ Event {e} does not have a 'date' field.")
                return datetime.datetime(9999, 12, 31)

        def by_priority(e):
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            return priority_order.get(self.events[e].get("priority", "Medium"), 1)

        try:
            if option == "1":
                sorted_list = sorted(self.events)
            elif option == "2":
                sorted_list = sorted(self.events, key=by_date)
            elif option == "3":
                sorted_list = sorted(self.events, key=by_priority)
            elif option == "4":
                sorted_list = sorted(self.events, key=lambda e: not self.events[e].get("starred"))
            elif option == "5":
                sorted_list = sorted(self.events, key=lambda e: not self.events[e].get("pinned"))
            else:
                self._speak("❌ Invalid option.")
                return

            self._speak("Here are your sorted events.")
            for e in sorted_list:
                event = self.events[e]
                self._speak(f"{e} - Date: {event.get('date', '-')}, Priority: {event.get('priority', '-')}")
        except Exception as err:
            self._speak(f"❌ Could not sort events. Error: {err}")

    def set_event_budget(self, name=None, amount=None):
        """
        Sets the overall budget for an event.

        Args:
            name (str, optional): Event name.
            amount (float, optional): Budget amount. If None, prompts user.

        Returns:
            None

        Logic:
            - Updates the event's 'budget' field.
        """
        name, e = self._get_event(name)
        if not e:
            return
        if amount is None:
            amount = self._input_valid_float("Enter budget amount: ")
        self.events[name]["budget"] = amount
        self._speak("Budget updated.")

    def edit_event_budget(self, name=None):
        """
        Edits the budget of an existing event.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Displays current budget and prompts for new amount.
            - Updates event dictionary with the new budget.
        """
        name = name or input("Enter event name: ").lower().strip()
        if name in self.events:
            current = self.events[name].get("budget", 0)
            self._speak(f"Current budget is {current} rupees.")
            self.events[name]["budget"] = self._input_valid_float("New budget: ")
            self._speak("Budget updated.")
        else:
            self._speak("Event not found.")

    def assign_budget_to_task(self, name=None):
        """
        Assigns or updates budget for a specific task in an event.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Prompts user to choose a task and enter a float budget.
            - Validates task index and updates the task's budget.
        """
        name, e = self._get_event(name)
        if not e:
            return

        tasks = e["tasks"]
        if not tasks:
            self._speak("📭 No tasks to assign budget.")
            return

        for i, t in enumerate(tasks, 1):
            self._speak(f"{i}. {t['task']}, ₹{t.get('budget', 0)}")

        index_input = input("Choose task number: ").strip()
        if not index_input.isdigit():
            self._speak("❌ Please enter a valid number.")
            return

        index = int(index_input) - 1
        if index < 0 or index >= len(tasks):
            self._speak("❌ Invalid task number.")
            return

        new_amount = self._input_valid_float("Enter task budget (e.g. 500.00): ")
        if new_amount is None:
            self._speak("❌ Invalid budget input. Aborted.")
            return

        tasks[index]["budget"] = new_amount

        # Check total task budget
        total_task = 0
        for t in tasks:
            try:
                total_task += float(t.get("budget", 0))
            except ValueError:
                continue
        # Warn user if total task budget exceeds the event budget
        if total_task > e.get("budget", 0):
            self._speak("⚠️ Warning: Task budgets exceed the event budget.")

        self._speak("✅ Budget assigned.")

    def view_event_budget_summary(self, name=None):
        """
        Shows a breakdown of event budget usage compared to task budgets.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Sums all task budgets.
            - Compares against event budget.
            - Shows remaining amount or overage.
            - Shows percentage used if event budget > 0.

        Exceptions:
            - Catches and skips task budgets that are invalid (non-float).
        """
        name, e = self._get_event(name)
        if not e:
            return

        total_task = 0
        for t in e["tasks"]:
            try:
                total_task += float(t.get("budget", 0))
            except ValueError:
                self._speak(f"⚠️ Invalid budget in task: {t.get('task', 'Unnamed')}. Skipping.")

        event_budget = e.get("budget", 0)
        remaining = event_budget - total_task

        self._speak(f"Budget summary for {name}")
        self._speak(f"Event Budget: ₹{event_budget}")
        self._speak(f"Task Budget Used: ₹{total_task}")

        if remaining >= 0:
            self._speak(f"Remaining amount is {remaining} rupees. Within budget.")
        else:
            self._speak(f"Over budget by {abs(remaining)} rupees.")

        if event_budget > 0:
            used_percent = int((total_task / event_budget) * 100)
            used_percent = min(used_percent, 999)
            self._speak(f"Usage: {used_percent}%")

    def view_task_budgets_only(self, name=None):
        """
        Displays only the task names and their individual budgets.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Iterates through event tasks and shows each task's budget.
        """
        name, e = self._get_event(name)
        if not e:
            return
        self._speak(f"Task budgets for {name}")
        for t in self.events[name]["tasks"]:
            self._speak(f"{t['task']}: ₹{t.get('budget', 0)}")

    def view_all_event_budgets(self):
        """
        Displays the total budget allocated for each event.

        Args:
            None

        Returns:
            None

        Logic:
            - Iterates over all events and outputs the budget for each.
        """
        self._speak("All event budgets.")
        for name, e in self.events.items():
            self._speak(f"{name}: ₹{e.get('budget', 0)}")

    def upcoming_events(self):
        """
        Lists all events (including recurring ones) happening within the next 7 days.

        Args:
            None

        Returns:
            None

        Logic:
            - Checks each event's date or recurrence pattern.
            - Recursively calculates next occurrence for recurring events.
            - Skips invalid or incomplete entries silently.
        """
        self._speak("Events in the next seven days.")
        today = datetime.date.today()
        found = False

        for name, e in self.events.items():
            try:
                base_date = datetime.datetime.strptime(e["date"], "%Y-%m-%d").date()
                recurrence = e.get("recurrence", {})

                # Check if no recurrence and event is within 7 days
                if not recurrence.get("enabled"):
                    if 0 <= (base_date - today).days <= 7:
                        self._speak(f"{name} on {e['date']}")
                        found = True
                else:
                    # Handle recurrence with frequency and interval
                    freq = recurrence.get("frequency")
                    interval = int(recurrence.get("interval", 1))
                    until = recurrence.get("until")
                    limit_date = datetime.datetime.strptime(until, "%Y-%m-%d").date() if until else (today + datetime.timedelta(days=365))
                    next_date = base_date

                    # Loop through recurrence and check the dates within the 7 days range
                    while next_date <= limit_date:
                        if 0 <= (next_date - today).days <= 7:
                            self._speak(f"{name} (recurring) on {next_date}")
                            found = True
                            break
                        # Advance to the next occurrence based on frequency
                        if freq == "daily":
                            next_date += datetime.timedelta(days=interval)
                        elif freq == "weekly":
                            next_date += datetime.timedelta(weeks=interval)
                        elif freq == "monthly":
                            next_date = self.add_months(next_date, interval)
                        elif freq == "yearly":
                            next_date = self.add_years(next_date, interval)
                        else:
                            break
            except Exception as e:
                # Handle exceptions gracefully
                continue

        if not found:
            self._speak("No upcoming events.")

    def check_task_deadlines(self):
        """
        Checks and lists tasks across all events that are due within the next 3 days.

        Args:
            None

        Returns:
            None

        Logic:
            - Compares each task's deadline to today.
            - Displays tasks with deadlines 0–3 days away.

        Exceptions:
            - Skips tasks with invalid/missing dates silently.
        """
        today = datetime.date.today()
        self._speak("Tasks due in the next three days.")
        found = False
        for name, e in self.events.items():
            for t in e["tasks"]:
                try:
                    # Use the helper method to validate and parse the deadline
                    task_deadline = t.get("deadline", "")
                    if task_deadline:
                        d = datetime.datetime.strptime(task_deadline, "%Y-%m-%d").date()
                        if 0 <= (d - today).days <= 3:
                            self._speak(f"{t['task']} ({name}) due on {task_deadline}")
                            found = True
                except Exception as error:
                    # Log the error for debugging (optional, can be removed in production)
                    continue

        if not found:
            self._speak("No urgent tasks due.")

    def set_reminder(self, name=None, days=None):
        """
        Sets the number of days before the event when a reminder should be triggered.

        Args:
            name (str, optional): Event name.
            days (int, optional): Days before event to remind. If None, prompts user.

        Returns:
            None

        Logic:
            - Ensures reminder is before event date.
            - Accepts only up to 365 days in advance.

        Exceptions:
            - Skips if event date is in the past or invalid.
        """
        name, e = self._get_event(name)
        if not e:
            return

        event_date = self._parse_date(e["date"])
        if not event_date:
            self._speak("❌ Invalid event date.")
            return

        today = datetime.date.today()
        days_until_event = (event_date - today).days
        # Ensure reminder is set within the number of days before the event
        if days_until_event <= 0:
            self._speak("❌ Cannot set a reminder for a past or today's event.")
            return

        max_reminder = min(365, days_until_event)

        if days is None:
            prompt = f"Days before to remind (max {max_reminder}): "
            days = self._input_valid_int(prompt, extra_check=lambda x: 0 <= x <= max_reminder)
            if days is None:
                self._speak("❌ Reminder not set due to invalid input.")
                return
        elif days > max_reminder:
            self._speak(f"❌ Cannot set reminder {days} days before. Event is only {days_until_event} day(s) away.")
            return

        self.events[name]["reminder_days"] = days
        self._speak(f"✅ Reminder set for {days} day(s) before the event.")

    def countdown_to_event(self, name=None):
        """
        Displays how many days are left until an event, or how long ago it happened.

        Args:
            name (str, optional): Event name.

        Returns:
            None

        Logic:
            - Compares today's date to the event date.
            - Gives countdown or elapsed time.
    
        Exceptions:
            - Handles ValueError for bad date format.
        """
        name, e = self._get_event(name)
        if not e:
            return
        try:
            today = datetime.date.today()
            target = datetime.datetime.strptime(self.events[name]["date"], "%Y-%m-%d").date()
        except (KeyError, ValueError) as error:
            self._speak("❌ Invalid date format.")
            return

        days = (target - today).days
        if days > 0:
            self._speak(f"{days} day(s) left until {name}.")
        elif days == 0:
            self._speak(f"{name} is today!")
        else:
            self._speak(f"{name} passed {abs(days)} day(s) ago.")


    def export_to_file(self):
        """
        Exports all events, their details, and tasks into a readable text file.

        Args:
            None

        Returns:
            None

        Output:
            - Creates or overwrites 'events_export.txt' with structured event and task info.

        Logic:
            - Iterates through each event and writes all fields and task details.
            - Supports archived task export as well.

        Exceptions:
            - Logs and reports export failures with exception message.
        """
        if not self.events:
            self._speak("⚠️ No events created. Nothing to export.")
            return

        try:
            with open("events_export.txt", "w", encoding="utf-8") as f:
                for name, e in self.events.items():
                    f.write(f"=== Event: {name.upper()} ===\n")
                    f.write(f"Date: {e.get('date', '-')}\n")
                    f.write(f"Notes: {e.get('notes', '-')}\n")
                    f.write(f"Tags: {', '.join(e.get('tags', []))}\n")
                    f.write(f"Category: {e.get('category', '-')}\n")
                    f.write(f"Priority: {e.get('priority', 'Medium')}\n")
                    f.write(f"Start Time: {e.get('start_time', '-')}\n")
                    f.write(f"End Time: {e.get('end_time', '-')}\n")
                    f.write(f"Pinned: {e.get('pinned', False)}\n")
                    f.write(f"Starred: {e.get('starred', False)}\n")
                    f.write(f"Reminder Days: {e.get('reminder_days', 0)}\n")
                    f.write(f"Budget: ₹{e.get('budget', 0)}\n")

                    # Recurrence
                    rec = e.get("recurrence", {})
                    # Write recurring event info only if enabled
                    if rec.get("enabled"):
                        f.write(f"Recurrence: {rec.get('frequency', '-')} every {rec.get('interval', 1)} until {rec.get('until', 'No end')}\n")
                    else:
                        f.write("Recurrence: None\n")

                    # Tasks
                    f.write("Tasks:\n")
                    tasks = e.get("tasks", [])
                    if tasks:
                        for t in tasks:
                            f.write(f"- {t.get('task', 'Unnamed')} || Status: {t.get('status', 'Pending')} || Deadline: {t.get('deadline', '-')}, Priority: {t.get('priority', 'Medium')}, Budget: ₹{t.get('budget', 0)}\n")
                    else:
                        f.write("- No tasks\n")

                    # Archived Tasks
                    archived = e.get("archived_tasks", [])
                    if archived:
                        f.write("Archived Tasks:\n")
                        for t in archived:
                            f.write(f"- {t.get('task', 'Unnamed')} || Status: {t.get('status', 'Pending')}\n")
                    f.write("\n")  # Space between events

            self._speak("📤 Events exported successfully to 'events_export.txt'.")

        except Exception as ex:
            self._speak("❌ Failed to export events. Error: " + str(ex))

    def get_tasks(self):
        """
        Returns the entire dictionary of events and their contents.

        Args:
            None

        Returns:
            dict: A dictionary of all current events.

        Logic:
            - Basic accessor used for external task saving or manipulation.
        """
        return self.events
