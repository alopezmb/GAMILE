import pickle
from copy import deepcopy

from aco.aco_final.ant import Colony
from aco.aco_final.solvers import Solver


class AlgorithmController:

    def __init__(self, graph=None, alpha=1, beta=3,
                 rho=0.02, pts=False, pts_factor=0.5, num_ants=100, start_room=1, start_node='D1-1'):

        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.pts = pts
        self.pts_factor = pts_factor
        self.num_ants = num_ants
        self.graph = None
        self.algorithm_states = []
        self.start_room = start_room
        self.start_node = start_node

        if graph is None:
            self.load_graph()
        else:
            self.graph = graph


    def _config_graph(self, graph_manager):
        g = graph_manager.door_graph
        graph_manager.initialise_pheromones(g)
        return g

    def compute_initial_iterations(self, limit=200):

        print(f'Starting mmas algorithm with {limit} initial iterations.')

        colony = Colony(alpha=self.alpha, beta=self.beta)
        solver = Solver(rho=self.rho, pts=self.pts, pts_factor=self.pts_factor)
        state = solver.solve(self.graph, colony=colony, n_ants=self.num_ants, limit=limit,
                             start_room=self.start_room, start_node=self.start_node)
        self.graph = state.graph
        self.algorithm_states.append(state)

        print(f'Finished computing the initial {limit} iterations')

    def compute_next_iterations(self, limit=15):

        if not self.algorithm_states:
            raise Exception("No saved states. You must run the algorithm for the first time using start()")

        print(f'Continuing mmas algorithm execution with {limit} more iterations.')
        # Retrieve the  most recent state
        last_state = deepcopy(self.algorithm_states[-1])
        solver = Solver(rho=self.rho, pts=self.pts, pts_factor=self.pts_factor, state=last_state)
        next_state = solver.solve(self.graph, limit=limit)
        self.graph = next_state.graph
        self.algorithm_states.append(next_state)
        print(f"Done {limit} iterations. Waiting for more feedback")

    def manual_pheromone_update(self, edge):
        print("Manual pheromone update of edge:", edge)
        u, v = edge
        self.graph[u][v]['pheromone'] *= 250

    def manual_pheromone_and_continue_iters(self, edge, limit=15):
        self.manual_pheromone_update(edge)
        self.compute_next_iterations(limit=limit)

    def pheromone_info(self, edges=None):
        if not edges:
            for u, v in self.graph.edges():
                print(f'Edge {u}->{v}, pheromone: {self.graph[u][v]["pheromone"]}')
        else:
            for edge in edges:
                u, v = edge
                print(f'Edge {u}->{v}, pheromone: {self.graph[u][v]["pheromone"]}')

    def save_graph(self):
        print("*******************************")
        print("Saving iML GRAPH with knowledge")
        print("*******************************")
        state = self.algorithm_states[-1]
        pickle.dump(state.graph, open('../virtual_museum_iml.pickle', 'wb'))
        print("Pickle Where is it")

    def load_graph(self):
        print("********************")
        print("Loading iML GRAPH!!")
        print("********************")
        self.graph = pickle.load(open('../virtual_museum_iml.pickle', 'rb'))

    def print_best_sol(self):
        state = self.algorithm_states[-1]
        best_cost = state.record.cost
        best_path = state.record.path
        print(best_cost)
        print(best_path)

