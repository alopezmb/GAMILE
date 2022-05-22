import functools
from itertools import count


class State:

    def __init__(self, graph, ants, limit, n_ants, colony):
        self.graph = graph
        self.ants = ants
        self.n_ants = n_ants
        self.current_iteration = 0
        self.current_upper_bound = 0
        self.current_lower_bound = 0
        self.limit = limit
        self.colony = colony
        self.solutions = None
        self.record = None
        self.previous_record = None
        self.is_new_record = False
        self.best = None
        self.best_iteration = 0
        self.last_smoothing_iteration = 0

        self.start = None
        self.objectives = None

    def set_best(self, best, iteration):
        self.is_new_record = self.record is None or best < self.record
        if self.is_new_record:
            self.previous_record = self.record
            self.record = best
            self.best_iteration = iteration
        self.best = best


@functools.total_ordering
class Solution:

    def __init__(self, graph, start, ant=None):
        self.graph = graph
        self.start = start
        self.ant = ant
        self.current = start
        self.previous = start
        self.cost = 0
        self.path = []
        self.nodes = [start]
        self.visited_objectives = set()

    def __iter__(self):
        return iter(self.path)

    def __eq__(self, other):
        return self.cost == other.cost

    def __lt__(self, other):
        return self.cost < other.cost

    def __contains__(self, node):
        return node in self.visited_objectives or node == self.current

    def add_node(self, node):
        self.nodes.append(node)

        if "E" in node:
            self.visited_objectives.add(node)

        edge = self.current, node
        edge_attributes = self.graph[self.current][node]
        self.path.append(edge)
        self.cost += edge_attributes['weight']
        self.previous = self.current
        self.current = node


