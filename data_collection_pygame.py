import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
from pathlib import Path
import csv

# initialize pygame
pygame.init()

# set screen width and height
screen_width = 1000
screen_height = 700
# pygame display size setup
screen = pygame.display.set_mode((screen_width, screen_height))
# set window title
pygame.display.set_caption("Data Collection")

clock = pygame.time.Clock()

running = True

# =========== FONT ===========
text_font_big = pygame.font.SysFont("robotoserif.ttf", 36, italic=True)
text_font_medium = pygame.font.SysFont("robotoserif.ttf", 28)

# =========== TEXT ===========
welcome_text = "Hello and Welcome! Thank you for participating in this study."
p_id_prompt = "Please enter your Participant ID in the box below."
p_gender_prompt = "Please enter your Gender in the box below."

# =========== TEXTBOX ===========
id_textbox = TextBox(screen, 50, 125, 50, 35, font=text_font_medium, placeholderText="ID",
                  borderColour=(255,255,255), radius=8, borderThickness=2)
gender_textbox = TextBox(screen, 50, 205, 200, 35, font=text_font_medium, placeholderText="Gender",
                    borderColour=(255,255,255), radius=8, borderThickness=2)

# =========== COLORS ===========
black = (0, 0, 0)
white = (255, 255, 255)

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
def write_to_csv(csv_writer, row):
    csv_writer.writerow(row)

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

# =========== MAIN LOOP ===========
# main loop
while running:
    # fill the screen with black color
    screen.fill(black)

    events = pygame.event.get()
    
    for event in events:
        # if user clicks X to close the pygame window
        if event.type == pygame.QUIT:
            running = False

    # display welcome text on the screen
    display_text(welcome_text, text_font_big, white, 50, 50)

    '''
    https://www.youtube.com/watch?v=Rvcyf4HsWiw
    '''
    # display get participant ID prompt on the screen
    id_text_surface = text_font_medium.render(p_id_prompt, True, white)
    screen.blit(id_text_surface, (50, 100))

    # display get participant gender prompt on the screen
    gender_text_surface = text_font_medium.render(p_gender_prompt, True, white)
    screen.blit(gender_text_surface, (50, 180))

    pygame_widgets.update(events)

    pygame.display.flip()
    clock.tick(60)

# quit the program
pygame.quit()
