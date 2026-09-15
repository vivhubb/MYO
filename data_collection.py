from pyomyo import Myo, emg_mode
from pathlib import Path
from datetime import datetime
import csv
import time
import threading

labels = ["flexion", "neutral", "extension", "neutral"]

repetitions = 10
movement_duration = 3
holding_duration = 5

current_label = ""
current_phase = ""
current_repetition = 0

fatigue = 0
recording = False

# prevents data from being read and changed at the same time
data_lock = threading.Lock()

# ====================== PARTICIPANT DETAILS ======================

# participant name input
name = input("\nHello and welcome! Please enter your name here: ").strip()

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


# ====================== PARTICIPANT FATIGUE INPUT ======================

# function to get user input for muscle fatigue level
def get_fatigue_input():
    fatigue = int(
        input("\nPlease enter your muscle fatigue level (1 - 5): ")
        )

    # input validation for out of range fatigue input
    if fatigue not in range(1,6):
        raise ValueError(
            "Your fatigue number input has to be between 1 and 5."
            )

    return fatigue


# ====================== MYO THREAD FUNCTION ======================
# function to continuously receive data from myo
def run_myo(armband, stop_event):
    # keep receiving data until thread is stopped
    while not stop_event.is_set():
        armband.run()


# ====================== RECORD EMG DATA ======================
def record_emg_data(emg, movement):
    # lock current information while building metadata
    with data_lock:
        # only record data if recording is turned on
        if not recording:
            return
        
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
    # write row to CSV
    write_to_csv(session_filename, row)


# ====================== TIME FUNCTION ======================

# function to collect data for the specified duration
def collect_for_duration(duration):
    # wait for the specified duration
    time.sleep(duration)


# ====================== DATA COLLECTION ======================

# function to collect data for each wrist position
def dc_wrist_position():
    global current_label
    global current_phase
    global current_repetition
    global fatigue
    global recording

    # turn recording off during input
    with data_lock:
        recording = False

    # set starting position for participant
    print("\nPlease place your hand in a neutral position.")
    # participant starts session by pressing ENTER
    input("Press ENTER when you are ready to start.")

    # repeat for the specified number of repeptitions
    for repetition in range(1, repetitions + 1):    # range(inclusive, exclusive)

        # turn recording off during input and update repetition
        with data_lock:
            recording = False
            current_repetition = repetition

        # get fatigue level input for current repetition
        new_fatigue = get_fatigue_input()

        # participant to return to neutral after fatigue input
        print("Please place your hand back to neutral position")
        time.sleep(movement_duration)

        # update fatigue level for current repetition
        with data_lock:
            fatigue = new_fatigue

        # display repetition information
        print(f"\nRepetition {current_repetition} of {repetitions}")

        # go through each wrist position
        for label in labels:

            # update current information before movement
            with data_lock:
                recording = False
                current_label = label
                current_phase = "moving"

            # =========== MOVING ===========

            # participant movement instructions
            print(f"Please CHANGE to {current_label} (3 seconds).")

            # turn recording on
            with data_lock:
                recording = True

            # collect movement data
            collect_for_duration(movement_duration)

            # update current information before holding phase
            with data_lock:
                recording = False
                current_phase = "holding"

            # =========== HOLDING ===========

            # participant instructions for holding
            print(f"Please HOLD {current_label} (5 seconds).")

            # turn recording on
            with data_lock:
                recording = True

            # collect holding data
            collect_for_duration(holding_duration)

        # turn recording off before next fatigue input
        with data_lock:
            recording = False

    # makes sure recording is off when collection is complete
    with data_lock:
        recording = False

    # participant instructions when all repetitions are complete
    print("\nThank you. Data collection is now complete.")


# ====================== MAIN FUNCTION ======================
def main():
    global recording

    # create session CSV
    create_session_csv()
    print(f"Created: {session_filename}")

    # create and connect myo armband
    armband = Myo(mode=emg_mode.RAW)
    armband.connect()

    # send incoming EMG samples to the record_emg_data function
    armband.add_emg_handler(record_emg_data)

    # event used to stop myo thread
    stop_event = threading.Event()

    # create myo background thread
    myo_thread = threading.Thread(target=run_myo, args=(armband, stop_event))

    try:
        # start receiving myo data in the background
        myo_thread.start()

        # start data collection
        dc_wrist_position()

    # stop the program with Ctrl+C
    except KeyboardInterrupt:
        print("\nData collection interrupted.")

    # stop thread, disconnect and turn myo off
    finally:
        # stop recording data
        with data_lock:
            recording = False

        # stop myo armband thread
        stop_event.set()    # change stop event to true
        myo_thread.join()   # wait until myo thread stops

        # disconnect armband
        armband.disconnect()
        print("\nMyo armband disconnected.")
        

if __name__ == "__main__":
    main()