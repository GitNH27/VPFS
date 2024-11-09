from Utils import Point
from Fare import Fare

fares : {int: Fare} = { }

# Lazy way to quickly generate some dummy fares
points = [
    Point(0,2),
    Point(3,0),
    Point(0,-4),
    Point(-5,0)
]
for point in points:
    f = Fare(Point(0,0), point)
    fares[f.ID] = f

