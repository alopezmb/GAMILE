class Ant:
    """
    Class representing an Ant in the ACO framework.
    """

    def __init__(self, ant_id, num_exhibits, first_exhibit, distances):

        self.id = ant_id
        self.visited_exhibits = []
        self.distances = distances
        self.ant_tour = self._tour_construction(num_exhibits, first_exhibit)

        pass

    def _tour_construction(self, num_exhibits, first_exhibit):
        """
        Construct ant tour
        """
        pass
        return None
