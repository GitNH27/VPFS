from Utils import Point
from Fare import Fare
import random
points = [
    Point(0,0),
    Point(1, 1),
    Point(2, 2),
    Point(3, 3),
    Point(4, 4),
    Point(5, 5),
    Point(6, 6),
    Point(7, 7),
    Point(8, 8),
    Point(9, 9),
    Point(10, 10),
    Point(11, 11)
]

DIST_MIN = 0.5
DIST_MAX = 999

def generate_fare(existingFares : [Fare]) -> Fare or None:

    # May be bound later to guarantee a range of distances
    min_dist = DIST_MIN
    max_dist = DIST_MAX

    existing = []
    for fare in existingFares:
        if fare.isActive:
            existing.append(fare.src)
            existing.append(fare.dest)

    # Cap at 10 tries to avoid getting stuck
    ovf = 0
    success = False
    while ovf < 10 and not success:
        ovf += 1
        # Pick two random points, and make sure they are a valid pairing
        p1 = random.choice(points)
        p2 = random.choice(points)
        dist = Point.dist(p1, p2)
        # Need two unique points, within distance bounds, and not already in use
        if (p1 == p2
                or dist > max_dist
                or dist < min_dist
                or p1 in existing
                or p2 in existing):
            continue
        success = True

    if success:
        return Fare(p1, p2)
    return None