import random

from Utils import Point
import time

POSITION_TOLERANCE = 0.15
PICKUP_DURATION = 10
DROPOFF_DURATION = 10

class Fare:
    def __init__(self, src : Point, dest: Point):
        """
        :param src: Location the ducky is picked up at
        :param dest: Location the ducky is delivered to
        """
        self.src = src
        self.dest = dest
        self.dist = src.dist(dest)
        self.expiry = time.time() + random.randint(60, 150)
        self.team : int | None = None
        # Timeout used to create pickup/dropoff delay
        self._phaseTimeout = -1
        self.isActive = True
        self.inPosition = False
        self.pickedUp = False
        self.completed = False

    def compute_fare(self) -> float:
        """
        Compute the fare earned from delivering this ducky
        :return:
        """
        return self.dist * 7.5 + 2

    def claim_fare(self, team : int) -> bool:
        """
        Claim the fare for a team
        :param team: To claim fare for
        :return: True if fare claimed successfully
        """
        # Claim if not already claimed
        if self.team is None:
            self.team = team
            return True
        return False

    def periodic(self, teams):
        """
        Update phases of the fare
        Checks team position to determine if they are at start/destination, and if dropoff/pickup should occur
        """
        # Update active status
        if not self.isActive:
            return
        # Becomes inactive if time expires without a claiming team or the fare is completed
        self.isActive = (self.expiry > time.time() or self.team is not None) and not self.completed

        if self.team is None or self.team not in teams:
            return

        team = teams[self.team]

        # Check phase
        if self.pickedUp is False:
            # For pickup should be near the source position
            if team.pos.dist(self.src) < POSITION_TOLERANCE:
                self.inPosition = True
                # If no timeout started, then start it
                if self._phaseTimeout == -1:
                    self._phaseTimeout = time.time() + 5
                # If timeout completed, then set picked up
                elif self._phaseTimeout < time.time():
                    self.pickedUp = True
                    self._phaseTimeout = -1
            else:
                self.inPosition = False
                self._phaseTimeout = -1
        else:
            # For dropoff should be near the destination position
            if team.pos.dist(self.dest) < POSITION_TOLERANCE:
                self.inPosition = True
                # If no timeout started, then start it
                if self._phaseTimeout == -1:
                    self._phaseTimeout = time.time() + 5
                # If timeout completed, then set fare completed
                elif self._phaseTimeout < time.time():
                    self.completed = True
                    self._phaseTimeout = -1
            else:
                self._phaseTimeout = -1
                self.inPosition = False
