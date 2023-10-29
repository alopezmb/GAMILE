from aco_final.AlgorithmController import AlgorithmController
from aco_final.MuseumGraphManager import MuseumGraphManager
import json

with open('../resources/space.json', 'r') as f:
    rooms_json = json.load(f)

gm = MuseumGraphManager(rooms_json) # rooms_subset=["room_6", "room_13"]
g = gm.door_graph
gm.initialise_pheromones(g)
params = {
    'graph': g,
    'alpha' : 1,
    'beta': 2,
    'rho' : 0.02,
    'pts': True,
    'pts_factor':1,
    'num_ants': len(g.nodes()),
    'start_room': 1,
    'start_node': 'D1-1'
}

controller = AlgorithmController(**params)

controller.compute_initial_iterations(limit=50)
controller.print_best_sol()
controller.save_graph()


import pickle


