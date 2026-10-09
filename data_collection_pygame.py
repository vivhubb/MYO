import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
from pathlib import Path
import csv
from pygame_widgets.button import Button
import time
from pyomyo import Myo, emg_mode
from datetime import datetime

# initialize pygame
pygame.init()

# clock to control the frame rate
clock = pygame.time.Clock()

# =========== SCREEN ===========
# set screen width and height
screen_width = 1200
screen_height = 700
# pygame display size setup
screen = pygame.display.set_mode((screen_width, screen_height))
# set window title
pygame.display.set_caption("MYO Project")

# set the starting screen
current_screen = "welcome"

# =========== VARIABLES ===========
running = True
error_message = ""

labels = ["flexion", "neutral", "extension", "neutral"]
label_index = 0

repetitions = 2

movement_duration = 3
holding_duration = 5

current_label = ""
current_phase = ""
current_repetition = 0

start_time = None

participant_id = ""

session_number = 0
session_csvfile = None
session_writer = None

# =========== FONT ===========
text_font_big = pygame.font.SysFont("robotoserif.ttf", 36, italic=True)
text_font_medium = pygame.font.SysFont("robotoserif.ttf", 24)

# =========== TEXT ===========
welcome_text = "Hello and Welcome! Thank you for participating in this study."
p_id_prompt = "Please enter your assigned Participant ID in the box below."
p_age_prompt = "Please enter your Age in the box below."
p_gender_prompt = "Please enter your Gender in the box below."
p_height_prompt = "Please enter your Height (cm) in the box below."
p_weight_prompt = "Please enter your Weight (kg) in the box below."
p_wrist_prompt = "Please enter your Wrist Circumference (cm) in the box below."
p_forearm_prompt = "Please enter your Forearm Length (cm) in the box below."

# =========== TEXTBOX ===========
id_textbox = TextBox(screen, 50, 175, 50, 32, font=text_font_medium, placeholderText="ID",
                  borderColour=(255,255,255), radius=8, borderThickness=2)
