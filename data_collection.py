from pyomyo import Myo, emg_mode
from pathlib import Path
from datetime import datetime
import csv
import time
import myo

labels = ["flexion", "neutral", "extension"]

repetitions = 10
movement_duration = 5
holding_duration = 5

current_label = ""
current_phase = ""
current_repetition = 0

rawdata = []

# ====================== PARTICIPANT DETAILS

# participant name input
name = input("Hello and welcome! Please enter your name here: ").strip()

# exception handling for no input
if not name:
    raise ValueError("This field cannot be empty.")

# participant filename created based on name input
participant_filename = name.lower().replace(" ", "_")

# ========================================================================================
