#! /usr/bin/python3
# ^ Necessary for running on Linux

# Pygame docs: https://www.pygame.org/docs/
import pygame
import random
import math

import physics

################################

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = int(WINDOW_WIDTH / 16 * 9)
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
        if event.key == pygame.K_SPACE:
            # Spacebar pressed
            # print("Spacebar has been pressed")
            fire_bullet()
            state["gun_sound"].play()  # Play the gun sound

        if event.key == pygame.K_ESCAPE:
            # Escape key pressed
            state["running"] = False
        
        if event.key == pygame.K_c:
            state["drawColliders"] = not state["drawColliders"]

    # A key has been released
    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_SPACE:
            # print("Spacebar has been released")
            pass

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

    elif event.type == state["collisionEventType"]:
        print(F"Collision: UID1 = {event.uid1} and UID2 = {event.uid2}")
        
#        if event.uid1 == state["player_uid"]:
#            removeObject(event.uid2)
#
#        if event.uid2 == state["player_uid"]:
#            removeObject(event.uid1)

def initialize_player():
    uid = generate_uid()
    player_image = pygame.image.load("assets/spaceship_red.png")

    # Rescale the image
    scale_factor = 0.2
    new_size = (int(player_image.get_width() * scale_factor), int(player_image.get_height() * scale_factor))
    player_image = pygame.transform.scale(player_image, new_size)

    collider = {
        "position": pygame.Vector2(0, 0), # Position relative to object
        "radius": max(new_size) / 2  # Approximate radius for collision
    }

    player = {
        "position": pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2),
        "velocity": pygame.Vector2(0, 0),
        "radius": max(new_size) / 2,  # Approximate radius for collision
          "mass": max(new_size)**3 / 8,
         "image": player_image,
        "image_rect": player_image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)),
        "colliders": [collider]
    }
    state["objects"][uid] = player
    state["player_uid"] = uid

def update_player():
    keys = pygame.key.get_pressed()
    player = state["objects"][state["player_uid"]]

    speed = 350  # Adjust Player speed as necessary

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
    # player["position"] += player["velocity"] * state["dt"]
    player["image_rect"].center = player["position"]

def update_bullets():
    for bullet in state["bullets"][:]:
        bullet["position"] += bullet["velocity"] * state["dt"]
        bullet["rect"].center = bullet["position"]
        if bullet["position"].y < 0:
            state["bullets"].remove(bullet)

def fire_bullet():
    player = state["objects"][state["player_uid"]]
    bullet_image = state["bullet_image"]
    bullet_rect = bullet_image.get_rect(center=(player["position"].x, player["position"].y - player["radius"]))
    bullet = {
        "position": pygame.Vector2(player["position"].x, player["position"].y - player["radius"]),
        "velocity": pygame.Vector2(0, -500),
        "image": bullet_image,
        "rect": bullet_rect
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
    #physics.update(state["dt"], state["objects"], state["bounds"])

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
    
    for bullet in state["bullets"]:
        state["screen"].blit(bullet["image"], bullet["rect"])
    
    
    if not state["drawColliders"]:
        return
    
    for uid, obj in state["objects"].items():
        if not "colliders" in obj:
            continue
        
        for collider in obj["colliders"]:
            pos = obj["position"] + collider["position"]
            r = collider["radius"]
            pygame.draw.circle(state["screen"], (50, 50, 50), pos, r, width=3)
            pygame.draw.circle(state["screen"], (50, 255, 30), pos, r, width=1)


############### OBJECT MANAGEMENT #################

# Generates a new unique ID number. Necessary for procedurally creating new objects and referencing them later on.
# TODO: In the future objects will be destroyed, but UIDs would still increase indefinetly. Make it smarter.
def generate_uid():
    global state

    largest_uid = -1

    for uid in state["objects"].keys():
        if uid > largest_uid:
            largest_uid = uid

    return largest_uid + 1

def createObject(position = pygame.Vector2(0, 0)):
    global state

    uid = generate_uid()
    state["objects"][uid] = {"position": position}
    
    return uid

def removeObject(uid):
    global state

    del state["objects"][uid]

###################################################

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

        "drawColliders": False,

        "bounds": pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
        "background": pygame.image.load("assets/space.png"),
        "objects": {},
        "gun_sound": pygame.mixer.Sound("assets/Gun+Silencer.mp3"),  # Load the gun sound
        "bullet_image": pygame.transform.scale(pygame.image.load("assets/bullet.png"), (60, 70)),  # Adjust the size as needed
        "bullets": []
    }

    colors = [
        ( 90, 200,  20),
        (255,  60,  60),
        ( 80,  70, 220),
        (255, 220,  30),
        (230, 230, 230)
    ]

    # Create randomized circles
    for i in range(10):
        uid = createObject() # Create a new object
        x = random.randrange(50, WINDOW_WIDTH - 50, 1)
        y = random.randrange(50, WINDOW_HEIGHT - 50, 1)
        radius = random.randrange(10, 100, 1)
        colliderCount = random.randrange(2, 5, 1)
        
        # Add colliders which are circles that determine where the object can collide
        # A collider's position is relative to its object's position
        # Colliders of the same object can overlap
        colliders = []

        for i in range(colliderCount):
            # Place the colliders in a circular pattern
            colliderX = radius/2*math.cos(2*math.pi/colliderCount*i)
            colliderY = radius/2*math.sin(2*math.pi/colliderCount*i)

            collider = {
                "position": pygame.Vector2(colliderX, colliderY),
                "radius": radius/2
            }

            colliders.append(collider)

        state["objects"][uid] = {
            "position": pygame.Vector2(x, y), # Every object is required to have a position
            "velocity": pygame.Vector2(0, 0), # Necessary for physics
            "mass": radius**3, # With constant density mass is proportional to radius cubed, necessary for physics
            "colliders": colliders, # Necessary for physics
            "radius": radius,
            "color": random.choice(colors),
            "tag": "asteroid"
        }

    initialize_player()

    # Program loop
    while state["running"]:
        # Handle all available events
        for event in pygame.event.get():
            handleEvent(event)

        # Game code goes there
        update()

        physics.update(state["dt"], state["objects"], state["bounds"], state["collisionEventType"])

        draw()

        # Update the window
        pygame.display.flip()

        # Limit the framerate
        state["dt"] = state["clock"].tick(FPS_LIMIT) / 1000  # Correct dt calculation (tick() returns milliseconds)

    pygame.quit()
