import pygame

# initialize pygame
pygame.init()
# pygame display size setup
screen = pygame.display.set_mode((1000, 700))
# set window title
pygame.display.set_caption("Data Collection")
# set font
pygame.font.Font()

running = True

# main loop
while running:
    for event in pygame.event.get():
        # if user clicks X to close the pygame window
        if event.type == pygame.QUIT:
            running = False

# quit the program
pygame.quit()
