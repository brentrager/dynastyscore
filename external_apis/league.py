class League:
    def __str__(self):
        return self.name

    def get_rosters(self):
        raise NotImplementedError

    @staticmethod
    def is_same_player(player, rankedPlayer):
        raise NotImplementedError
