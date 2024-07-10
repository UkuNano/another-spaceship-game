import pygame


def solveCollision(collision):
    # All collisions are perfectly elastic

    # Impulse must be conserved:
    #   m1u1 + m2u2 = m1v1 + m2v2

    # Kinetic energy must be conserved:
    #   m1(u1)^2 + m2(u2)^2 = m1(v1)^2 + m2(v2)^2
    # (after cancelling out the 1/2)

    # Solving for v1 and v2 yields:
    #   v1 = u1 + 2m2(u2 - u1)/(m1 + m2)
    #   v2 = u2 + 2m1(u1 - u2)/(m1 + m2)

    # Source: S. Targ, "Teoreetiline mehaanika", 1966

    m1 = collision[0]["mass"]
    m2 = collision[1]["mass"]

    collisionAxis = collision[0]["displacement"].normalize()

    u1 = collisionAxis.dot(collision[0]["velocity"])
    u2 = collisionAxis.dot(collision[1]["velocity"])

    # Axis perpendicular to the normal
    otherAxis = pygame.Vector2(-collisionAxis.y, collisionAxis.x)

    # Components of velocities perpendicular to the normal which aren't affected by the collision
    other_u1 = otherAxis.dot(collision[0]["velocity"])
    other_u2 = otherAxis.dot(collision[1]["velocity"])

    v1 = u1 + 2 * m2 / (m1 + m2) * (u2 - u1)
    v2 = u2 + 2 * m1 / (m1 + m2) * (u1 - u2)

    return [other_u1 * otherAxis + v1 * collisionAxis,
            other_u2 * otherAxis + v2 * collisionAxis]


def findCircleCollisions(objects):
    collisions = []

    for uid1, obj1 in objects.items():
        if "radius" not in obj1 or "velocity" not in obj1:
            continue  # Skip objects without a radius or a velocity

        for uid2, obj2 in objects.items():
            if uid1 == uid2 or "radius" not in obj2 or "velocity" not in obj2:
                continue  # Skip same object and objects without a radius or a velocity

            if (obj1["position"] - obj2["position"]).length() < obj1["radius"] + obj2["radius"]:
                # Check if the collision has been registered before
                isNew = True
                for collision in collisions:
                    if (collision[0]["uid"] == uid1 and collision[1]["uid"] == uid2) or \
                            (collision[0]["uid"] == uid2 and collision[1]["uid"] == uid1):
                        isNew = False
                        break

                if not isNew:
                    continue

                distance = (obj1["position"] - obj2["position"]).length()
                displacement = (obj1["position"] - obj2["position"]).normalize() * (
                        obj1["radius"] + obj2["radius"] - distance) / 2

                collision = [{
                    "uid": uid1,
                    "velocity": obj1["velocity"],
                    "mass": obj1["mass"],
                    "displacement": displacement
                }, {
                    "uid": uid2,
                    "velocity": obj2["velocity"],
                    "mass": obj2["mass"],
                    "displacement": -displacement
                }]

                collisions.append(collision)

    return collisions


def findBoundaryCollisions(objects, bounds):
    collisions = []

    for uid, obj in objects.items():
        if "radius" not in obj:
            continue  # Skip objects without a radius

        displacement = pygame.Vector2(0, 0)

        # Not using elif here and using +=, because a circle might intersect multiple borders (at a corner)

        if obj["position"].x - obj["radius"] < bounds.x:
            displacement += pygame.Vector2(obj["radius"] - obj["position"].x + bounds.x, 0)

        if obj["position"].x + obj["radius"] > bounds.w:
            displacement += pygame.Vector2(bounds.w - obj["position"].x - obj["radius"], 0)

        if obj["position"].y - obj["radius"] < bounds.y:
            displacement += pygame.Vector2(0, obj["radius"] - obj["position"].y + bounds.y)

        if obj["position"].y + obj["radius"] > bounds.h:
            displacement += pygame.Vector2(0, bounds.h - obj["position"].y - obj["radius"])

        # No collisions with borders
        if abs(displacement.length()) < 0.001:
            continue

        collision = [{
            "uid": uid,
            "velocity": obj["velocity"],
            "mass": obj["mass"],
            "displacement": displacement
        }, {  # An immovable wall with infinite mass
            "uid": -1,
            "velocity": pygame.Vector2(0, 0),
            "mass": 1000000000,
            "displacement": pygame.Vector2(0, 0)
        }]

        collisions.append(collision)

    return collisions


def update(dt, objects, bounds, eventType):
    circleCollisions = findCircleCollisions(objects)
    boundaryCollisions = findBoundaryCollisions(objects, bounds)

    collisions = circleCollisions + boundaryCollisions

    # Collision response
    for collision in collisions:
        velocities = solveCollision(collision)

        if collision[0]["uid"] >= 0:
            objects[collision[0]["uid"]]["position"] += collision[0]["displacement"]
            objects[collision[0]["uid"]]["velocity"] = velocities[0]

        if collision[1]["uid"] >= 0:
            objects[collision[1]["uid"]]["position"] += collision[1]["displacement"]
            objects[collision[1]["uid"]]["velocity"] = velocities[1]

        # Emit collision event
        if collision[0]["uid"] >= 0 and collision[1]["uid"] >= 0:
            attributes = {"uid1": collision[0]["uid"], "uid2": collision[1]["uid"]}
            collisionEvent = pygame.event.Event(eventType, attributes)

            pygame.event.post(collisionEvent)

    # Movement
    for uid, obj in objects.items():
        if "velocity" not in obj:
            continue  # Skip objects without a velocity

        obj["position"] += obj["velocity"] * dt