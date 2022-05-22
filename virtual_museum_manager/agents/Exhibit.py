import numpy as np

from mesa import Agent


class Exhibit(Agent):
    """
    An Exhibit agent to be consumed by a visitor
    """

    def __init__(self, unique_id=None, model=None, name=None,
                 room_name=None, popularity="common", pos=None, selected=False):
        """
        Create a new Room object.

        Parameters
        ----------
        name: Name of the exhibit.
        pos: position of exhibit in the room.
        room_name: name of the room the exhibit is located in.
        popularity: popularity of the exhibit. "common" or "popular".
        selected: whether the exhibit is chosen by the visitor in their museum tour.
        """

        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.name = name
        self.room_name = room_name
        self.popularity = popularity
        self.selected = selected

    def __hash__(self):
        hashing_param = f"{self.unique_id}_{self.name}"
        return hash(hashing_param)

    def __eq__(self, other):
        return (self.name == other.name) and np.array_equal(self.pos, other.pos)

    def __str__(self):
        return self.name

    def step(self):
        """
        Exhibit agent has a passive interaction: visitors consume them, but exhibits themselves do nothing.
        """
        pass
