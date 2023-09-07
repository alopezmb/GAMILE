import itertools
import bisect
import random
import sys
from copy import copy

from aco_final.solvers import Solution


class Ant:

    def __init__(self, alpha=1, beta=3):
        self.alpha = alpha
        self.beta = beta

    def construct_tour(self, exhibit_and_door_graph, start_room=1, start_door='D1-1'):
        """
        Construct a tour including all chosen exhibits
        """
        start_node = start_door
        solution = Solution(exhibit_and_door_graph, start_node, ant=self)
        all_unexplored_exhibits = self.get_unexplored_exhibits_in_room(solution, exhibit_and_door_graph,
                                                                       start_node, start_room, all_rooms=True)
        room = start_room
        door = start_node
        visited_rooms = {room}
        while all_unexplored_exhibits:
            door, room, all_unexplored_exhibits, visited_rooms = self._construct_exhibit_tour_in_room(solution, room, door,
                                                                                                      exhibit_and_door_graph,
                                                                                                      all_unexplored_exhibits, visited_rooms)

        return solution

    def _construct_exhibit_tour_in_room(self, solution, current_room, starting_node_in_current_room, exhibit_and_door_graph,
                                        all_unexplored_exhibits, visited_rooms):

        # solution = Solution(room_graph, starting_node_in_current_room, ant=self)
        unexplored_exhibit_nodes_in_room = self.get_unexplored_exhibits_in_room(solution, exhibit_and_door_graph,
                                                                                starting_node_in_current_room, current_room)
        last_exhibit = None
        while unexplored_exhibit_nodes_in_room:
            next_exhibit = self._choose_destination(exhibit_and_door_graph, solution, unexplored_exhibit_nodes_in_room)

            solution.add_node(next_exhibit)
            last_exhibit = next_exhibit
            unexplored_exhibit_nodes_in_room = self._remove_node_safe(unexplored_exhibit_nodes_in_room, next_exhibit)
            all_unexplored_exhibits = self._remove_node_safe(all_unexplored_exhibits, next_exhibit)

        # All exhibits in the room have been explored, now we need choose a door to go to the next room

        # Have all exhibits been visited?
        if len(all_unexplored_exhibits) == 0:
            return current_room, starting_node_in_current_room, all_unexplored_exhibits, visited_rooms

        last_exhibit = last_exhibit if last_exhibit is not None else starting_node_in_current_room
        unexplored_door_nodes_in_room = self._get_unexplored_door_nodes(solution, exhibit_and_door_graph, last_exhibit, current_room)

        next_door = self._choose_destination(exhibit_and_door_graph, solution, unexplored_door_nodes_in_room)
        next_room = self.get_next_room(solution, exhibit_and_door_graph, next_door, current_room, visited_rooms)
        solution.add_node(next_door)
        visited_rooms.add(next_room)

        return next_door, next_room, all_unexplored_exhibits, visited_rooms

    def _remove_node_safe(self, node_list, node):
        try:
            node_list.remove(node)
        except ValueError:
            pass
        finally:
            return node_list

    def get_next_room(self, solution, exhibit_and_door_graph, next_door, current_room, visited_rooms):
        """ Gets next room based on the neighbours of the door.
        Valid neighbours are those that are not in the current room.
        With a valid neighbour node then we can access its 'room' attribute to get the next room.
        Only next room valid if it has not been explored yet or if there is no other way to exit the current
        room other than repeating a room.
        """
        neighbor_exhibits_of_door = self.get_unexplored_neighbor_exhibits_not_in_room(solution, exhibit_and_door_graph, next_door, current_room)
        new_room = current_room

        if len(neighbor_exhibits_of_door) == 0:
            new_room = exhibit_and_door_graph[solution.current][next_door]["room"]
            return new_room

        doors_in_current_room = exhibit_and_door_graph.graph['n_doors_per_room'][f'{current_room}']

        for exhibit in neighbor_exhibits_of_door:
            room_candidate = exhibit_and_door_graph[next_door][exhibit]["room"]

            if room_candidate != current_room and room_candidate not in visited_rooms:
                new_room = room_candidate
                break
            elif room_candidate != current_room and room_candidate in visited_rooms and doors_in_current_room == 1:
                new_room = room_candidate
                break
        return new_room

    def get_unexplored_exhibits_in_room(self, solution, exhibit_and_door_graph, starting_node_in_current_room, current_room,
                                        all_rooms=False):
        # node_type is "exhibit" or "door"
        available_exhibits = []

        if all_rooms:
            for n in exhibit_and_door_graph.nodes():
                if exhibit_and_door_graph.nodes[n]["type"] == "exhibit" and n not in solution:
                    available_exhibits.append(n)
        else:
            available_exhibits = [nb for nb in exhibit_and_door_graph.neighbors(starting_node_in_current_room)
                                  if (nb not in solution and exhibit_and_door_graph.nodes[nb]["type"] == "exhibit"
                                      and exhibit_and_door_graph.nodes[nb]["room"] == current_room)]


        return available_exhibits

    def get_unexplored_neighbor_exhibits_not_in_room(self, solution, exhibit_and_door_graph, starting_node_in_current_room, current_room):
        available_exhibits = [nb for nb in exhibit_and_door_graph.neighbors(starting_node_in_current_room)
                              if (nb not in solution and exhibit_and_door_graph.nodes[nb]["type"] == "exhibit"
                                  and exhibit_and_door_graph.nodes[nb]["room"] != current_room)]
        return available_exhibits

    def _get_unexplored_door_nodes(self, solution, exhibit_and_door_graph, starting_node_in_current_room, current_room):
        doors_in_current_room = exhibit_and_door_graph.graph['n_doors_per_room'][f'{current_room}']
        available_neighbours = [nb for nb in exhibit_and_door_graph.neighbors(starting_node_in_current_room)
                                if (nb not in solution) or
                                (nb in solution and doors_in_current_room == 1)]

        if len(available_neighbours) == 0:
            # Got to a door that leads to a room that has
            # already been visited, this leads to a block. So
            # in these cases we have to open again all search possibilities
            # to try to find the room that we missed
            available_neighbours  = [nb for nb in exhibit_and_door_graph.neighbors(starting_node_in_current_room)]

        available_doors = [n for n in available_neighbours if exhibit_and_door_graph.nodes[n]["type"] == "door"]


        return available_doors


    def _get_unexplored_nodes(self, graph, solution):
        """
        Returns the possible transition nodes (neighbors) for the current node.
        """
        # return [name for name, _ in graph[solution.current].items() if name not in solution]
        return [n for n in graph.nodes() if n not in solution]

    def _choose_destination(self, graph, solution, neighbours_of_current):
        """
        Returns next node to visit
        """
        current = solution.current

        if len(neighbours_of_current) == 1:
            return neighbours_of_current[0]

        if solution.previous in neighbours_of_current:
            # Avoid ant going back and forth between two nodes,
            # unless there is no other option
            self._remove_node_safe(neighbours_of_current, solution.previous)

        scores = self._get_scores(graph, current, neighbours_of_current)
        return self._choose_node(neighbours_of_current, scores)

    def _get_scores(self, graph, current, destinations):
        """
        Return scores for the given destinations
        """
        scores = []
        for node in destinations:
            edge = graph[current][node]
            score = self._score_edge(edge)
            scores.append(score)
        return scores

    def _choose_node(self, choices, scores):
        """
        Return one of the choices
        """
        total = sum(scores)
        cumdist = list(itertools.accumulate(scores)) + [total]
        chosen_node_index = bisect.bisect(cumdist, random.random() * total)
        return choices[min(chosen_node_index, len(choices) - 1)]

    def _score_edge(self, edge):

        weight = edge['weight']
        pheromone = edge['pheromone']

        if weight == 0:
            return sys.float_info.max
        eta = 1.0 / weight
        tau = pheromone

        return (tau ** self.alpha) * (eta ** self.beta)


class Colony:

    def __init__(self, alpha=1, beta=3):
        self.alpha = alpha
        self.beta = beta

    def __repr__(self):
        return f'{self.__class__.__name__}(alpha={self.alpha}, beta={self.beta})'

    def get_ants(self, num_ants):
        return [Ant(**vars(self)) for i in range(num_ants)]