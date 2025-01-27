from Utils import Point
from Fare import Fare, FareType
import random

from VPFS.FareProbability import FareProbability

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

# TODO: Find a way to link this to the one in FMS.py without a circular import
TARGET_FARES = 5
# Aim to have 1-2 of the special fare types at a time, Normal is the remainder
targetProbabilities = {
    FareType.SUBSIDIZED: 1.5 / TARGET_FARES,
    FareType.SENIOR: 1.5 / TARGET_FARES
}
targetProbabilities[FareType.NORMAL] = 1 - sum(targetProbabilities.values())

def generate_fare(existingFares : [Fare]) -> Fare or None:

    # May be bound later to guarantee a range of distances
    min_dist = DIST_MIN
    max_dist = DIST_MAX

    existing = []
    # Track number of each type
    quantities: dict[FareType, float] = {
        FareType.NORMAL: 0,
        FareType.SUBSIDIZED: 0,
        FareType.SENIOR: 0,
    }
    active_fares : int = 0
    for fare in existingFares:
        if fare.isActive:
            active_fares += 1
            existing.append(fare.src)
            existing.append(fare.dest)
            quantities[fare.type] += 1

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

    # Additional probability weightings to try to balance options
    prob_mul: dict[FareType, float] = { }
    for key, value in quantities.items():
        # Determine the current ratio for the fare type, relative to target qty not actual qty
        curr_ratio = value / max(active_fares, 1)
        if curr_ratio == 0:
            curr_ratio = 0.01
        # Calculate the probability multiplier based on target and current. Bound between 1/10x and 10x
        prob_mul[key] = min(max(targetProbabilities[key] / curr_ratio, 1/4), 10)

    if success:
        prob = FareProbability()
        # Multiply base probabilities by the
        for key, value in prob:
            prob[key] *= prob_mul.get(key, 1)

        return Fare(p1, p2, prob.roll())
    return None