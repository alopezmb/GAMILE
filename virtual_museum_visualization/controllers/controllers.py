##################################
# ######## Controllers ###########
##################################
import inspect

import bcrypt
import secrets

from flask import make_response, render_template, session, redirect

from models.RamenVisitor import RamenVisitor
from settings.settings import Users


####################################################################
# Helper functions
###################################################################

def render(template, **kwargs):
    headers = {'Content-type': 'text/html'}
    return make_response(render_template(template, **kwargs), 200, headers)


# ######### REGISTRATION ############

def process_registration(username, password, password_confirmation):
    user_exists = Users.count_documents({'username': username}, limit=1) == 1

    # Check if username already exists
    if user_exists:
        return False, 'Username already in use.'

    # Username is new but pwd verification is incorrect
    if not user_exists and (password != password_confirmation):
        return False, 'Passwords do not match'

    # Everything okay, register new user
    if not user_exists and (password == password_confirmation):
        hashedpwd = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(14))
        Users.insert_one({'username': username,
                          'password': hashedpwd.decode('utf8'),
                          'score': 0, 'time': 0})
        return True, f"Username {username} successfully registered"


# ######### LOGOUT ############
def process_logout():
    session['token'] = ''

# ######### LOGIN ############

def process_login(username, password):
    user = Users.find_one({'username': username})
    match = False

    if user:
        match = bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
    if match:
        usertoken = secrets.token_hex(16)
        session['token'] = usertoken
        Users.update_one({"_id": user["_id"]},
                         {"$set": {
                             "auth_token": usertoken
                         }
                         })
        return True

    return False


def login_required(func):
    def wrapper(*args, **kwargs):
        usertoken = session.get('token')
        user = Users.find_one({'auth_token': usertoken})
        if user is not None and usertoken is not None:
            return func(*args)
        else:
            return redirect('/login')

    return wrapper


def login_class(cls):
    for name, function in inspect.getmembers(cls, inspect.isfunction):
        setattr(cls, name, login_required(function))
    setattr(cls, 'get_user', get_request_user)
    return cls


#################################################
#                Request Data Processing        #
# ###############################################

def get_request_user(*args):
    usertoken = session.get('token')
    user = Users.find_one({'auth_token': usertoken})
    return RamenVisitor(user)


#################################################
#                Mesa Manager                   #
# ###############################################

# with open('simulation/resources/space.json', 'r') as f:
#     rooms_json = json.load(f)
#
# museum_model_parameters = {
#     "visitor_radius": 6,
#     "exhibit_radius": 2,
#     "width": 2900,
#     "height": 2400,
#     "rooms_json": rooms_json
# }
#
#
# class MesaManager:
#     def __init__(self):
#
#         self.model_params = museum_model_parameters
#         self.model_class = Museum
#         self.model = None  # instance of model class
#
#     def reset_model(self):
#         """ Reinstantiate the model object, using the current parameters. """
#         model_params = {}
#         for key, val in self.model_params.items():
#             model_params[key] = val
#         self.model = self.model_class(**model_params)
#         print("Museum model initialized!", flush=True)
#
#     def execute_instructions(self, instructions):
#         """
#         @param instructions: dict of instructions.
#         """
#         instruction_type = instructions.get("instruction_type")
#         instruction_data = instructions.get("data")
#
#         if instruction_type == "set_position":
#             position = instruction_data.get("position")
#             self.set_position(position)
#
#         elif instruction_type == "move_visitor":
#             axis_rotation_angle = instruction_data.get("rotation")
#             movement_direction = instruction_data.get("direction")
#             modulus_multiplier = instruction_data.get("modulus_multiplier")
#             return self.move_with_obstacles(movement_direction, axis_rotation_angle, modulus_multiplier)
#
#         elif instruction_type == "watch_painting":
#             painting_name = instruction_data.get("painting_name")
#             self.model.visitor.watch_painting(painting_name)
#
#     def move_with_obstacles(self, movement_direction, axis_rotation_angle, modulus_multiplier):
#
#         can_visitor_move = self.model.visitor.calculate_movement_vector(
#             movement_direction, float(axis_rotation_angle),
#             modulus_multiplier=float(modulus_multiplier))
#         self.model.step()
#
#         print_trace(f"New position: {self.model.visitor.pos}")
#         response_payload = {'movement_allowed': can_visitor_move}
#         return response_payload
#
#     def set_position(self, position):
#         pos_x = position["x"]
#         pos_y = position["y"]
#         new_pos = np.array((pos_x, pos_y))
#         self.model.visitor.pos = new_pos
