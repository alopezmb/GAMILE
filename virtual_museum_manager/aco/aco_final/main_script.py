from aco_final.AlgorithmController import AlgorithmController
from aco_final.MuseumGraphManager import MuseumGraphManager
import json

with open('../resources/space.json', 'r') as f:
    rooms_json = json.load(f)

gm = MuseumGraphManager(rooms_json) # rooms_subset=["room_6", "room_13"]
params = {
    'graph_manager': gm,
    'alpha' : 1,
    'beta': 2,
    'rho' : 0.02,
    'pts': True,
    'pts_factor':1,
    'num_ants': len(gm.door_graph.nodes()),
    'start_room': 4,
    'start_node': 'D3-4'
}

controller = AlgorithmController(**params)

# %debug --breakpoint aco_final/ant.py:42 controller.compute_initial_iterations(limit=1)



