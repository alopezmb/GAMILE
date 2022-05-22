import json
from abc import ABC
import numpy as np
from tornado.web import RequestHandler
from tornado.escape import json_decode
from utils.utils import print_trace

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

	def get(self):
		response = 'Museum API!'
		self.write(response)

	def post(self):
		# Retrieve movement instructions
		instructions = json_decode(self.request.body)

		# Execute instructions appropriately
		self.execute_instructions(instructions)

	def execute_instructions(self, instructions):
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
			self.reset_simulation()

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

	def reset_simulation(self):
		self.mesa_manager.reset_model()
		self.mesa_manager.render_model()
		self.model.step()

	def options(self, *args):
		self.set_status(204)
		self.finish()


api_handlers = [(r"/api/v1?", MuseumAPI)]