age_textbox = TextBox(screen, 50, 110, 50, 32, font=text_font_medium, placeholderText="Age",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
gender_textbox = TextBox(screen, 50, 190, 200, 32, font=text_font_medium, placeholderText="Gender",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
height_textbox = TextBox(screen, 50, 270, 150, 32, font=text_font_medium, placeholderText="Height (cm)",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
weight_textbox = TextBox(screen, 50, 350, 150, 32, font=text_font_medium, placeholderText="Weight (kg)",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
wrist_textbox = TextBox(screen, 50, 430, 210, 32, font=text_font_medium, placeholderText="Wrist Circumference (cm)",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
forearm_textbox = TextBox(screen, 50, 510, 200, 32, font=text_font_medium, placeholderText="Forearm Length (cm)",
                    borderColour=(255,255,255), radius=8, borderThickness=2)

questionnaire_textboxes = [age_textbox, gender_textbox, height_textbox, weight_textbox, wrist_textbox, forearm_textbox]

# hide questionnaire textboxes on the welcome screen
for widget in questionnaire_textboxes:
    widget.hide()

# =========== COLORS ===========
black = (0, 0, 0)
white = (255, 255, 255)
grey = (194, 197, 204)

# =========== CSV FOLDERS ===========
# folder containing participant CSV file
participant_folder = Path("data/participants")
participant_folder.mkdir(parents=True, exist_ok=True)

# folder containing individual session CSV files
session_folder = Path("data/sessions")
session_folder.mkdir(parents=True, exist_ok=True)

# =========== CSV FILES ===========
# participant csv file
participant_filename = participant_folder/"participants_data.csv"

# =========== CSV ===========
# participant CSV headers
p_headers = ["participant_id", "age", "gender", "height", "weight", "wrist_circumference", "forearm_length"]
dc_headers = ["timestamp", "participant_id", "session", "label", "phase", "repetition",
              "ch_01", "ch_02", "ch_03", "ch_04", "ch_05", "ch_06", "ch_07", "ch_08",]

# function to create and open participant CSV
def create_participant_csv():
    with open(participant_filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        # write headers to the CSV file
        csv_writer.writerow(p_headers)
        print(f"Created: {participant_filename}")

# function to write complete row to csv file
def write_csv_row(csv_writer, row):
    csv_writer.writerow(row)

# function to write participant data to csv file
def write_to_csv(row):
    with open(participant_filename, "a", newline="") as csvfile:
        write_csv_row(csv.writer(csvfile), row)

# function to get the next session number for the participant
def get_session_number(participant_id):
    # find the participant's session files
    existing_files = session_folder.glob(f"{participant_id}_session_*.csv")
    session_numbers = []

    for file in existing_files:
        # get session number part from the filename
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

# function to create an dopen session CSV
def open_session_csv():
    global participant_id, session_number, session_csvfile, session_writer

    participant_id = id_textbox.getText().strip()

    session_number = get_session_number(participant_id)

    # create session's filename
    session_filename = (session_folder/f"{participant_id}_session_{session_number:02d}.csv")

    # create new file without overwriting existing session
    session_csvfile = open(session_filename, "x", newline="")
    session_writer = csv.writer(session_csvfile)
    session_writer.writerow(dc_headers)

# funtion to close session CSV
def close_session_csv():
    global session_csvfile, session_writer

    if session_csvfile is not None:
        session_csvfile.close()
        session_csvfile = None
        session_writer = None

# function to record EMG data with current session details
def record_emg_data(emg, movement, csv_writer):
    # get current timestamp
    timestamp = datetime.now()

    metadata = [timestamp, participant_id, session_number, current_label, current_phase, current_repetition]

    # build CSV row 
    row = metadata + list(emg)
    write_csv_row(csv_writer, row)

# wrapper function to pass the csv_writer to the record_emg_data function
def wrapper(emg, movement):
    if current_screen == "data collection":
        record_emg_data(emg, movement, session_writer)

# =========== MYO ===========
myo = Myo(mode=emg_mode.RAW)
myo.add_emg_handler(wrapper)
myo_connected = False

# =========== INPUT VALIDATION ===========
# function to check for no input
def validate_input(text):
    return text.strip() != ""

# function to validate and save questionnaire answers
def validate_all_inputs():
    global error_message, current_screen
    textboxes = [id_textbox, age_textbox, gender_textbox, height_textbox, weight_textbox, wrist_textbox, forearm_textbox]

    row = [
        id_textbox.getText().strip(),
        age_textbox.getText(),
        gender_textbox.getText(),
        height_textbox.getText(),
        weight_textbox.getText(),
        wrist_textbox.getText(),
        forearm_textbox.getText()
    ]

    # check if there are any empty fields before submitting
    for answer in row:
        if not validate_input(answer):
            error_message = "**Please fill in all the fields before submitting!"
            return 

    write_to_csv(row)
    error_message = ""

    # hide questionnaire widgets
    for widget in textboxes:        
        widget.hide()
        submit_button.hide()

    current_screen = "data collection start"

# =========== HELPER FUNCITONS ===========
'''
https://www.youtube.com/watch?v=ndtFoWWBAoE
'''
# display text as image helper function
def display_text(text, font, text_color, x, y):
    image = font.render(text, True, text_color)
    screen.blit(image, (x, y))

# function to check if entered ID is already participant csv
def id_exists(entered_id):
    with open(participant_filename, "r", newline="") as csvfile:
        # read participant rows using CSV headers and Dictionary keys
        reader = csv.DictReader(csvfile)

        for participant in reader:
            # check if entered participant id is found in csv
            if participant["participant_id"].strip() == entered_id:
                return True
            
    return False

# function to decide which screen to show after checking if ID exists
def show_questionnaire():
    global current_screen, error_message

    entered_id = id_textbox.getText().strip()

    # makes sure ID field is not empty
    if not entered_id:
        error_message = "Please enter your assigned Participant ID."

        return

    error_message = ""
    id_textbox.hide()
    continue_button.hide()

    # existing participants will skip the questionnaire
    if id_exists(entered_id):
        current_screen = "data collection start"
    else:
        # shows questionnaire widgets for new participants
        for widgets in questionnaire_textboxes:
            widgets.show()

        submit_button.show()
        current_screen = "questionnaire"

# =========== FUNCTION CALLS ===========
# create participant csv if it doesn't exist
if not participant_filename.exists():
    create_participant_csv()

# =========== BUTTON ===========
'''
https://pygamewidgets.readthedocs.io/en/stable/widgets/button/
'''
submit_button = Button(screen, 50, 650, 100, 32, 
                text='Submit', font=text_font_medium, 
                radius=8, borderThickness=2,
                inactiveColour=grey, 
                hoverColour=pygame.Color('mediumseagreen'), 
                pressedColour=pygame.Color('mediumseagreen'),
                onClick=validate_all_inputs)

# hide button until questionnaire screen
submit_button.hide()

continue_button = Button(screen, 50, 650, 100, 32, 
                text='Continue', font=text_font_medium, 
                radius=8, borderThickness=2,
                inactiveColour=grey, 
                hoverColour=pygame.Color('mediumseagreen'), 
                pressedColour=pygame.Color('mediumseagreen'),
                onClick=show_questionnaire)

# =========== IMAGES ===========
neutral_image = pygame.image.load("media/pictures/neutral.png")
extension_image = pygame.image.load("media/pictures/extension.png")
flexion_image = pygame.image.load("media/pictures/flexion.png")

# =========== MAIN LOOP ===========
try:
    # main loop
    while running:
        # fill the screen with black color
        screen.fill(black)
        # get all the events that have occurred since the last frame
        events = pygame.event.get()
        
        for event in events:
            # if user clicks X to close the pygame window
            if event.type == pygame.QUIT:
                running = False
            if current_screen == "data collection start":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        try:
                            myo.connect()
                            myo_connected = True
                            open_session_csv()
                        except Exception as error:
                            error_message = f"Error collecting data: {error}"
                            # close file if session failed
                            close_session_csv()

                            # disconnect before another attempt
                            if myo_connected:
                                myo.disconnect()
                                myo_connected = False
                        else:
                            error_message = ""

                            current_screen = "data collection"
                            label_index = 0
                            current_label = labels[label_index]
                            current_phase = "moving"
                            current_repetition = 1
                            start_time = time.monotonic()

        if current_screen == "data collection":
            elapsed_time = time.monotonic() - start_time

            if current_phase == "moving":
                # switch to holding when when movement duration ends
                if elapsed_time >= movement_duration:
                    current_phase = "holding"
                    start_time = time.monotonic()

            elif current_phase == "holding":
                # change hand position when holding duration ends
                if elapsed_time >= holding_duration:
                    label_index += 1

                    if label_index >= len(labels):
                        if current_repetition < repetitions:
                            current_repetition += 1
                            label_index = 0
                        else:
                            # go to final screen when repetitions end
                            current_screen = "data collection complete"

                            # close session csv 
                            close_session_csv()

                    if current_screen == "data collection":
                        current_label = labels[label_index]
                        current_phase = "moving"
                        start_time = time.monotonic()

        if current_screen == "data collection" and myo_connected:
            myo.run()

        if current_screen == "welcome":
            # display welcome text on the screen
            display_text(welcome_text, text_font_big, pygame.Color('blanchedalmond'), 200, 25)

            # display get participant ID prompt on the screen
            id_text_surface = text_font_medium.render(p_id_prompt, True, white)
            screen.blit(id_text_surface, (50, 150))

            # display input error message
            display_text(error_message, text_font_medium, pygame.Color('red'), 175, 655)

            
        elif current_screen == "questionnaire":
            '''
            https://www.youtube.com/watch?v=Rvcyf4HsWiw
            '''
            
            # display get participant age prompt on the screen
            age_text_surface = text_font_medium.render(p_age_prompt, True, white)
            screen.blit(age_text_surface, (50, 75))

            # display get participant gender prompt on the screen
            gender_text_surface = text_font_medium.render(p_gender_prompt, True, white)
            screen.blit(gender_text_surface, (50, 155))

            # display get participant height prompt on the screen
            height_text_surface = text_font_medium.render(p_height_prompt, True, white)
            screen.blit(height_text_surface, (50, 235))

            # display get participant weight prompt on the screen
            weight_text_surface = text_font_medium.render(p_weight_prompt, True, white)
            screen.blit(weight_text_surface, (50, 315))

            # display get participant wrist circumference prompt on the screen
            wrist_text_surface = text_font_medium.render(p_wrist_prompt, True, white)
            screen.blit(wrist_text_surface, (50, 395))

            # display get participant forearm length prompt on the screen
            forearm_text_surface = text_font_medium.render(p_forearm_prompt, True, white)
            screen.blit(forearm_text_surface, (50, 475))

            display_text(error_message, text_font_medium, pygame.Color('red'), 175, 655)

        elif current_screen == "data collection start":
            display_text("Please place your hand in a NEUTRAL position and follow the instructions on the screen.", 
                        text_font_big, pygame.Color('blanchedalmond'), 50, 25)
            screen.blit(neutral_image, (50, 100))
            display_text("Press ENTER to continue.", 
                        text_font_medium, pygame.Color('blanchedalmond'), 50, 600)
            # myo error message
            display_text(error_message, text_font_medium, pygame.Color('red'), 50, 640)

        elif current_screen == "data collection":
            # display prompt based on current phase
            if current_phase == "moving":
                prompt = (f"Please CHANGE to {current_label.upper()} (3 seconds).")
            else:
                prompt = (f"Please HOLD {current_label.upper()} (5 seconds).")

            # display image based on current label
            if current_label == "flexion":
                current_image = flexion_image
            elif current_label == "neutral":
                current_image = neutral_image
            elif current_label == "extension":
                current_image = extension_image

            display_text(prompt, text_font_big, pygame.Color('blanchedalmond'), 50, 25)
            display_text(f'Repetition: {current_repetition} of {repetitions}', 
                        text_font_medium, white, 1000, 25)
            screen.blit(current_image, (50, 75))

        elif current_screen == "data collection complete":
            display_text("Data collection complete. Thank you for participating!", 
                        text_font_big, pygame.Color('blanchedalmond'), 250, 200)
            display_text("You may now close the program window.", 
                        text_font_medium, pygame.Color('blanchedalmond'), 50, 500)

        # update the textboxes and button
        pygame_widgets.update(events)

        pygame.display.flip()
        clock.tick(60)

except KeyboardInterrupt:
    print("Data collection interrupted.")

finally:
    try:
        if myo_connected:
            # disconnect myo - does not turn it off
            myo.disconnect()
            print("Myo disconnected.")
    finally:
        try:
            close_session_csv()
        finally:
            # quit the program
            pygame.quit()
