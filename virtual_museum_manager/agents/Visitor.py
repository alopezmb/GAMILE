from typing import Tuple, Optional

import numpy as np
from mesa import Agent
from space.Door import Door
from space.Wall import Wall
from agents.Exhibit import Exhibit
from utils.utils import print_trace


class Visitor(Agent):
    """
    A Visitor agent.
    """

    def __init__(
            self,
            unique_id,
            model,
            pos
    ):
        """
        Create a new Visitor agent.

        Parameters
        ----------
        pos: Unique name of the room.

        """
        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.direction_vector = np.array((0, 0))
        self.accumulated_rotation = 0
        self.movement_direction = ''
        self.fov = 30
        self.room = None
        self.last_step_was_door: Tuple[bool, Optional[Door]] = (False, None)
        self.edge_path = []
        self.total_path = [self.pos]
        self.visited_exhibits = set()
        self.travel_score = 0

    def step(self):
        if not (self.direction_vector == np.array((0, 0))).all():
            self.apply_movement_vector()
        print_trace(f"Total edge path: {len(self.edge_path)}")

    def calculate_movement_vector(self, movement_direction: str, accumulated_rotation: float,
                                  modulus_multiplier=1.0):
        self.readjust_room(force=True)
        old_pos = self.pos

        # Calculate direction vector and scale it with the modulus multiplier to get
        # the resulting movement vector
        movement_vector = self.move(movement_direction, accumulated_rotation, modulus_multiplier=modulus_multiplier)
        print_trace(f'movement vector: {movement_vector}')
        print_trace(f'Accumulated rotation: {accumulated_rotation} rad')

        # Calculate next position and obtain collisions (if any) within the given field of view (FoV)
        collision_object = self.room.check_collision(old_pos, movement_vector, self.fov)

        if isinstance(collision_object, Wall):
            self.direction_vector = np.array((0, 0))
            return False

        elif isinstance(collision_object, Door):
            self.direction_vector = movement_vector
            self.last_step_was_door = (True, collision_object)

        else:
            self.direction_vector = movement_vector

        self.travel_score -= 1
        return True

    def apply_movement_vector(self):
        new_pos = self.pos + self.direction_vector
        self.pos = new_pos
        self.total_path.append(new_pos)
        self.readjust_room()
        self.direction_vector = np.array((0, 0))

    def readjust_room(self, force=False):

        if self.last_step_was_door[0] or force:
            old_room = self.room
            new_room = self.model.locate_visitor()
            door = self.last_step_was_door[1]
            if not old_room.name == new_room.name:
                self.room = new_room
                print_trace("Visitor has left {0} and has entered {1}".format(old_room.name, new_room.name))
                # If the visitor goes through the door but then decides to go again through the door without visiting
                # a painting then the edge_path list will contain two consecutive identical doors, which does not
                # make any sense for a node graph. Hence, we have to take into account this type of movement
                is_last_node_this_door = len(self.edge_path) > 0 and isinstance(self.edge_path[-1], Door) and (
                            self.edge_path[-1].name in [door.name, door.reciprocal])

                if (len(self.edge_path) == 0) or not is_last_node_this_door:
                    self.edge_path.append(door)

                self.last_step_was_door = (False, None)  # reset

    def move(self, cardinal_direction, axis_rotation_angle, modulus_multiplier=1.0):
        PI = np.pi
        if cardinal_direction == 'UP':
            return modulus_multiplier * self._transform_vector(axis_rotation_angle)
        elif cardinal_direction == 'DOWN':
            return modulus_multiplier * self._transform_vector(axis_rotation_angle + PI)
        elif cardinal_direction == 'LEFT':
            return modulus_multiplier * self._transform_vector(axis_rotation_angle + (3.0 / 2.0) * PI)
        elif cardinal_direction == 'RIGHT':
            return modulus_multiplier * self._transform_vector(axis_rotation_angle + PI / 2)
        else:
            return np.array((0, 0))

    def _transform_vector(self, axis_rotation_angle):
        """ Transform unit vector (0,1) according to the rotation angle.
        We use (0,1) in x,z axis as reference vector, and any transformation
        we do will be with respect to this vector.

        Details:

        Our reference axis in Mesa is not the traditional x,z axis. It is x,z axis but reflected
        over the x axis, which means that in reality when the visitor goes north they are travelling through
        negative z (-z) axis. Thus, transformation 1 = REFLECTION OVER X AXIS. This transformation matrix is:
        [[1 0],[0 -1]]

        Also, we need to know which direction the visitor is facing. Initially, visitor faces -z axis, so a = 0 rad.
        Visitor turning clockwise increases alpha angle. Thus, transformation 2 = ROTATION BY ANGLE α.


        @param axis_rotation_angle:
        @return:
        """

        x = np.sin(axis_rotation_angle)
        z = -np.cos(axis_rotation_angle)
        return np.array((x, z))

    def watch_painting(self, name_of_painting):
        visited_painting = next((x for x in self.model.exhibit_agents if x.name == name_of_painting), None)
        if visited_painting is not None:
            print_trace(f"Visiting {visited_painting.name}")

            # Need to make sure that no repetitions are added
            original_length = len(self.visited_exhibits)
            self.visited_exhibits.add(visited_painting)
            new_length = len(self.visited_exhibits)

            if original_length < new_length:
                self.travel_score += 100
                self.edge_path.append(visited_painting)

        else:
            raise Exception("Should have found a painting")
