from Utils import Point
from Fare import Fare
from Team import Team

fares : list[Fare] = [ ]

# Lazy way to quickly generate some dummy fares
points = [
    Point(0,2),
    Point(3,0),
    Point(0,-4),
    Point(-5,0)
]
for point in points:
    fares.append(Fare(Point(0,0), point))

teams : {int : Team} = {
    3 : Team(3),
    5 : Team(5),
    7 : Team(7),
    10 : Team(10)
}

def periodic():
    global fares
    while True:
        # with mutex:
        # Update fare statuses
        for fare in fares:
            fare.periodic(teams)

        time.sleep(0.02)