from copy import deepcopy

from mmas.ant import Colony
from mmas.solvers import Solver


class AlgorithmController:

    def __init__(self, graph_manager=None, alpha=1, beta=3,
                 rho=0.02, pts=False, pts_factor=0.5, num_ants=100,
                 start='D1-1', objectives=[]):

        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.pts = pts
        self.pts_factor = pts_factor
        self.num_ants = num_ants
        self.start = start
        self.objectives = objectives
        self.graph = self._config_graph(graph_manager)

        self.algorithm_states = []

    def _config_graph(self, graph_manager):
        g = graph_manager.door_graph
        graph_manager.initialise_pheromones(g, self.start, self.objectives, self.rho)
        return g

    def compute_initial_iterations(self, limit=200):

        print(f'Starting mmas algorithm with {limit} initial iterations.')

        colony = Colony(alpha=self.alpha, beta=self.beta)
        solver = Solver(rho=self.rho, pts=self.pts, pts_factor=self.pts_factor)
        state = solver.solve(self.graph, colony=colony,
                             n_ants=self.num_ants, limit=limit,
                             start=self.start, objectives=self.objectives)
        self.graph = state.graph
        self.algorithm_states.append(state)
        return state.record

    def compute_next_iterations(self, limit=200):

        if not self.algorithm_states:
            raise Exception("No saved states. You must run the algorithm for the first time using start()")

        print(f'Continuing mmas algorithm execution with {limit} more iterations.')
        # Retrieve the  most recent state
        last_state = deepcopy(self.algorithm_states[-1])
        solver = Solver(rho=self.rho, pts=self.pts, pts_factor=self.pts_factor, state=last_state)
        next_state = solver.solve(self.graph, limit=limit)
        self.graph = next_state.graph
        self.algorithm_states.append(next_state)

    def manual_pheromone_update(self, edge):
        u, v = edge
        self.graph[u][v]['pheromone'] *= 5

    def pheromone_info(self, edges):
        if not edges:
            for u, v in self.graph.edges():
                print(f'Edge {u}->{v}, pheromone: {self.graph[u][v]["pheromone"]}')
        else:
            for edge in edges:
                u, v = edge
                print(f'Edge {u}->{v}, pheromone: {self.graph[u][v]["pheromone"]}')