class Solver:

    def __init__(self, rho=0.02, pts_factor=0.1, pBest=0.05, pts=True, state=None):
        self.rho = rho
        self.pts_factor = pts_factor
        self.pBest = pBest
        self.pts = pts
        self.state = state

    def __repr__(self):
        return f'{self.__class__.__name__}(rho={self.rho}, pts_factor={self.pts_factor})'

    def solve(self, graph, colony=None, n_ants=None, limit=None, start=None, objectives=None):

        self.optimize(graph, colony, n_ants, limit, start, objectives)
        return self.state

    def optimize(self, graph, colony, n_ants, limit, start, objectives):

        if not self.state:
            ants = colony.get_ants(n_ants)
            state = State(graph, ants, limit, n_ants,colony)
            state.start = start
            state.objectives = objectives
        else:
            state = self.state
            ants = state.ants
            start = state.start
            objectives = state.objectives

        # loop to yield increasingly better solutions
        looper = range(state.current_iteration,
                       limit + state.current_iteration) if limit is not None else count()

        for i in looper:

            print(f'Current Iteration: {i}')
            solutions = self._construct_solutions(state, start, objectives)

            # print(f'Iteration {i}: GRAPH BEFORE UPDATE')
            # for node1, node2, data in graph.edges.data():
            #    print(f'{node1}-{node2}:{data}')
            # print()

            solutions, ants = self._order_solutions_ants(solutions, ants)

            # print(f'Iteration {i}: AFTER ORDERING')
            # for s in solutions_ordered_costs:
            #    print(s.cost)
            # print()

            state.solutions, state.ants = solutions, ants

            iteration_best_solution = state.solutions[0]
            state.set_best(iteration_best_solution, i)

            self._update_pheromones(state)

            # print(f'Iteration {i} best solution:')
            # print(iteration_best_solution.cost)
            # print(iteration_best_solution.path)
            # print()

            # print(f'Iteration {i}: GRAPH AFTER PHEROMONE UPDATE')
            # for node1, node2, data in graph.edges.data():
            #    print(f'{node1}-{node2}:{data}')
            # print("----------------------")
            # print()

            if state.is_new_record:
                print(f'Best iteration so far: {i}')
                print(f'cost: {state.best.cost}')
                print(f'path: {state.best.path}')
                print("----------------------")
                print()
                # yield state.record
            state.current_iteration = i + 1

        self.state = state

    def _construct_solutions(self, state, start, objectives):
        return [ant.construct_tour(state.graph, start, objectives) for ant in state.ants]

    def _order_solutions_ants(self, solutions, ants):
        # We need to order the solutions found by their cost (and still know its associated ant)
        data = list(zip(solutions, range(len(ants)), ants))
        data.sort()
        # Ordered list of solutions and their corresponding ants
        solutions_ordered_costs, _, ants = zip(*data)

        return solutions_ordered_costs, ants

    def _update_pheromones(self, state):

        best_solution = self._best_solution_type_choice(state)

        for edge in state.graph.edges:
            # Evaporate and increase pheromone trails
            self._evaporate_and_increase_pheromone_trails(state, edge, best_solution)

            # Update pheromone trail lower and upper bounds
            self._adjust_pheromone_trail_limits(state, edge, best_solution)

            # Pheromone trail smoothing
            self._pheromone_trail_smoothing(state, edge)

    def _best_solution_type_choice(self, state):

        # Choose between global best and iteration best

        t = state.current_iteration

        if t <= 25:
            global_best_frequency = 0
        elif 25 < t <= 75:
            global_best_frequency = 8
        elif 75 < t <= 125:
            global_best_frequency = 5
        elif 125 < t <= 250:
            global_best_frequency = 4
        else:
            global_best_frequency = 3

        if global_best_frequency > 0 and t % global_best_frequency == 0:
            best_solution = state.record
            # print(f'Global best solution (it {t})')
        else:
            best_solution = state.solutions[0]
            # print(f'Iteration best solution (it {t})')

        return best_solution

    def _evaporate_and_increase_pheromone_trails(self, state, edge, best_solution):

        best_length = best_solution.cost

        pheromone_increase = 0
        old_pheromone = state.graph.edges[edge]['pheromone']

        # Only increase pheromone in edges that are relevant
        if edge in best_solution.path and old_pheromone != 0:
            pheromone_increase = 1.0 / best_length

        state.graph.edges[edge]['pheromone'] = (1 - self.rho) * old_pheromone + pheromone_increase

    def _adjust_pheromone_trail_limits(self, state, edge, best_solution):

        # Adjust pheromone trails to limits
        updated_pheromone_trail = state.graph.edges[edge]['pheromone']

        if updated_pheromone_trail != 0:

            best_length = best_solution.cost
            n = len(state.graph.nodes())

            upper_bound = 1.0 / (self.rho * best_length)
            lower_bound = (upper_bound * (1.0 - (self.pBest ** (1.0 / n)))) / ((n / 2.0) * (self.pBest ** (1.0 / n)))

            # print(f' Upper bound: {upper_bound}')
            # print(f' Lower bound: {lower_bound}')

            if updated_pheromone_trail < lower_bound:
                updated_pheromone_trail = lower_bound

            elif updated_pheromone_trail > upper_bound:
                updated_pheromone_trail = upper_bound

            else:
                updated_pheromone_trail = updated_pheromone_trail

            state.graph.edges[edge]['pheromone'] = updated_pheromone_trail

            state.current_upper_bound = upper_bound
            state.current_lower_bound = lower_bound

    def _pheromone_trail_smoothing(self, state, edge):

        # PTS lift-minimum approach
        freq = 50
        pheromone_trail = state.graph.edges[edge]['pheromone']

        cond1 = self.pts
        cond2 = abs(state.best_iteration - state.current_iteration) >= freq
        cond3 = abs(state.last_smoothing_iteration - state.current_iteration) >= freq
        cond4 = pheromone_trail != 0

        if cond1 and cond2 and cond3 and cond4:
            print("smoothing")
            state.last_smoothing_iteration = state.current_iteration
            smoothing_factor = self.pts_factor
            lower_bound = state.current_lower_bound
            upper_bound = state.current_upper_bound
            new_lower_bound = lower_bound + smoothing_factor * (upper_bound - lower_bound)

            pheromone_trail = state.graph.edges[edge]['pheromone']

            if pheromone_trail < new_lower_bound:
                pheromone_trail = lower_bound
                state.graph.edges[edge]['pheromone'] = pheromone_trail

            state.current_lower_bound = new_lower_bound

            # pheromone trail reinitialization
            # tengo que explorarlo, o cojo la formula (un poco movida) o compruebo si no mejora la
            # busqueda en x iteraciones, y con ese criterio sencillo digo que reinicio los trails
