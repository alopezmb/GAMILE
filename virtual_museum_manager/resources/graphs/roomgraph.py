import networkx as nx
import re
import matplotlib.pyplot as plt
from copy import deepcopy
import numpy as np


class RoomGraph:

    def __init__(self, rooms_map):

        """
        Graph of Rooms class

        Parameters
        ----------
        rooms_map: map of the rooms

        """
        # self.grid_dimensions = grid_dimensions
        # self.room_denormalized = self._denormalize_room_map(rooms_map)
        self.graph = self._create_graph(rooms_map)

    def _denormalize_room_map(self, rooms_map):

        rooms_map_copy = deepcopy(rooms_map)

        for room in rooms_map_copy:
            for door in room['doors']:
                x_start = door['p_start']['x']
                y_start = door['p_start']['y']

                x_end = door['p_end']['x']
                y_end = door['p_end']['y']

                p_start = self._denormalize_coordinate({'x': x_start, 'y': y_start})
                p_end = self._denormalize_coordinate({'x': x_end, 'y': y_end})

                location = (p_start + p_end) / 2.0

                door = {"location": location,
                        "connects_to_room": door['connects_to_room']
                        }

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

    def _create_graph(self, rooms_map):

        """
        Create a Graph of Rooms

        Parameters
        ----------
        rooms_map: map of the rooms

        """

        # create empty graph
        g = nx.Graph()
        link_list = []

        for room in rooms_map:
            room_number = re.findall(r"\d+", room['room_name'])[0]
            for node in room['connected_rooms']:
                link = (int(room_number), node, {'weight': 1})
                link_list.append(link)

        # Add links to graph (automatically creates nodes)
        g.add_edges_from(link_list)
        return g

    def get_shortest_path(self, origin, dest):
        return nx.dijkstra_path(self.graph, source=origin, target=dest)

    def plot_graph(self):
        pos = nx.spring_layout(self.graph)
        plt.figure(figsize=(10, 10))
        distance_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw(self.graph, pos, edge_color='black', width=1, linewidths=1, node_size=500,
                node_color='pink', alpha=0.9, labels={node: node for node in self.graph.nodes()})
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=distance_labels, font_color='red')
        plt.axis('off')
        plt.show()

