from pyomyo import Myo, emg_mode
from pathlib import Path
from datetime import datetime
import csv
import time
from pynput import keyboard
import termios
import sys

labels = ["flexion", "neutral", "extension", "neutral"]

repetitions = 1
movement_duration = 3
holding_duration = 5

current_label = ""
current_phase = ""
current_repetition = 0

fatigue = 0

# ====================== PARTICIPANT DETAILS ======================

# participant name input
name = input("Hello and welcome! Please enter your name here: ").strip()

# exception handling for no input
if not name:
    raise ValueError("This field cannot be empty.")

# participant filename created based on name input
participant_filename = name.lower().replace(" ", "_")


# ====================== SESSION HANDLING ======================

# folder containing individual session CSV files
session_folder = Path("data/sessions")
session_folder.mkdir(parents=True, exist_ok=True)


# function to get the session number for the participant
def get_session_number(participant_filename):
    # find the participant's session files
    existing_files = session_folder.glob(f"{participant_filename}_session_*.csv")
    session_numbers = []

    for file in existing_files:
        # get session number part from the filename
        # example filename: test_session_01.csv
        session_part = file.stem.split("_session_")[-1]

        try:
            session_numbers.append(int(session_part))
        except ValueError:
            # ignore files with different naming pattern
            continue

    # if this is the participant's first session
    if not session_numbers:
        return 1

    return max(session_numbers) + 1

session_number = get_session_number(participant_filename)

# print name and next session number
print(f"\nParticipant's name: {name}")
print(f"Participant's session number: {session_number}")

# create session's filename   |  test_session_01.csv
session_filename = (session_folder/f"{participant_filename}_session_{session_number:02d}.csv")


# ====================== CSV FUNCTIONS ======================

# data_collection.py headers
dc_headers = ["timestamp", "name", "session", "label", "phase", "repetition", "fatigue",
              "ch_01", "ch_02", "ch_03", "ch_04", "ch_05", "ch_06", "ch_07", "ch_08",]

# function to create csv file for session and add headers
def create_session_csv():
    with open(session_filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(dc_headers)

# function to write complete row to csv file
def write_to_csv(filename, row):
    with open(filename, "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(row)


# ====================== FATIGUE INPUT EVENT LISTENER ======================

# function to get user input for muscle fatigue level
def get_fatigue_input(key):
    global fatigue
    fatigue_levels = ["1", "2", "3", "4", "5"]

    try:
        if key.char in fatigue_levels:
            fatigue = int(key.char)
    except AttributeError:
        # ignore special keys (e.g., shift, ctrl)
        pass


# ====================== RECORD EMG DATA ======================
def record_emg_data(emg, movement):
    # get current timestamp
    timestamp = datetime.now()

    metadata = [timestamp, 
                name, 
                session_number, 
                current_label, 
                current_phase, 
                current_repetition, 
                fatigue]

    # build CSV row 
    row = metadata + list(emg)

    write_to_csv(session_filename, row)


# ====================== TIME FUNCTION ======================

# function to collect data for the specified duration
def collect_for_duration(armband, duration):
    # starting point for measuring time passed
    start_time = time.monotonic()

    # receive EMG samples until duration passed
    while time.monotonic() - start_time <= duration:
        armband.run()


# ====================== DATA COLLECTION ======================

# function to collect data for each wrist position
def dc_wrist_position(armband):
    global current_label
    global current_phase
    global current_repetition

    # set starting position for participant
    print("\nPlease place your hand in a neutral position.")
    # participant starts session by pressing ENTER
    input("Press ENTER when you are ready to start.")


    # =========== DISABLE TERMINAL ECHO ===========
    """
    https://docs.python.org/3/library/termios.html
    https://gist.github.com/kgriffs/5726314
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    new_settings = termios.tcgetattr(fd)
    new_settings[3] = new_settings[3] & ~termios.ECHO

    try:
        termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)

        with keyboard.Listener(on_press=get_fatigue_input) as listener:

            # repeat for the specified number of repeptitions
            for repetition in range(1, repetitions + 1):    # range(inclusive, exclusive)
                current_repetition = repetition

                # display repetition information
                print(f"\nRepetition {current_repetition} of {repetitions}")

                # go through each wrist position
                for label in labels:
                    # update current wrist position label
                    current_label = label

                    # =========== MOVING ===========
                    # update the current phase
                    current_phase = "moving"

                    # participant movement instructions
                    print(f"Please CHANGE to {current_label}. ({movement_duration} seconds)")

                    # collect movement data
                    collect_for_duration(armband, movement_duration)

                    # =========== HOLDING ===========
                    # update the current phase
                    current_phase = "holding"

                    # participant instructions for holding
                    print(f"Please HOLD {current_label} ({holding_duration} seconds)")

                    # collect holding data
                    collect_for_duration(armband, holding_duration)

            # participant instructions when all repetitions are complete
            print("\nData collection complete.")

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# ====================== MAIN FUNCTION ======================
def main():
    # create session CSV
    create_session_csv()
    print(f"Created: {session_filename}")

    armband = Myo(mode=emg_mode.RAW)
    armband.connect()

    armband.add_emg_handler(record_emg_data)

    try:
        dc_wrist_position(armband)

    # stop the program with Ctrl+C
    except KeyboardInterrupt:
        print("\nData collection interrupted.")

    # without this Myo armband never turns off
    finally:
        armband.disconnect()
        print("Myo armband disconnected.")
        

if __name__ == "__main__":
    main()