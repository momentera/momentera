try:
    import pyttsx3
except ImportError:
    pyttsx3 = None  # If not installed, disable voice functionality

#File where user-specific voice settings are stored in the format:
#username:enabled,rate,volume,voice_index
VOICE_FILE = "voice_settings.txt"

def speak(text, settings):
    """
    Speaks a given text using pyttsx3 if enabled in settings.

    Args:
        text (str): The message to speak.
        settings (dict): Voice settings (enabled, rate, volume, voice_index).

    Returns:
        None

    Logic:
        - Initializes pyttsx3 engine.
        - Applies rate, volume, and voice index.
        - Outputs speech using system TTS.
    
    Exceptions:
        - Catches and logs pyttsx3 engine errors.
    """
    print(text)
    if not pyttsx3 or not settings.get("enabled", False):
        return
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', settings.get("rate", 150))
        engine.setProperty('volume', settings.get("volume", 1.0))
        voices = engine.getProperty('voices')
        index = settings.get("voice_index", 0)
        if 0 <= index < len(voices):
            engine.setProperty('voice', voices[index].id)
        engine.say(text)
        engine.runAndWait()
    except pyttsx3.EngineError:
        print("🔇 Voice output failed due to engine error.")
    except Exception as e:
        print(f"🔇 Voice output failed: {str(e)}")

def load_voice_settings(username):
    """
    Loads voice settings for a specific user from the settings file.

    Args:
        username (str): The username whose settings to load.

    Returns:
        dict: Voice settings with keys:
            - enabled (bool)
            - rate (int)
            - volume (float)
            - voice_index (int)

    Logic:
        - Returns default settings if file not found or username not present.
        - Defaults used for None usernames.
    """
    settings = {"enabled": False, "rate": 150, "volume": 1.0, "voice_index": 0}
    
    # If username is None, return the default settings
    if username is None:
        return settings

    try:
        with open(VOICE_FILE, 'r') as file:
            for line in file:
                if line.startswith(username + ":"):
                    parts = line.strip().split(":")[1].split(",")
                    return {
                        "enabled": parts[0] == "True",
                        "rate": int(parts[1]),
                        "volume": float(parts[2]),
                        "voice_index": int(parts[3])
                    }
    except FileNotFoundError:
        print("Voice settings file not found. Using default settings.")
        pass  # No voice settings file, using defaults
    except Exception as e:
        print(f"Error loading voice settings: {e}")

    return settings  # Return default settings if no match is found

def save_voice_settings(username, settings):
    """
    Saves or updates a user’s voice settings in the file.

    Args:
        username (str): Username whose settings to save.
        settings (dict): Voice configuration.

    Returns:
        None

    Exceptions:
        - Creates file if not present.
        - Logs error if writing fails.
    """
    # If username is None, don't save any settings
    if username is None:
        return

    updated_lines = []
    found = False
    try:
        with open(VOICE_FILE, 'r') as file:
            for line in file:
                if line.startswith(username + ":"):
                    line = username + ":" + ",".join([  # Update settings for this user
                        str(settings.get("enabled", False)),
                        str(settings.get("rate", 150)),
                        str(settings.get("volume", 1.0)),
                        str(settings.get("voice_index", 0))
                    ]) + "\n"
                    found = True
                updated_lines.append(line)
    except FileNotFoundError:
        print(f"{VOICE_FILE} not found. Creating a new file.")
        pass  # If the file doesn't exist, it will be created below

    if not found:  # Add new settings for this user if not found
        updated_lines.append(username + ":" + ",".join([
            str(settings.get("enabled", False)),
            str(settings.get("rate", 150)),
            str(settings.get("volume", 1.0)),
            str(settings.get("voice_index", 0))
        ]) + "\n")

    try:
        with open(VOICE_FILE, 'w') as file:
            file.writelines(updated_lines)
        print("✅ Voice settings saved.")
        speak("Voice settings saved successfully.", settings)  # Optional
    except IOError:
        print("Error saving voice settings.")
        speak("Error saving voice settings.", settings)  # Added feedback for save failure

def configure_voice_settings(username, settings):
    """
    Interactive CLI interface to update voice settings.

    Args:
        username (str): Username to apply changes to.
        settings (dict): Current voice settings.

    Returns:
        dict or None: Updated voice settings if saved, else None.

    Logic:
        - Asks user to toggle voice, change rate, volume, and choose voice index.
        - Applies changes temporarily.
        - Confirms before saving changes.
    
    Exceptions:
        - Handles invalid user inputs and index errors gracefully.
    """
    speak("\n🎙️ Voice Settings", settings)
    temp_settings = settings.copy()
    speak("Voice Settings", temp_settings)

    current = "enabled" if settings["enabled"] else "disabled"
    speak("Voice currently: " + current, temp_settings)

    speak("Would you like to turn voice on or off?", temp_settings)
    toggle = input("Turn voice ON or OFF? (on/off or 'cancel'): ").strip().lower()

    if toggle == "cancel":
        speak("❌ Cancelled voice settings.", temp_settings)
        return None
    elif toggle not in ["on", "off"]:
        speak("❌ Invalid choice. Please try again.", temp_settings)
        return None

    new_settings = settings.copy()
    new_settings["enabled"] = (toggle == "on")
    temp_settings["enabled"] = new_settings["enabled"]

    if new_settings["enabled"]:
        speak("Let's configure your voice settings.", temp_settings)

        # Ask for rate
        speak(f"Set rate between 100 and 300. Current rate is {new_settings['rate']}.", temp_settings)
        rate = input(f"Set rate (100-300, current is {new_settings['rate']}): ").strip()
        if rate.isdigit():
            new_settings["rate"] = int(rate)
            speak("Speech rate set to " + rate, temp_settings)
        else:
            speak("Invalid rate input. Keeping default rate.", temp_settings)

        # Ask for volume
        speak(f"Set volume between 0.0 and 1.0. Current volume is {new_settings['volume']}.", temp_settings)
        volume = input(f"Set volume (0.0 to 1.0, current is {new_settings['volume']}): ").strip()
        try:
            vol = float(volume)
            if 0.0 <= vol <= 1.0:
                new_settings["volume"] = vol
                speak("Volume set to " + volume, temp_settings)
            else:
                speak("Volume out of range. Keeping default.", temp_settings)
        except ValueError:
            speak("Invalid volume input. Keeping default.", temp_settings)

        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            speak("Available voices:", temp_settings)
            for i, v in enumerate(voices):
                speak(f"{i}: {v.name}", temp_settings)
            speak("Choose your preferred voice index.", temp_settings)

            vi = input(f"Choose voice index (current is {new_settings['voice_index']}): ").strip()
            if vi.isdigit() and int(vi) < len(voices):
                new_settings["voice_index"] = int(vi)
                speak("Voice changed to index " + vi, temp_settings)
            else:
                speak("Invalid voice index. Keeping current.", temp_settings)
        except Exception as e:
            speak(f"Error listing voices: {e}", temp_settings)
            speak("Error listing voices. Skipping this step.", temp_settings)

    speak("Do you want to save these voice settings?", temp_settings)
    confirm = input("Overwrite your voice settings? (y/n): ").strip().lower()
    if confirm not in ["y", "yes"]:
        speak("❌ Voice settings not saved.", temp_settings)
        return None

    if username:
        save_voice_settings(username, new_settings)
    else:
        speak("✅ Voice settings saved for this session.", temp_settings)

    return new_settings
