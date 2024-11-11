class Team:
    def __init__(self, number : int):
        self.number = number
        self.money = 0
        self.karma = 20
        self.currentFare : int or None = None