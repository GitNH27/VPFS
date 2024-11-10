from Utils import Point

class Fare:
    def __init__(self, src : Point, dest: Point):
        """
        :param src: Location the ducky is picked up at
        :param dest: Location the ducky is delivered to
        """
        self.src = src
        self.dest = dest
        self.dist = src.dist(dest)
        self.team : int | None = None

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
