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


def checkObjectProperties(obj):
    return "colliders" in obj and "velocity" in obj and "mass" in obj and len(obj["colliders"]) > 0


def checkCollisionCircleCircle(pos1, r1, pos2, r2):
    return (pos1 - pos2).length_squared() < (r1 + r2) ** 2

def getDisplacementCircleCircle(pos1, r1, pos2, r2):
    difference = pos1 - pos2
    distance = difference.length()
    return difference / distance * (r1 + r2 - distance) / 2

def findObjectCollisions(objects):
    collisions = []

    for uid1, obj1 in objects.items():
        if not checkObjectProperties(obj1):
            continue  # Skip objects without a collider or a velocity

        for uid2, obj2 in objects.items():
            if uid1 == uid2 or not checkObjectProperties(obj2):
                continue  # Skip same object and objects without a collider or a velocity

            # Check if the potential collision has been registered before
            collisionFound = True
            for collision in collisions:
                if (collision[0]["uid"] == uid1 and collision[1]["uid"] == uid2) or \
                        (collision[0]["uid"] == uid2 and collision[1]["uid"] == uid1):
                    collisionFound = False
                    break

            # If we have already found a collision between these objects then skip
            if not collisionFound:
                continue

            for collider1 in obj1["colliders"]:
                for collider2 in obj2["colliders"]:
                    pos1 = obj1["position"] + collider1["position"]
                    pos2 = obj2["position"] + collider2["position"]
                    r1 = collider1["radius"]
                    r2 = collider2["radius"]

                    if not checkCollisionCircleCircle(pos1, r1, pos2, r2):
                        continue

                    displacement = getDisplacementCircleCircle(pos1, r1, pos2, r2)

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
        if not checkObjectProperties(obj):
            continue  # Skip objects without a collider or a velocity

        finalDisplacement = pygame.Vector2(0, 0)

        for collider in obj["colliders"]:
            pos = obj["position"] + collider["position"]
            radius = collider["radius"]
            displacement = pygame.Vector2(0, 0)

            # Not using elif here and using +=, because a circle might intersect multiple borders (at a corner)

            if pos.x - radius < bounds.x:
                displacement += pygame.Vector2(radius - pos.x + bounds.x, 0)

            if pos.x + radius > bounds.w:
                displacement += pygame.Vector2(bounds.w - pos.x - radius, 0)

            if pos.y - radius < bounds.y:
                displacement += pygame.Vector2(0, radius - pos.y + bounds.y)

            if pos.y + radius > bounds.h:
                displacement += pygame.Vector2(0, bounds.h - pos.y - radius)

            if abs(displacement.x) > abs(finalDisplacement.x):
                finalDisplacement.x = displacement.x

            if abs(displacement.y) > abs(finalDisplacement.y):
                finalDisplacement.y = displacement.y

        # No collisions with borders
        if finalDisplacement.length_squared() < 0.001:
            continue

        collision = [{
            "uid": uid,
            "velocity": obj["velocity"],
            "mass": obj["mass"],
            "displacement": finalDisplacement
        }, {  # An immovable wall with infinite mass
            "uid": -1,
            "velocity": pygame.Vector2(0, 0),
            "mass": 1000000000,
            "displacement": pygame.Vector2(0, 0)
        }]

        collisions.append(collision)

    return collisions


def update(dt, objects, bounds, eventType):
    # Movement
    for uid, obj in objects.items():
        if "velocity" not in obj:
            continue  # Skip objects without a velocity

        obj["position"] += obj["velocity"] * dt

    circleCollisions = findObjectCollisions(objects)
    boundaryCollisions = findBoundaryCollisions(objects, bounds)

    collisions = circleCollisions + boundaryCollisions

    # Collision response
    for collision in collisions:
        velocities = solveCollision(collision)

        if collision[0]["uid"] >= 0:
            # Move the objects away a bit more than just the displacement to avoid very small collisions
            displacement = (collision[0]["displacement"].length() + 0.01) * collision[0]["displacement"].normalize()
            objects[collision[0]["uid"]]["position"] += displacement
            objects[collision[0]["uid"]]["velocity"] = velocities[0]

        if collision[1]["uid"] >= 0:
            # Move the objects away a bit more than just the displacement to avoid very small collisions
            displacement = (collision[1]["displacement"].length() + 0.01) * collision[1]["displacement"].normalize()
            objects[collision[1]["uid"]]["position"] += displacement
            objects[collision[1]["uid"]]["velocity"] = velocities[1]

        # Emit collision event
        if collision[0]["uid"] >= 0 and collision[1]["uid"] >= 0:
            attributes = {"uid1": collision[0]["uid"], "uid2": collision[1]["uid"]}
            collisionEvent = pygame.event.Event(eventType, attributes)

            pygame.event.post(collisionEvent)