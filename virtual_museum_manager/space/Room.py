import numpy as np
import re
from shapely.geometry import Point, Polygon, LineString

from space.Door import Door
from space.Wall import Wall
from utils.utils import print_trace


class Room:
    """
    Class that implements the rooms that Visitors can enter and consume Exhibits

    Methods
    -------

    """

    def __init__(self, name=None, vertices=None, doors=None, exhibits=None, grid_dimensions=None):
        """
        Create a new Room object.

        Parameters
        ----------
        name: Unique name of the room.
        vertices: list of the vertices that make up the room
        doors: list of doors that this room has.
        exhibits : list of exhibits in the room.
        grid_dimensions: dimensions of the grid. This is used to denormalize coordinates

        """

        self.name = name
        self.grid_dimensions = grid_dimensions
        self.vertices = [self._create_room_coordinate(vertex) for vertex in vertices]
        self.polygon = Polygon(self.vertices)
        self.doors = self._create_doors(doors)
        self.exhibits = self._create_exhibits(exhibits)

    def inside_room(self, position):
        """
        Checks if the specified position (x,y) is contained within the room's bounds.

        Parameters
        ----------
        position (x,y) :

        Returns
        -------
        (Boolean): True if the specified position is in the room, otherwise return false
        """

        x, y = position
        point = Point(x, y)

        return point.intersects(self.polygon)

    def check_collision(self, old_position, movement_vector, fov):
        """ Checks collisions of the specified movement

        @param old_position: current visitor's position
        @param movement_vector: movement vector that defines which will be
        the new position of the visitor
        @param fov: range of collision detection
        @return: object with which visitor collides (Door, Wall or None if there is no collision)
        """

        x_old, y_old = old_position
        old_point = Point(x_old, y_old)

        x_new, y_new = (old_position + movement_vector)
        new_position = np.array((x_new, y_new))
        center = Point(x_new, y_new)
        circle = center.buffer(fov)

        # Line that describes the movement between the old position and the new position
        # Will be used to detect visitor crossing doors
        movement_line = LineString([old_position, new_position])

        # Same as the movement line but longer (2*fov). Midpoint is the new position
        # Will be used to detect walls and doors inside the visitor's FoV.
        direction_ray = LineString([new_position - (movement_vector * fov),
                                    new_position + (movement_vector * fov)])

        v_norm = movement_vector / (np.linalg.norm(movement_vector) + 1e-16)
        direction_ray_forward = LineString([new_position, new_position + v_norm * fov])

        # Perpendicular to the direction ray.
        perpendicular_movement_vector = np.array((-movement_vector[1], movement_vector[0]))
        perpendicular_direction_ray = LineString([new_position - (perpendicular_movement_vector * fov),
                                                  new_position + (perpendicular_movement_vector * fov)])

        # Enter condition if the defined vision circle touches or goes beyond boundaries of the room
        # Boundaries can be walls or doors. Gotcha: Doors are superposed in walls, so
        # we have to be careful to distinguish doors from walls when allowing/hindering
        # movement.
        if not circle.within(self.polygon):
            direction_ray_intersects_wall = not direction_ray.within(self.polygon)
            perpendicular_ray_intersects_wall = not perpendicular_direction_ray.within(self.polygon)

            for door in self.doors:
                in_fov = circle.intersects(door.door_line)
                entrance_door_id = '1_1'

                if in_fov and door.name != entrance_door_id:

                    ray_intersects_door = direction_ray.intersects(door.door_line)
                    perpendicular_ray_intersects_door = perpendicular_direction_ray.intersects(door.door_line)
                    crossing_door = movement_line.intersects(door.door_line) and ray_intersects_door
                    moving_away_from_door = (center.distance(door.door_line) >= old_point.distance(
                        door.door_line)) and (ray_intersects_door or perpendicular_ray_intersects_door)

                    # Visitor is approaching or moving away from the door
                    if (ray_intersects_door and not crossing_door) or (moving_away_from_door and not crossing_door):
                        print_trace('Moving around door {}'.format(door.name))
                        return None
                    # Visitor is crossing a door with this movement
                    elif crossing_door:
                        print_trace('Crossing door {}'.format(door.name))
                        return door if door.name != 'D1-1' else Wall()

            direction_ray_forward_intersects_wall = not direction_ray_forward.within(self.polygon)
            if not direction_ray_forward_intersects_wall:
                return None

            elif direction_ray_intersects_wall or perpendicular_ray_intersects_wall:
                print_trace('Intersecting wall')
                return Wall()
        else:
            # Visitor's circle is completely inside the room, which means
            # no obstacles found
            print_trace('No obstacles found. Advance.')
            return None

    def _create_room_coordinate(self, coordinate):

        """
        Created an (x,y) numpy coordinate from the specified dictionary
         e.g. IN {'x': 123, 'y':234} --> OUT = np.array((123,234))

       Parameters
       ----------
       coordinate dict

       Returns
       -------
       point (Numpy array) : numpy coordinate.
       """

        x_max = self.grid_dimensions[0]
        y_max = self.grid_dimensions[1]

        # Denormalize
        _x = coordinate['x']
        _y = coordinate['y']

        # Make sure denormalized values stay within permitted range
        # i.e. x_max = 50 means the maximum value is not 50, but 49 (50 values 0 to 49).
        x = x_max if _x == x_max else _x
        y = y_max if _y == y_max else _y

        point = np.array((x, y))
        return point

    def _create_doors(self, doors):
        """
        Creates a door object

        Parameters
        ---------
        doors (list) : list of door dictionaries that contain relevant properties about the doors (including location).

        Returns
        -------
        door_objects (list Door) : list of instances of Door class, i.e. door objects.

        """
        # If there are no doors, just return an empty list
        if not doors:
            return []

        x_max = self.grid_dimensions[0]
        y_max = self.grid_dimensions[1]
        door_objects = []
        room_number_origin = re.findall(r"\d+", self.name)[0]

        for door in doors:
            # Denormalize
            _x1 = door['p_start']['x']
            _y1 = door['p_start']['y']
            _x2 = door['p_end']['x']
            _y2 = door['p_end']['y']

            # Make sure denormalized values stay within permitted range
            # i.e. x_max = 50 means the maximum value is not 50, but 49 (50 values 0 to 49).
            x1 = x_max if _x1 == x_max else _x1
            y1 = y_max if _y1 == y_max else _y1
            x2 = x_max if _x2 == x_max else _x2
            y2 = y_max if _y2 == y_max else _y2

            # Pair of denormalized coordinates: start of door and end of door
            ini_point = np.array((x1, y1))
            end_point = np.array((x2, y2))

            # Create door object
            door_object = Door(start_point=ini_point,
                               end_point=end_point, room_origin=room_number_origin,
                               room_destination=door['connects_to_room'])
            # Add door object to the list of door objects for this room
            door_objects.append(door_object)

        return door_objects

    def _create_exhibits(self, exhibits):
        """
        Creates a list of exhibits that are associated to the current room.

        Parameters
        ----------
        exhibits (list) : list of dictionaries each containing information about a given exhibit.
        This information includes its name, popularity and location within the room.

        Returns
        -------
        exhibits (list) : same list as the beginning but with the location property as a numpy array
        with the denormalized position.
        """

        # If there are no exhibits, just return an empty list
        if not exhibits:
            return []

        x_max = self.grid_dimensions[0]
        y_max = self.grid_dimensions[1]
        x_min = 0
        y_min = 0
        exhibits_adjusted = []

        for exhibit in exhibits:

            _x = exhibit['location']['x']
            _y = exhibit['location']['y']

            # Make sure exhibits are not placed within the limits of the grid.
            # They have to to be placed one coord away from the limit (limits of grid have walls)
            x = (x_max - 1) if _x == x_max else (x_min + 1) if _x == x_min else _x
            y = (y_max - 1) if _y == y_max else (y_min + 1) if _y == y_min else _y

            exhibit['location'] = np.array((x, y))
            exhibits_adjusted.append(exhibit)

        return exhibits_adjusted
