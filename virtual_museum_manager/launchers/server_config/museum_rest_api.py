import json
from abc import ABC

import numpy as np
from tornado.web import RequestHandler
from tornado.escape import json_decode
from utils.utils import print_trace
from pymongo import MongoClient
import os

CONNECTION_URI = os.getenv("MONGO_CONNECT")
client = MongoClient(CONNECTION_URI, connect=False)
db = client.virtualmuseum
Users = db['users']

"""
    API ENDPOINTS

        /api/v1/
            Returns the movement of all occupants as a list of positions [x, y].

"""


class MuseumAPI(RequestHandler, ABC):

    def set_default_headers(self):
        # self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def initialize(self, mesa_manager):
        self.mesa_manager = mesa_manager
        self.model = mesa_manager.model
        self.username = ""

    def get(self):
        response = 'Museum API!'
        self.write(response)

    async def post(self):
        # Retrieve movement instructions
        instructions = json_decode(self.request.body)
        print("************************************")
        print("*       RECEIVED INSTRUCTIONS:     *")
        print(instructions)
        print("***********************************+")
        print("\n")

        # Execute instructions appropriately
        await self.execute_instructions(instructions)

    async def execute_instructions(self, instructions):
        """
        @param instructions: dict of instructions.
        """
        instruction_type = instructions.get("instruction_type")
        instruction_data = instructions.get("data")

        if instruction_type == "set_position":
            position = instruction_data.get("position")
            self.set_position(position)

        elif instruction_type == "move_visitor":
            axis_rotation_angle = instruction_data.get("rotation")
            movement_direction = instruction_data.get("direction")
            modulus_multiplier = instruction_data.get("modulus_multiplier")
            self.move_with_obstacles(movement_direction, axis_rotation_angle, modulus_multiplier)

        elif instruction_type == "watch_painting":
            painting_name = instruction_data.get("painting_name")
            self.model.visitor.watch_painting(painting_name)
            response_payload = {'travel_score': self.model.visitor.travel_score}
            self.write(json.dumps(response_payload))

        elif instruction_type == "reset":
            await self.reset_simulation()

        elif instruction_type == "start_tour":
            self.start_tour(instruction_data)
            self.write(json.dumps({'message': 'tour started'}))

        elif instruction_type == "finish_tour":
            self.finish_tour(instruction_data)
            self.write(json.dumps({}))

        else:
            self.set_status(400)
            self.write('Error: unknown instructions')

    def move_with_obstacles(self, movement_direction, axis_rotation_angle, modulus_multiplier):

        can_visitor_move = self.model.visitor.calculate_movement_vector(
            movement_direction, float(axis_rotation_angle),
            modulus_multiplier=float(modulus_multiplier))
        self.model.step()

        print_trace(f"New position: {self.model.visitor.pos}")
        response_payload = {'movement_allowed': can_visitor_move, 'travel_score': self.model.visitor.travel_score}
        self.write(json.dumps(response_payload))

    def set_position(self, position):
        pos_x = position["x"]
        pos_y = position["y"]
        new_pos = np.array((pos_x, pos_y))
        self.model.visitor.pos = new_pos
        self.write("Position successfully set!")

    async def reset_simulation(self):
        # if len(self.model.visitor.edge_path) > 4:
        #    # First store our important stuff
        #    self.model.mmas_controller.save_graph()
        #    self.model.dump_results()
        #    self.model.mmas_controller.print_best_sol()

        self.mesa_manager.reset_model()
        self.mesa_manager.render_model()
        self.model.step()

    def start_tour(self, instruction_data):
        pass
        # self.username = instruction_data.get('username')
        # Users.find_one({'username': username})
        # print("USER FOUND:")
        # print(user)
        # if user:
        #    Users.update_one({"_id": user["_id"]},
        #                     {"$set": {"visits": ['myvisit']}})
        # user = Users.find_one({'username': username})
        # print("UPDATED USER:")
        # print(user)

    def finish_tour(self, instruction_data):
        username = instruction_data.get('username')
        user = Users.find_one({'username': username})
        print('\n')
        print("*******************************************")
        print(f'Saving tour data for user: {user}')
        if user:
            user_tour_data = self.model.get_tour_data()
            Users.update_one({"_id": user["_id"]},
                             {"$push": {"visits": user_tour_data}})
            print("User Tour Data saved in database:")
            user = Users.find_one({'username': username})
            print(user['visits'][-1])
            print("*********************************")
            print('\n')

    def options(self, *args):
        self.set_status(204)
        self.finish()


api_handlers = [(r"/api/v1?", MuseumAPI)]
