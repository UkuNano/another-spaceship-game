#! /usr/bin/python3
# ^ Necessary for running on Linux

# Pygame docs: https://www.pygame.org/docs/
import pygame
import random

import physics

################################

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 960
WINDOW_TITLE = "Another spaceship game"
FPS_LIMIT = 60
MAX_SPEED = 500  # The maximum speed for circles

colors = [
    (90, 200, 20),
    (255, 60, 60),
    (80, 70, 220),
    (255, 220, 30),
    (230, 230, 230)
]

# Fonts
pygame.font.init()
FONT = pygame.font.Font(None, 74)
SMALL_FONT = pygame.font.Font(None, 50)
SCORE_FONT = pygame.font.Font(None, 36)

################################

def draw_text(screen, text, font, color, position):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

# Run for every event.
# Place here the code that checks for user input.
def handleEvent(event):
    # Get access to the global variables
    global state

    if event.type == pygame.QUIT:
        state["running"] = False

    # A key has been pressed
    elif event.type == pygame.KEYDOWN:
        if state["page"] == "intro":
            if event.key == pygame.K_q:
                state["running"] = False
            elif event.key == pygame.K_p:
                state["page"] = "game"
                reset_game_state()
            elif event.key == pygame.K_h:
                state["page"] = "how_to_play"
        elif state["page"] == "how_to_play":
            if event.key == pygame.K_b:
                state["page"] = "intro"
        elif state["page"] == "game":
            if event.key == pygame.K_SPACE:
                fire_bullet()
                state["gun_sound"].play()
            if event.key == pygame.K_ESCAPE:
                state["running"] = False
        elif state["page"] == "game_over":
            if event.key == pygame.K_RETURN:
                state["page"] = "intro"


    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if state["page"] == "intro":
            if state["play_button"].collidepoint(event.pos):
                state["page"] = "game"
                reset_game_state()
            elif state["how_to_play_button"].collidepoint(event.pos):
                state["page"] = "how_to_play"
            elif state["quit_button"].collidepoint(event.pos):
                state["running"] = False
        elif state["page"] == "how_to_play":
            if state["back_button"].collidepoint(event.pos):
                state["page"] = "intro"
        elif state["page"] == "game_over":
            if state["play_button"].collidepoint(event.pos):
                state["page"] = "intro"

def reset_game_state():
    global state
    state["objects"] = {}
    state["bullets"] = []
    initialize_player()
    state["spawn_timer"] = 0
    state["spawn_interval"] = 3000
    state["score"] = 0

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
          "mass": max(new_size)**3 / 8,
         "image": player_image,
        "image_rect": player_image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    }
    state["objects"][uid] = player
    state["player_uid"] = uid

def update_player():
    keys = pygame.key.get_pressed()
    player = state["objects"][state["player_uid"]]

    speed = 300  # Adjust Player speed as necessary

    # Simple movement logic: Adjust velocity based on key presses
    player["velocity"] = pygame.Vector2(0, 0)
    if keys[pygame.K_w]:
        player["velocity"].y = -speed
    if keys[pygame.K_s]:
        player["velocity"].y = speed
    if keys[pygame.K_a]:
        player["velocity"].x = -speed
    if keys[pygame.K_d]:
        player["velocity"].x = speed

    # Update player position
    player["position"] += player["velocity"] * state["dt"]
    player["image_rect"].center = player["position"]

def update_bullets():
    for bullet in state["bullets"][:]:
        bullet["position"] += bullet["velocity"] * state["dt"]
        bullet["rect"].center = bullet["position"]
        if bullet["position"].y < 0:
            state["bullets"].remove(bullet)
        elif bullet.get("marked_for_removal") and bullet["drawn"]:
            state["bullets"].remove(bullet)
        else:
            bullet["drawn"] = True

def handle_bullet_collisions():
    player_uid = state.get("player_uid")
    for bullet in state["bullets"][:]:
        bullet_rect = bullet["rect"]
        for uid, obj in list(state["objects"].items()):
            if uid == player_uid:
                continue  # Skip the player object
            if "radius" in obj:
                circle_rect = pygame.Rect(obj["position"].x - obj["radius"], obj["position"].y - obj["radius"],
                                          obj["radius"] * 2, obj["radius"] * 2)
                if bullet_rect.colliderect(circle_rect):
                    bullet["marked_for_removal"] = True
                    del state["objects"][uid]
                    state["score"] += 1  # Increment score
                    break

def check_player_collision():
    player = state["objects"][state["player_uid"]]
    player_rect = player["image_rect"]

    for uid, obj in list(state["objects"].items()):
        if uid == state["player_uid"]:
            continue  # Skip the player object
        if "radius" in obj:
            circle_center = obj["position"]
            circle_radius = obj["radius"]

            # Check for collision between player rectangle and circle
            closest_point = pygame.Vector2(
                max(player_rect.left, min(circle_center.x, player_rect.right)),
                max(player_rect.top, min(circle_center.y, player_rect.bottom))
            )

            distance = (closest_point - circle_center).length()
            if distance < circle_radius:
                state["page"] = "game_over"
                return

