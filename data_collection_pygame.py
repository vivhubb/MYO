import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
from pathlib import Path
import csv
from pygame_widgets.button import Button

# initialize pygame
pygame.init()

# set screen width and height
screen_width = 1200
screen_height = 700
# pygame display size setup
screen = pygame.display.set_mode((screen_width, screen_height))
# set window title
pygame.display.set_caption("Data Collection")

clock = pygame.time.Clock()

running = True

# =========== FONT ===========
text_font_big = pygame.font.SysFont("robotoserif.ttf", 36, italic=True)
text_font_medium = pygame.font.SysFont("robotoserif.ttf", 24)

# =========== TEXT ===========
welcome_text = "Hello and Welcome! Thank you for participating in this study."
p_id_prompt = "Please enter your Participant ID in the box below."
p_age_prompt = "Please enter your Age in the box below."
p_gender_prompt = "Please enter your Gender in the box below."
p_height_prompt = "Please enter your Height in the box below."
p_weight_prompt = "Please enter your Weight in the box below."
p_wrist_prompt = "Please enter your Wrist Circumference in the box below."
p_forearm_prompt = "Please enter your Forearm Length in the box below."

# =========== TEXTBOX ===========
id_textbox = TextBox(screen, 50, 100, 50, 32, font=text_font_medium, placeholderText="ID",
                  borderColour=(255,255,255), radius=8, borderThickness=2)
age_textbox = TextBox(screen, 50, 180, 50, 32, font=text_font_medium, placeholderText="Age",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
gender_textbox = TextBox(screen, 50, 260, 200, 32, font=text_font_medium, placeholderText="Gender",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
height_textbox = TextBox(screen, 50, 340, 200, 32, font=text_font_medium, placeholderText="Height",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
weight_textbox = TextBox(screen, 50, 420, 200, 32, font=text_font_medium, placeholderText="Weight",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
wrist_textbox = TextBox(screen, 50, 500, 200, 32, font=text_font_medium, placeholderText="Wrist",
                    borderColour=(255,255,255), radius=8, borderThickness=2)
forearm_textbox = TextBox(screen, 50, 580, 200, 32, font=text_font_medium, placeholderText="Forearm",
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
                hoverColour=pygame.Color('aquamarine'), 
                pressedColour=pygame.Color('mediumseagreen'),
                onClick=lambda: write_to_csv([
                    id_textbox.getText(), 
                    age_textbox.getText(), 
                    gender_textbox.getText(), 
                    height_textbox.getText(), 
                    weight_textbox.getText(), 
                    wrist_textbox.getText(), 
                    forearm_textbox.getText()
                    ]))

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

    # update the textboxes and button
    pygame_widgets.update(events)

    pygame.display.flip()
    clock.tick(60)

# quit the program
pygame.quit()
