import pygame

_collisions = []

def begin():
    print("Hi from physics.py")

def update(dt, objects, bounds):
    global _collisions

    # Forget collisions from the previous frame
    _collisions = []

    # Collisions between circles
    for uid1, obj1 in objects.items():
        if "radius" not in obj1:
            continue  # Skip objects without a radius

        for uid2, obj2 in objects.items():
            if uid1 == uid2 or "radius" not in obj2:
                continue  # Skip same object and objects without a radius

            if (obj1["position"] - obj2["position"]).length() < obj1["radius"] + obj2["radius"]:
                # Check if the collision has been registered before
                isNew = True
                for collision in _collisions:
                    if (collision[0]["uid"] == uid1 and collision[1]["uid"] == uid2) or \
                            (collision[0]["uid"] == uid2 and collision[1]["uid"] == uid1):
                        isNew = False
                        break

                if not isNew: continue

                distance = (obj1["position"] - obj2["position"]).length()
                delta = (obj1["position"] - obj2["position"]).normalize() * (
                            obj1["radius"] + obj2["radius"] - distance) / 2

                collision = [{}, {}]
                collision[0]["uid"] = uid1
                collision[0]["position"] = obj1["position"]  # For debug purposes
                collision[0]["delta"] = delta
                collision[1]["uid"] = uid2
                collision[1]["position"] = obj2["position"]  # For debug purposes
                collision[1]["delta"] = -delta

                _collisions.append(collision)

    # Collisions with world boundaries
    for uid, obj in objects.items():
        if "radius" not in obj:
            continue  # Skip objects without a radius

        delta = pygame.Vector2(0, 0)

        # Not using elif here and using +=, because a circle might intersect multiple borders (at a corner)

        if obj["position"].x - obj["radius"] < bounds[0].x:
            delta += pygame.Vector2(obj["radius"] - obj["position"].x + bounds[0].x, 0)

        if obj["position"].x + obj["radius"] > bounds[1].x:
            delta += pygame.Vector2(bounds[1].x - obj["position"].x - obj["radius"], 0)

        if obj["position"].y - obj["radius"] < bounds[0].y:
            delta += pygame.Vector2(0, obj["radius"] - obj["position"].y + bounds[0].y)

        if obj["position"].y + obj["radius"] > bounds[1].y:
            delta += pygame.Vector2(0, bounds[1].y - obj["position"].y - obj["radius"])

        if abs(delta.length()) < 0.001: continue

        collision = [{}, {}]
        collision[0]["uid"] = uid
        collision[0]["position"] = obj["position"] # For debug purposes
        collision[0]["delta"] = delta
        collision[1]["uid"] = -1
        collision[1]["position"] = obj["position"] - obj["radius"] * delta.normalize() # For debug purposes
        collision[1]["delta"] = pygame.Vector2(0, 0)
        
        _collisions.append(collision)

    # Collision response
    for collision in _collisions:
        if collision[0]["uid"] >= 0:
            objects[collision[0]["uid"]]["position"] += collision[0]["delta"]

        if collision[1]["uid"] >= 0:
            objects[collision[1]["uid"]]["position"] += collision[1]["delta"]

def drawDebug(screen):
    global _collisions

    for collision in _collisions:
        pos1 = collision[0]["position"]
        delta1 = collision[0]["delta"]
        pos2 = collision[1]["position"]
        delta2 = collision[1]["delta"]

        pygame.draw.rect(screen, (255, 0, 255), pygame.Rect(pos1 - (5, 5), (10, 10)))
        pygame.draw.line(screen, (255, 0, 255), pos1, pos1 + delta1, width=3)

        pygame.draw.rect(screen, (255, 0, 255), pygame.Rect(pos2 - (5, 5), (10, 10)))
        pygame.draw.line(screen, (255, 0, 255), pos2, pos2 + delta2, width=3)

#def handleCollisions(dt, objects):
#    global _collisions
#
#    for collision in _collisions:
#        if collision[0]["uid"] >= 0:
#            objects[collision[0]["uid"]]["position"] += collision[0]["delta"]
#
#        if collision[1]["uid"] >= 0:
#            objects[collision[1]["uid"]]["position"] += collision[1]["delta"]
