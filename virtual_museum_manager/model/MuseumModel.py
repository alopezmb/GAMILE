"""
Flockers
=============================================================
A Mesa implementation of Craig Reynolds's Boids flocker model.
Uses numpy arrays to represent vectors.
"""
import itertools
import os

import random
import time
from datetime import timedelta

import numpy as np
from copy import deepcopy

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation

from agents.Exhibit import Exhibit
from agents.Visitor import Visitor
from space.Door import Door
from space.Room import Room

from aco.aco_final.AlgorithmController import AlgorithmController
from aco.aco_final.MuseumGraphManager import MuseumGraphManager
from utils.utils import print_trace


class Museum(Model):
    """
    Cálculo de rutas en el museo utilizando Machine Learning interactivo (iML).
    """

    def __init__(
            self,
            n_exhibits=30,
            visitor_radius=6,
            exhibit_radius=4,
            width=100,
            height=100,
            rooms_json=None
    ):
        """
        Create a new Museum model.
       """
        super().__init__()
        self.schedule = RandomActivation(self)
        self.space = ContinuousSpace(width, height, False)
        self.running = True

        self.grid_dimensions = [width, height]
        self.n_exhibits = n_exhibits
        self.visitor_radius = visitor_radius,
        self.exhibit_radius = exhibit_radius
        self.rooms_json = rooms_json
        self.obstacle_map = []

        self.exhibit_agents = []
        self.chosen_exhibits = []
        self.n_choices = 2

        # Functions to execute at the instantiation time of the model
        self.create_floor_plan()

        self.visitor = None
        self.visitor_start_pos = np.array((1450, 2300))  # 1450 2300
        self.make_visitor()

        self.place_exhibits()

        # self.choose_exhibits_and_place_all()

        # self.choose_exhibits_and_place_agents(["room_13"])
        self.graph_manager = MuseumGraphManager(self.rooms_json)

        # self.config_mmas()
        # self.initial_iterations = 10
        # self.next_iterations = 5
        # record_solution = self.mmas_controller.compute_initial_iterations(limit=10)
        # print("Best solution found:")
        # print(f'cost: {record_solution.cost}')
        # print(f'path: {record_solution.path}')
        # print()

    def make_visitor(self):
        """
        Create self.population agents, with random positions and starting headings.
        Create N exhibits with random positions
        Create a visitor that will "consume" the artworks
        """

        # Create Visitor (only one agent, will start at museum entrance)

        pos = self.visitor_start_pos
        print_trace(f"visitor starting point {pos}")

        visitor = Visitor(self.next_id(), self, pos)
        self.visitor = visitor
        self.visitor.start_timestamp = time.time()
        self.visitor.node_times = [self.visitor.start_timestamp]

        start_door = Door(start_point=(2, 8), end_point=(5, 10), room_origin=1, room_destination=1)
        d_name = start_door.name.replace("_", "-")
        start_door.name = f'D{d_name}'
        self.visitor.edge_path = [start_door]

        # Locate visitor in a room (room_number,idx) and assign room object to visitor
        self.visitor.room = self.locate_visitor()
        print_trace("START: visitor is in {0}".format(self.visitor.room.name))

        self.space.place_agent(self.visitor, pos)
        self.schedule.add(self.visitor)

    def create_floor_plan(self):

        rooms_json = deepcopy(self.rooms_json)

        for room in rooms_json:

            vertices_list = room['vertices'] if 'vertices' in room.keys() else []
            exhibit_list = room['exhibits'] if 'exhibits' in room.keys() else []
            door_list = room['doors'] if 'doors' in room.keys() else []

            # Create room object
            room_object = Room(name=room['room_name'],
                               vertices=vertices_list,
                               doors=door_list,
                               exhibits=exhibit_list,
                               grid_dimensions=(self.space.x_max, self.space.y_max))

            # Now, create the Exhibit agents
            exhibit_dicts = room_object.exhibits  # Get list of exhibit dictionaries

            for ex in exhibit_dicts:
                agent_id = self.next_id()
                x, y = ex['location']

                exhibit = Exhibit(unique_id=agent_id, model=self,
                                  name=ex["name"], room_name=room_object.name,
                                  pos=(x, y), selected=False)

                self.exhibit_agents.append(exhibit)

            self.obstacle_map.append(room_object)

    def locate_visitor(self, locate_start=False):
        """
        Function that checks where is the visitor located, and thus outputs
        the room in which the visitor is located.

        Args
        ----------
        locate_start (bool): turn flag on if this call is the initial call to locate visitor, which means
                             we will be looking for the starting room.

        Returns
        -------
        room (Room): room where visitor is located in.
        """

        for room in self.obstacle_map:
            if room.inside_room(self.visitor.pos):
                return room

    def step(self):
        self.schedule.step()

    def place_exhibits(self):
        for exhibit in self.exhibit_agents:
            self.insert_agent(exhibit, exhibit.pos)

    def choose_exhibits_and_place_all(self):
        exhibit_choices = random.sample(self.exhibit_agents, self.n_choices)
        # exhibit_choices_unmodified = deepcopy(exhibit_choices)

        for chosen_exhibit in exhibit_choices:
            chosen_exhibit.selected = True
            self.insert_agent(chosen_exhibit, chosen_exhibit.pos)

        for exhibit in self.exhibit_agents:
            if exhibit not in exhibit_choices:
                self.insert_agent(exhibit, exhibit.pos)

    def insert_agent(self, agent, pos):
        self.space.place_agent(agent, pos)
        self.schedule.add(agent)

    def choose_exhibits_and_place_agents(self, rooms_to_chose_from):

        chosen_exhibits_tmp = []
        for exhibit in self.exhibit_agents:

            # Initial MMAS exhibit selection
            if exhibit.room_name in rooms_to_chose_from:
                # Change "selected" property to True so that we can distinguish the chosen exhibits in the map
                exhibit.selected = True
                chosen_exhibits_tmp.append(exhibit)

            # Place exhibit in the map and schedule it. All of the exhibits are placed.
            self.space.place_agent(exhibit, exhibit.pos)
            self.schedule.add(exhibit)

        if chosen_exhibits_tmp:
            for key, group in itertools.groupby(chosen_exhibits_tmp, lambda x: x.room_name):
                room_object = next((room for room in self.obstacle_map if room.name == key), None)
                exs = list(group)

                # Check if there are exhibits to watch from room 1 (starting room)
                if room_object.name == "room_1":
                    # If there are, append door entrance to dictionary
                    exs = [self.entrance_door] + exs[:]

                self.chosen_exhibits.append({"room": room_object, "exhibits": exs})

    def config_mmas(self, initial_iters=10):
        # Parameters
        print("*************************")
        print("Configuring MMAS iML...")
        print("*************************")

        if os.path.isfile("../virtual_museum_iml.pickle"):
            print("Found a saved graph")
            g = None
        else:
            print("Creating new graph for the first time...")
            gm = MuseumGraphManager(self.rooms_json)
            g = gm.door_graph
            gm.initialise_pheromones(g)

        params = {
            'graph': g,
            'alpha': 1,
            'beta': 1,
            'rho': 0.02,
            'pts': True,
            'pts_factor': 1,
            'num_ants': len(g.nodes()),
            'start_node': 'D1-1',
            'start_room': 1
        }

        ac = AlgorithmController(**params)
        # ac.compute_initial_iterations(limit=initial_iters)
        return ac

    def get_tour_data(self):
        print("*******************************")
        print("      Retrieving Tour Data     ")
        print("*******************************")

        graph = self.graph_manager.door_graph
        clean_edge_data = self._create_tuples(self.visitor.edge_path)
        clean_time_data = self._create_tuples(self.visitor.node_times)
        tour_data = []
        w = 0
        for idx, edge in enumerate(clean_edge_data):
            u, v = edge
            u_str = u.name
            v_str = v.name
            edge_data = graph[u_str][v_str]
            edge_t = clean_time_data[idx]
            t0, t1 = edge_t
            t0_good = str(timedelta(seconds=(t0 - self.visitor.start_timestamp)))
            t1_good = str(timedelta(seconds=(t1 - self.visitor.start_timestamp)))
            edge_weight = edge_data['weight']
            w += edge_data['weight']
            data_item = {"origin": u_str, "destination": v_str, "origin_timestamp": t0_good,
                         "destination_timestamp": t1_good, "edge_weight": edge_weight}
            tour_data.append(data_item)
        return tour_data

    def _create_tuples(self, lst):

        # Create tuples by iterating through the list
        result = []
        for i in range(0, len(lst) + 1):
            if i + 1 < len(lst):
                result.append((lst[i], lst[i + 1]))

        return result