def fire_bullet():
    player = state["objects"][state["player_uid"]]
    bullet_image = state["bullet_image"]
    bullet_rect = bullet_image.get_rect(center=(player["position"].x, player["position"].y - player["radius"]))
    bullet = {
        "position": pygame.Vector2(player["position"].x, player["position"].y - player["radius"]),
        "velocity": pygame.Vector2(0, -500),
        "image": bullet_image,
        "rect": bullet_rect,
        "drawn": False
    }
    state["bullets"].append(bullet)

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
    update_bullets()
    handle_bullet_collisions()
    check_player_collision()
    #physics.update(state["dt"], state["objects"], state["bounds"])

    # Cap the speed of circles
    for uid, obj in state["objects"].items():
        if "velocity" in obj:
            speed = obj["velocity"].length()
            if speed > MAX_SPEED:
                obj["velocity"].scale_to_length(MAX_SPEED)

# Run every frame.
# Place here the code that draws on the screen every frame.
def draw():
    # Get access to the global variables
    global state

    # Background
    state["screen"].blit(state["background"], (0, 0))

    if state["page"] == "intro":
        draw_text(state["screen"], "Play", FONT, (255, 255, 255), (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 100))
        draw_text(state["screen"], "How to Play", FONT, (255, 255, 255), (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2))
        draw_text(state["screen"], "Quit", FONT, (255, 255, 255), (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 + 100))

    elif state["page"] == "how_to_play":
        draw_text(state["screen"], "How to Play", FONT, (255, 255, 255), (WINDOW_WIDTH // 2 - 150, 100))
        draw_text(state["screen"], "Use W/A/S/D to move", SMALL_FONT, (255, 255, 255), (100, 300))
        draw_text(state["screen"], "Press Space to shoot", SMALL_FONT, (255, 255, 255), (100, 400))
        draw_text(state["screen"], "Press ESC to quit the game", SMALL_FONT, (255, 255, 255), (100, 500))
        draw_text(state["screen"], "Press B to go back", SMALL_FONT, (255, 255, 255), (100, 600))

    elif state["page"] == "game":
        for uid, obj in state["objects"].items():
            if "color" in obj and "radius" in obj:
                pygame.draw.circle(state["screen"], obj["color"], obj["position"], obj["radius"])
            elif "image" in obj:
                state["screen"].blit(obj["image"], obj["image_rect"])
        for bullet in state["bullets"]:
            state["screen"].blit(bullet["image"], bullet["rect"])

        draw_text(state["screen"], f"Score: {state['score']}", SCORE_FONT, (255, 255, 255), (10, 10))
    elif state["page"] == "game_over":
        draw_text(state["screen"], "Oh no, you lost!", FONT, (255, 255, 255),
                  (WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 - 50))
        draw_text(state["screen"], "Press Enter to return to main menu", SMALL_FONT, (255, 255, 255),
                  (WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2 + 50))


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

def spawn_circle():
    uid = generate_uid(state["objects"])
    x = random.randrange(50, WINDOW_WIDTH - 50, 1)
    y = -50  # Start from above the top of the screen
    r = random.randrange(10, 100, 1)
    velocity = pygame.Vector2(random.uniform(-100, 100), random.uniform(50, 200))  # Random direction and speed

    state["objects"][uid] = {
        "position": pygame.Vector2(x, y),
        "velocity": velocity,
        "mass": r**3,  # With constant density mass is proportional to radius cubed
        "radius": r,
        "color": random.choice(colors),
        "tag": "asteroid"
    }

# Program entry point
if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    # The state dictionary holds all the global variables some core functions such as update() and handleEvent() need.
    # The keys are variable name strings and the values are the corresponding variable values.
    # Every function that needs access to this global program state must have a line containing 'global state'.
    state = {
        "screen": pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT]),
        "clock": pygame.time.Clock(),
        "dt": 1 / FPS_LIMIT, # Deltatime aka time between the current frame and the last frame.
        "running": True,
        "collisionEventType": pygame.event.custom_type(),

        "dragObject": -1, # The UID of the object being dragged. Is set to -1 when not dragging because UIDs are only positive.
        "dragDelta": pygame.Vector2(0, 0), # The difference between the object's position and the mouse's position

        "bounds": pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
        "background": pygame.image.load("assets/space.png"),
        "objects": {},
        "gun_sound": pygame.mixer.Sound("assets/Gun+Silencer.mp3"),  # Load the gun sound
        "bullet_image": pygame.transform.scale(pygame.image.load("assets/bullet.png"), (60, 70)),  # Adjust the size as needed
        "bullets": [],

        "spawn_timer": 0,
        "spawn_interval": 3000,  # Initial interval in milliseconds
        "max_circles": 8,  # Maximum number of circles on the screen

        "page": "intro",
        "play_button": pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 100, 200, 50),
        "how_to_play_button": pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2, 300, 50),
        "quit_button": pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 100, 200, 50),
        "back_button": pygame.Rect(100, 600, 200, 50),
        "score": 0  # Initialize score
    }

    initialize_player()

    # Program loop
    while state["running"]:
        # Handle all available events
        for event in pygame.event.get():
            handleEvent(event)

        # Game code goes there
        if state["page"] == "game":
            update()

            substeps = 2
            for i in range(substeps):
                physics.update(state["dt"] / substeps, state["objects"], state["bounds"], state["collisionEventType"])

        draw()

        # Update the window
        pygame.display.flip()

        # Limit the framerate
        state["dt"] = state["clock"].tick(FPS_LIMIT) / 1000  # Correct dt calculation (tick() returns milliseconds)

        state["spawn_timer"] += state["clock"].get_time()
        if state["spawn_timer"] >= state["spawn_interval"] and len(state["objects"]) < state["max_circles"]:
            spawn_circle()
            state["spawn_timer"] = 0
            state["spawn_interval"] = max(500,
                                          state["spawn_interval"] - 50)  # Decrease the interval, but not below 500ms

    pygame.quit()