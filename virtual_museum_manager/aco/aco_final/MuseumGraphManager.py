import networkx as nx
import numpy as np
import re
from itertools import combinations
# import matplotlib.pyplot as plt


class MuseumGraphManager:

    def __init__(self, rooms_map, rooms_subset=None, grid_dimensions=[100, 70]):

        """
        Graph of Rooms

        Parameters
        ----------
        rooms_map: map of the rooms

        """
        self.grid_dimensions = grid_dimensions

        self._rooms = self._prepare_room_map(rooms_map, rooms_subset=rooms_subset)
        self.room_graph = self._create_room_graph()
        self.door_graph = self._create_door_graph()

    def _prepare_room_map(self, rooms_map, rooms_subset=None):

        rooms_prepared = []
        rooms_filtered = filter(lambda x: x['room_name'] in rooms_subset, rooms_map) if rooms_subset is not None else rooms_map
        for room in rooms_filtered:

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
                min_room_n, max_room_n = sorted([room_number_origin, int(door['connects_to_room'])])
                d = {"location": location,
                     "connects_to_room": door['connects_to_room'],
                     "name": "D{a}-{b}".format(a=min_room_n,
                                               b=max_room_n),
                     "type": "door"
                     }
                # Add prepared door to list of doors that make up the room
                doors_prepared.append(d)

            # Prepare exhibits
            for exhibit in room['exhibits']:
                # Create new exhibit dictionary based on mods made to the original.
                e = {
                    "location": self._denormalize_coordinate(exhibit['location']),
                    "name": exhibit['name'],
                    "type": "exhibit"
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
        g.graph.update({"n_doors_per_room": {}})
        link_list = []
        nodes_list = []
        for room in self._rooms:  # ([self._rooms[5]] + [self._rooms[12]]):
            # [self._rooms[0]] + [self._rooms[2]] + [self._rooms[4]] + [self._rooms[5]] +  [self._rooms[12]]
            # Make all possible two pair combinations inside the room.
            # (door-door, exhibits-exhibit, door-exhibit)
            room_number_origin = int(re.findall(r"\d+", room['room_name'])[0])
            node_combinations = list(combinations(room['doors'] + room['exhibits'], 2))

            for node1, node2 in node_combinations:

                n1_with_info = (node1['name'], {'type': node1['type'], 'room': room_number_origin})
                n2_with_info = (node2['name'], {'type': node2['type'], 'room': room_number_origin})

                if n1_with_info not in nodes_list:
                    nodes_list.append(n1_with_info)
                if n2_with_info not in nodes_list:
                    nodes_list.append(n2_with_info)

                distance = np.linalg.norm(node1['location'] - node2['location'])
                n1_name, n2_name = node1['name'], node2['name']
                link = (n1_name, n2_name, {'weight': np.around(distance, 2), 'pheromone': 0,
                                           'room': room_number_origin})
                # print(link)
                link_list.append(link)

            doors_in_room = len(room['doors'])
            g.graph['n_doors_per_room'][f'{room_number_origin}'] = doors_in_room

        # Add links to graph (this automatically creates nodes)
        g.add_nodes_from(nodes_list)
        g.add_edges_from(link_list)
        return g



    def initialise_pheromones(self, graph):
        initial_pheromone_value = 0.9
        for edge in graph.edges():
            u, v = edge
            graph[u][v]['pheromone'] = initial_pheromone_value


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
                if int(room_number) != node:
                    # Prevent having links between the same room
                    link = (int(room_number), node, {'weight': 1})
                    link_list.append(link)

        # Add links to graph (automatically creates nodes)
        g.add_edges_from(link_list)

        for room in self._rooms:
            room_number = int(re.findall(r"\d+", room['room_name'])[0])
            exhibit_names = [exhibit['name'] for exhibit in room['exhibits']]
            door_names = [door['name'] for door in room['doors']]
            g.nodes[room_number]['elements'] = exhibit_names + door_names
        return g

    def get_elements_in_room(self, room_node,):
        pass


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

    def plot(self, graph, edge_attribute='weight'):
        pos = nx.spring_layout(graph)
        plt.figure(figsize=(15, 15))
        attribute_labels = nx.get_edge_attributes(graph, edge_attribute)
        nx.draw(graph, pos, edge_color='black', width=1, linewidths=1, node_size=500,
                node_color='pink', alpha=0.9, labels={node: node for node in graph.nodes()})
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=attribute_labels, font_color='red')
        plt.axis('off')
        plt.show()