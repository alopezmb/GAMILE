import networkx as nx
import numpy as np
import re
from itertools import combinations
import matplotlib.pyplot as plt


class MuseumGraphManager:

    def __init__(self, rooms_map, grid_dimensions):

        """
        Graph of Rooms

        Parameters
        ----------
        rooms_map: map of the rooms

        """
        self.grid_dimensions = grid_dimensions

        self._rooms = self._prepare_room_map(rooms_map)
        self.room_graph = self._create_room_graph()
        self.door_graph = self._create_door_graph()

    def _prepare_room_map(self, rooms_map):

        rooms_prepared = []

        for room in rooms_map:

            # Extract room number
            room_number_origin = int(re.findall(r"\d+", room['room_name'])[0])

            # Lists to be filled with the respective adapted door and exhibit structures
            doors_prepared = []
            exhibits_prepared = []

            # Prepare doors
            for door in room['doors']:
                p_start = self._denormalize_coordinate(door['p_start'])
                p_end = self._denormalize_coordinate(door['p_end'])

                # Location of door as a single point (midpoint of line formed by p_start and p_end)
                location = (p_start + p_end) / 2.0

                # Create new door dictionary based on mods made to the original.
                min_room_n, max_room_n = sorted([room_number_origin, door['connects_to_room']])
                d = {"location": location,
                     "connects_to_room": door['connects_to_room'],
                     "name": "D{a}-{b}".format(a=min_room_n,
                                               b=max_room_n)
                     }
                # Add prepared door to list of doors that make up the room
                doors_prepared.append(d)

            # Prepare exhibits
            for exhibit in room['exhibits']:
                # Create new exhibit dictionary based on mods made to the original.
                e = {
                    "location": self._denormalize_coordinate(exhibit['location']),
                    "name": exhibit['name'].replace("Exhibit ", "E")
                }

                # Add prepared exhibit to list of exhibits that make are inside this room
                exhibits_prepared.append(e)

            # Prepare the room with the prepared doors and exhibits
            r = {"room_name": room['room_name'],
                 "connected_rooms": room['connected_rooms'],
                 "doors": doors_prepared,
                 "exhibits": exhibits_prepared
                 }

            # Add the prepared room to the list of prepared rooms
            rooms_prepared.append(r)

        return rooms_prepared

    def _denormalize_coordinate(self, coordinate):
        """
        Denormalizes the specified coordinate, since elements from the space.json file
        are expressed as percentages.

        Parameters
        ----------
        coordinate (x,y) :

        Returns
        -------
        point (Numpy array) : denormalized coordinate.
        """
        x_max = self.grid_dimensions[0]
        y_max = self.grid_dimensions[1]

        # Denormalize
        _x = round((coordinate['x'] / 100.0) * x_max)
        _y = round((coordinate['y'] / 100.0) * y_max)

        # Make sure denormalized values stay within permitted range
        # i.e. x_max = 50 means the maximum value is not 50, but 49 (50 values 0 to 49).
        x = x_max if _x == x_max else _x
        y = y_max if _y == y_max else _y

        point = np.array((x, y))

        return point

    def _create_door_graph(self):
        """
        Create a Graph of Doors
        """

        # create empty graph
        g = nx.Graph()
        link_list = []

        for room in self._rooms:  # ([self._rooms[5]] + [self._rooms[12]]):
            # [self._rooms[0]] + [self._rooms[2]] + [self._rooms[4]] + [self._rooms[5]] +  [self._rooms[12]]
            # Make all possible two pair combinations inside the room.
            # (door-door, exhibits-exhibit, door-exhibit)

            node_combinations = list(combinations(room['doors'] + room['exhibits'], 2))
            # print(f' Doors for {room["room_name"]}:')
            # print(room['doors'])
            # print()
            # print(f' Exhibits for {room["room_name"]}:')
            # print(room['exhibits'])
            # print('----------------------------------')
            # print()
            # print(f'Combinations for {room["room_name"]}:')
            for node1, node2 in node_combinations:
                distance = np.linalg.norm(node1['location'] - node2['location'])
                n1, n2 = node1['name'], node2['name']
                link = (n1, n2, {'weight': np.around(distance, 2), 'pheromone': 0})
                # print(link)
                link_list.append(link)

        # Add links to graph (this automatically creates nodes)
        g.add_edges_from(link_list)

        return g

    def initialise_pheromones(self, graph, start, objectives, rho):
        cost_nn_heuristic = self._nearest_neighbor_heuristic(graph, start, objectives)
        initial_pheromone_value = 1.0 / (rho * cost_nn_heuristic)
        for edge in graph.edges():
            u, v = edge

            # door-door links must have phermone
            if 'D' in u and 'D' in v:
                graph[u][v]['pheromone'] = initial_pheromone_value

            # exhibit-exhibit links that involve the objectives must have pheromone
            elif (u in objectives and v in objectives):
                graph[u][v]['pheromone'] = initial_pheromone_value

                # exhibit-door links that involve objectives must have pheromone
            elif (u in objectives or v in objectives) and ('D' in u or 'D' in v):
                graph[u][v]['pheromone'] = initial_pheromone_value

            # links that are initially not relevant
            # some of these will later be significant as the visitor travels towards interesting exhibits
            # not located in the initial objectives
            else:
                graph[u][v]['pheromone'] = 0

    def _create_room_graph(self):
        """
        Create a Graph of Rooms.
        This is a simple graph.

        """

        # create empty graph
        g = nx.Graph()
        link_list = []
        # dist = np.linalg.norm(point1 - point2)

        for room in self._rooms:
            room_number = re.findall(r"\d+", room['room_name'])[0]
            for node in room['connected_rooms']:
                link = (int(room_number), node, {'weight': 1})
                link_list.append(link)

        # Add links to graph (automatically creates nodes)
        g.add_edges_from(link_list)
        return g

    def get_shortest_path(self, graph, origin, dest):
        return nx.shortest_path_length(graph, source=origin, target=dest, weight='weight')

    def get_neighbors(self, graph, node, neighbor_type=""):

        if (neighbor_type == 'door'):
            return [name for name, props in graph[node].items() if "D" in name]
        elif (neighbor_type == 'exhibit'):
            return [name for name, props in graph[node].items() if "E" in name]
        else:
            return graph[node]

    def _nearest_neighbor_heuristic(self, graph, start, objectives):
        sps = [nx.shortest_path_length(graph, source=start,
                                       target=objective, weight='weight') for objective in objectives]
        furthest_exhibit = max(sps)
        sum_paths = sum(sps)
        estimated_cost = sum_paths / 1.8
        # print(estimated_cost)
        return estimated_cost

    def plot(self, graph, edge_attribute):
        pos = nx.spring_layout(graph)
        plt.figure(figsize=(15, 15))
        attribute_labels = nx.get_edge_attributes(graph, edge_attribute)
        nx.draw(graph, pos, edge_color='black', width=1, linewidths=1, node_size=500,
                node_color='pink', alpha=0.9, labels={node: node for node in graph.nodes()})
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=attribute_labels, font_color='red')
        plt.axis('off')
        plt.show()