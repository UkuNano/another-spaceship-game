#! /usr/bin/python3
# ^ Necessary for running on Linux

# Pygame docs: https://www.pygame.org/docs/
import pygame
import random

import physics

################################

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WINDOW_TITLE = "Another spaceship game"
FPS_LIMIT = 60

################################

# Run for every event.
# Place here the code that checks for user input.
def handleEvent(event):
    # Get access to the global variables
    global state

    if event.type == pygame.QUIT:
        state["running"] = False

    # A key has been pressed
    elif event.type == pygame.KEYDOWN:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            #print("Spacebar has been pressed")
            physics.handleCollisions(state["dt"], state["objects"])

        if keys[pygame.K_ESCAPE]:
            state["running"] = False

    # A key has been released
    elif event.type == pygame.KEYUP:
        keys = pygame.key.get_pressed()

        #if not keys[pygame.K_SPACE]:
            #print("Spacebar has been released")

    # Right mouse button has been pressed
    elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
        # Find a circle to drag
        for uid, obj in state["objects"].items():
            if "radius" in obj and (pygame.mouse.get_pos() - obj["position"]).length() < obj["radius"]:
                state["dragObject"] = uid
                state["dragDelta"] = pygame.mouse.get_pos() - obj["position"]

    # Right mouse button has been released
    elif event.type == pygame.MOUSEBUTTONUP and not pygame.mouse.get_pressed()[0]:
        # Stop dragging
        if state["dragObject"] > -1:
            state["dragObject"] = -1

def initialize_player():
    uid = generate_uid(state["objects"])
    player_image = pygame.image.load("assets/spaceship_red.png")

    # Rescale the image
    scale_factor = 0.2
    new_size = (int(player_image.get_width() * scale_factor), int(player_image.get_height() * scale_factor))
    player_image = pygame.transform.scale(player_image, new_size)

    player = {
        "position": pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2),
        "velocity": pygame.Vector2(0, 0),
        "radius": max(new_size) / 2,  # Approximate radius for collision
         "image": player_image,
        "image_rect": player_image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    }
    state["objects"][uid] = player
    state["player_uid"] = uid

def update_player():
    keys = pygame.key.get_pressed()
    player = state["objects"][state["player_uid"]]

    speed = 75  # Adjust Player speed as necessary

    # Simple movement logic: Adjust velocity based on key presses
    player["velocity"] = pygame.Vector2(0, 0)
    if keys[pygame.K_w]:
        player["velocity"].y = -speed * state["dt"]
    if keys[pygame.K_s]:
        player["velocity"].y = speed * state["dt"]
    if keys[pygame.K_a]:
        player["velocity"].x = -speed * state["dt"]
    if keys[pygame.K_d]:
        player["velocity"].x = speed * state["dt"]

    # Update player position
    player["position"] += player["velocity"]
    player["image_rect"].center = player["position"]

# Run every frame.
# Place here the code that changes the state of the game in some way every frame.
def update():
    # Get access to the global variables
    global state

    if state["dragObject"] > -1:
        for uid, obj in state["objects"].items():
            if state["dragObject"] == uid:
                obj["position"] = pygame.mouse.get_pos() - state["dragDelta"]
                break

    update_player()
    physics.update(state["dt"], state["objects"], state["bounds"])

# Run every frame.
# Place here the code that draws on the screen every frame.
def draw():
    # Get access to the global variables
    global state

    # Background
    state["screen"].blit(state["background"], (0, 0))

    # Circles
    for uid, obj in state["objects"].items():
        if "color" in obj and "radius" in obj:
            pygame.draw.circle(state["screen"], obj["color"], obj["position"], obj["radius"])
        elif "image" in obj:
            state["screen"].blit(obj["image"], obj["image_rect"])


################################

# Generates a new unique ID number. Necessary for procedurally creating new objects and referencing them later on.
# TODO: In the future objects will be destroyed, but UIDs would still increase indefinetly. Make it smarter.
def generate_uid(objects):
    largest_uid = -1

    for uid in objects.keys():
        if uid > largest_uid:
            largest_uid = uid

    return largest_uid + 1

################################

# Program entry point
if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    # The state dictionary holds all the global variables some core functions such as update() and handleEvent() need.
    # The keys are variable name strings and the values are the corresponding variable values.
    # Every function that needs access to this global program state must have a line containing 'global state'.
    state = {}

    state["screen"] = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
    state["clock"] = pygame.time.Clock()

    state["dt"] = 1 / FPS_LIMIT # Deltatime aka time between the current frame and the last frame.
    state["running"] = True

    state["dragObject"] = -1 # The UID of the object being dragged. Is set to -1 when not dragging because UIDs are only positive.
    state["dragDelta"] = pygame.Vector2(0, 0) # The difference between the object's position and the mouse's position

    state["bounds"] = [pygame.Vector2(0, 0), pygame.Vector2(WINDOW_WIDTH, WINDOW_HEIGHT)]
    state["objects"] = {}

    state["background"] = pygame.image.load("assets/space.png")

    colors = [
        ( 90, 200,  20),
        (255,  60,  60),
        ( 80,  70, 220),
        (255, 220,  30),
        (230, 230, 230)
    ]

    # Create random circles
    for i in range(10):
        uid = generate_uid(state["objects"])
        x = random.randrange(50, WINDOW_WIDTH - 50, 1)
        y = random.randrange(50, WINDOW_HEIGHT - 50, 1)
        state["objects"][uid] = {}
        state["objects"][uid]["position"] = pygame.Vector2(x, y)
        state["objects"][uid]["radius"] = random.randrange(10, 100, 1)
        state["objects"][uid]["color"] = random.choice(colors)

#    uid1 = generate_uid(state["objects"])
#    state["objects"][uid1] = {}
#    state["objects"][uid1]["position"] = pygame.Vector2(WINDOW_WIDTH / 2 - 128, WINDOW_HEIGHT / 2)
#    state["objects"][uid1]["radius"] = 100
#    state["objects"][uid1]["color"] = (90, 200, 20)
#
#    uid2 = generate_uid(state["objects"])
#    state["objects"][uid2] = {}
#    state["objects"][uid2]["position"] = pygame.Vector2(WINDOW_WIDTH / 2 + 128, WINDOW_HEIGHT / 2)
#    state["objects"][uid2]["radius"] = 150
#    state["objects"][uid2]["color"] = (255, 60, 60)

    initialize_player()

    physics.begin()

    # Program loop
    while state["running"]:
        # Handle all available events
        for event in pygame.event.get():
            handleEvent(event)

        # Game code goes there
        update()

        # Physics updates
        # At the moment atleast 2 substeps are necessary
        substeps = 2
        for i in range(substeps):
            physics.update(state["dt"]/substeps, state["objects"], state["bounds"])

        draw()
        #physics.drawDebug(state["screen"]) # Draw on top

        # Update the window
        pygame.display.flip()

        # Limit the framerate
        state["dt"] = state["clock"].tick(FPS_LIMIT) / 100  # Correct dt calculation

    pygame.quit()
