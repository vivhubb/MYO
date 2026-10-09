import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
from pathlib import Path
import csv
from pygame_widgets.button import Button
import time

# initialize pygame
pygame.init()

clock = pygame.time.Clock()

# =========== SCREEN ===========
# set screen width and height
screen_width = 1200
screen_height = 700
# pygame display size setup
screen = pygame.display.set_mode((screen_width, screen_height))
# set window title
pygame.display.set_caption("MYO Project")

# =========== VARIABLES ===========
running = True
error_message = ""

current_screen = "questionnaire"

labels = ["flexion", "neutral", "extension", "neutral"]
label_index = 0
repetition = 1

movement_duration = 3
holding_duration = 5

current_label = ""
current_phase = ""
current_repetition = 0

start_time = None

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
id_textbox = TextBox(screen, 50, 100, 50, 32, font=text_font_medium, placeholderText="ID",
                  borderColour=(255,255,255), radius=8, borderThickness=2)
age_textbox = TextBox(screen, 50, 180, 50, 32, font=text_font_medium, placeholderText="Age",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
gender_textbox = TextBox(screen, 50, 260, 200, 32, font=text_font_medium, placeholderText="Gender",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
height_textbox = TextBox(screen, 50, 340, 150, 32, font=text_font_medium, placeholderText="Height (cm)",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
weight_textbox = TextBox(screen, 50, 420, 150, 32, font=text_font_medium, placeholderText="Weight (kg)",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
wrist_textbox = TextBox(screen, 50, 500, 210, 32, font=text_font_medium, placeholderText="Wrist Circumference (cm)",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
forearm_textbox = TextBox(screen, 50, 580, 200, 32, font=text_font_medium, placeholderText="Forearm Length (cm)",
                    borderColour=(255,255,255), radius=8, borderThickness=2)

# =========== COLORS ===========
black = (0, 0, 0)
white = (255, 255, 255)
grey = (194, 197, 204)

# =========== CSV FOLDERS ===========
# folder containing participant CSV file
participant_folder = Path("data/participants")
participant_folder.mkdir(parents=True, exist_ok=True)

# =========== CSV FILES ===========
# participant csv file
participant_filename = participant_folder/"participants_data.csv"

# =========== CSV ===========
# participant CSV headers
p_headers = ["participant_ID", "age", "gender", "height", "weight", "wrist_circumference", "forearm_length"]

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

# =========== INPUT VALIDATION ===========
def validate_input(text):
    return text.strip() != ""

def validate_all_inputs():
    global error_message, current_screen
    textboxes = [id_textbox, age_textbox, gender_textbox, height_textbox, weight_textbox, wrist_textbox, forearm_textbox]

    row = [
        id_textbox.getText(),
        age_textbox.getText(),
        gender_textbox.getText(),
        height_textbox.getText(),
        weight_textbox.getText(),
        wrist_textbox.getText(),
        forearm_textbox.getText()
    ]

    for answer in row:
        if not validate_input(answer):
            error_message = "**Please fill in all the fields before submitting!"
            return 

    write_to_csv(row)

    for widget in textboxes:        
        widget.hide()
        button.hide()

    current_screen = "data collection start"

# =========== HELPER FUNCITON ===========
'''
https://www.youtube.com/watch?v=ndtFoWWBAoE
'''
# display text as image helper function
def display_text(text, font, text_color, x, y):
    image = font.render(text, True, text_color)
    screen.blit(image, (x, y))

# =========== FUNCTION CALLS ===========
# create participant csv if it doesn't exist
if not participant_filename.exists():
    create_participant_csv()

# =========== BUTTON ===========
'''
https://pygamewidgets.readthedocs.io/en/stable/widgets/button/
'''
button = Button(screen, 50, 650, 100, 32, 
                text='Submit', font=text_font_medium, 
                radius=8, borderThickness=2,
                inactiveColour=grey, 
                hoverColour=pygame.Color('mediumseagreen'), 
                pressedColour=pygame.Color('mediumseagreen'),
                onClick=validate_all_inputs)


# =========== IMAGES ===========
neutral_image = pygame.image.load("media/pictures/neutral.png")
extension_image = pygame.image.load("media/pictures/extension.png")
flexion_image = pygame.image.load("media/pictures/flexion.png")

# =========== MAIN LOOP ===========
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
                    current_screen = "data collection"
                    label_index = 0
                    current_label = labels[label_index]
                    current_phase = "moving"
                    current_repetition = 1
                    start_time = time.monotonic()

    if current_screen == "data collection":
        elapsed_time = time.monotonic() - start_time

        if current_phase == "moving":
            if elapsed_time >= movement_duration:
                current_phase = "holding"
                start_time = time.monotonic()

        elif current_phase == "holding":
            if elapsed_time >= holding_duration:
                label_index += 1

                if label_index < len(labels):
                    current_label = labels[label_index]
                    current_phase = "moving"
                    start_time = time.monotonic()
                else:
                    current_screen = "data collection complete"

    if current_screen == "questionnaire":
    
        # display welcome text on the screen
        display_text(welcome_text, text_font_big, pygame.Color('blanchedalmond'), 50, 25)

        '''
        https://www.youtube.com/watch?v=Rvcyf4HsWiw
        '''
        # display get participant ID prompt on the screen
        id_text_surface = text_font_medium.render(p_id_prompt, True, white)
        screen.blit(id_text_surface, (50, 75))

        # display get participant age prompt on the screen
        age_text_surface = text_font_medium.render(p_age_prompt, True, white)
        screen.blit(age_text_surface, (50, 155))

        # display get participant gender prompt on the screen
        gender_text_surface = text_font_medium.render(p_gender_prompt, True, white)
        screen.blit(gender_text_surface, (50, 235))

        # display get participant height prompt on the screen
        height_text_surface = text_font_medium.render(p_height_prompt, True, white)
        screen.blit(height_text_surface, (50, 315))

        # display get participant weight prompt on the screen
        weight_text_surface = text_font_medium.render(p_weight_prompt, True, white)
        screen.blit(weight_text_surface, (50, 395))

        # display get participant wrist circumference prompt on the screen
        wrist_text_surface = text_font_medium.render(p_wrist_prompt, True, white)
        screen.blit(wrist_text_surface, (50, 475))

        # display get participant forearm length prompt on the screen
        forearm_text_surface = text_font_medium.render(p_forearm_prompt, True, white)
        screen.blit(forearm_text_surface, (50, 555))

        display_text(error_message, text_font_medium, pygame.Color('red'), 175, 655)

    elif current_screen == "data collection start":
        display_text("Please place your hand in a NEUTRAL position and follow the instructions on the screen.", text_font_big, pygame.Color('blanchedalmond'), 50, 25)
        screen.blit(neutral_image, (50, 100))
        display_text("Press ENTER to continue.", text_font_medium, pygame.Color('blanchedalmond'), 50, 600)

    elif current_screen == "data collection":
        if current_phase == "moving":
            prompt = (f"Please CHANGE to {current_label.upper()} (3 seconds).")
        else:
            prompt = (f"Please HOLD {current_label.upper()} (5 seconds).")

        if current_label == "flexion":
            current_image = flexion_image
        elif current_label == "neutral":
            current_image = neutral_image
        elif current_label == "extension":
            current_image = extension_image

        display_text(prompt, text_font_big, pygame.Color('blanchedalmond'), 50, 25)
        display_text(f'Repetition: {current_repetition}', text_font_medium, white, 1000, 25)
        screen.blit(current_image, (50, 75))

    else:
        current_screen == "data collection complete"


    # update the textboxes and button
    pygame_widgets.update(events)

    pygame.display.flip()
    clock.tick(60)

# quit the program
pygame.quit()