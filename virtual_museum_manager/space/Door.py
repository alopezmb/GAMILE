from shapely.geometry import LineString


class Door:
    """
    Class that implements the doors for each room

    Methods
    -------

    """

    def __init__(self, start_point=None, end_point=None,
                 room_origin=None, room_destination=None):
        """
        Create a new Door object

        Parameters
        ----------
        start_point: coordinates of the starting point of the door.
        end_point: coordinates of the ending point of the door.
        """

        self.name = str(room_origin) + "_" + str(room_destination)
        self.reciprocal = str(room_destination) + "_" + str(room_origin)
        self.start_point = start_point
        self.end_point = end_point

        self.room_origin = room_origin
        self.room_destination = room_destination
        self.door_line = self._create_door_line()

    def __str__(self):
        return str(self.name)

    def _create_door_line(self):
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        return LineString([(x1, y1), (x2, y2)])

