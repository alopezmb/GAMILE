import functools
import itertools
import random
import math


class State:
    def __init__(self, graph, ants, limit, n_ants, colony):
        self.graph = graph
        self.ants = ants
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
            print(f'New record at iteration: {iteration}: ({best.cost})')
            self.previous_record = self.record
            self.record = best
            self.best_iteration = iteration
        self.best = best


@functools.total_ordering
class Solution:

    def __init__(self, graph, start, ant=None):
        self.graph = graph
        self.start = start
        self.current = start
        self.previous = start
        self.cost = 0
        self.path = []
        self.nodes = [start]
        self.visited_nodes = set(self.nodes)

    def __iter__(self):
        return iter(self.path)

    def __eq__(self, other):
        return self.cost == other.cost

    def __lt__(self, other):
        return self.cost < other.cost

    def __contains__(self, node):
        return node in self.visited_nodes or node == self.current

    def add_node(self, node):
        self.nodes.append(node)
        self.visited_nodes.add(node)
        self._add_node(node)

    def _add_node(self, node):
        edge = self.current, node
        edge_attributes = self.graph[self.current][node]
        self.path.append(edge)
        self.cost += edge_attributes['weight']
        self.previous = self.current
        self.current = node

    def close(self):
        self._add_node(self.start)


class Solver:

    def __init__(self, rho=0.02, pts_factor=0.1, pBest=0.05, pts=True, state=None, print_msg=False):
        self.rho = rho
        self.pts_factor = pts_factor
        self.pBest = pBest
        self.pts = pts
        self.state = state
        self.print_msg = print_msg

    def __repr__(self):
        return f'{self.__class__.__name__}(rho={self.rho}, pts_factor={self.pts_factor})'

    def solve(self, graph, colony=None, n_ants=None, limit=None, start_room=1, start_node='D1-1'):
        # best = None
        # for solution in self.optimize(graph, colony, n_ants, limit, start, objectives):
        #    best = solution
        # return self.state, best
        self.optimize(graph, colony, n_ants, limit, start_room, start_node)
        return self.state

    def optimize(self, graph, colony, n_ants, limit, start_room, start_node):

        if not self.state:
            ants = colony.get_ants(n_ants)
            state = State(graph=graph, ants=ants, limit=limit, n_ants=n_ants, colony=colony)
        else:
            state = self.state
            state.limit = limit
            ants = state.ants

        # loop to yield increasingly better solutions
        looper = range(state.current_iteration,
                       limit + state.current_iteration) if limit is not None else itertools.count()

        for i in looper:
            if i % 20 == 0:
                print("Iteration: ", i)

            solutions = self._construct_solutions(state, start_room, start_node)
            solutions, ants = self._order_solutions_ants(solutions, ants)

            state.solutions, state.ants = solutions, ants

            iteration_best_solution = state.solutions[0]
            state.set_best(iteration_best_solution, i)

            self._update_pheromones(state)

            state.current_iteration = i + 1

        self.state = state

    def _construct_solutions(self, state, start_room, start_door):
        return [ant.construct_tour(state.graph, start_room=start_room, start_door=start_door) for ant in state.ants]

    def _order_solutions_ants(self, solutions, ants):
        # We need to order the solutions found by their cost (and still know its associated ant)
        data = list(zip(solutions, range(len(ants)), ants))
        data.sort()
        # Ordered list of solutions and their corresponding ants
        solutions_ordered_costs, _, ants = zip(*data)

        return solutions_ordered_costs, ants

    def _update_pheromones(self, state):

        best_solution = state.best  # iteration best # self._best_solution_type_choice(state)
        self._update_pheromone_bounds(state, best_solution)

        for edge in state.graph.edges:
            # Evaporate and increase pheromone trails
            self._evaporate_and_increase_pheromone_trails(state, edge, best_solution)

            # Update pheromone trail lower and upper bounds
            self._adjust_pheromone_trail_limits(state, edge)

            # Pheromone trail smoothing
            # self._pheromone_trail_smoothing(state,edge)

    def sigmoid(self, x, a=1, b=1):
        # Sigmoid-like function with parameters 'a' and 'b'
        return 1 / (1 + math.exp(-a * (x - b)))

    def biased_weighted_random(self, number):
        # Use the sigmoid-like function to calculate the threshold
        # Bias max at 300
        threshold = self.sigmoid(number, a=0.02, b=150)  # Adjust 'a' and 'b' for desired bias

        # Generate a random number between 0 and 1
        random_number = random.random()

        # Compare the random number to the threshold
        if random_number < threshold:
            return 'global_best'
        else:
            return 'iteration_best'

    def __best_solution_type_choice(self, state):
        # Choose between global best and iteration best
        choices = {'iteration_best': state.solutions[0], 'global_best': state.record}
        t = state.current_iteration
        type = self.biased_weighted_random(t)
        # choice_made = print(f'{type} used at iteration {t}')
        return choices[type]

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
        if edge in best_solution.path:  # and old_pheromone != 0 :
            pheromone_increase = 1.0 / best_length

        state.graph.edges[edge]['pheromone'] = (1 - self.rho) * old_pheromone + pheromone_increase

    def _adjust_pheromone_trail_limits(self, state, edge):

        # Adjust pheromone trails to limits
        updated_pheromone_trail = state.graph.edges[edge]['pheromone']

        if updated_pheromone_trail != 0:

            if updated_pheromone_trail < state.current_lower_bound:
                updated_pheromone_trail = state.current_lower_bound

            elif updated_pheromone_trail > state.current_upper_bound:  # updated_pheromone_trail / upper_bound < 100:
                updated_pheromone_trail = state.current_upper_bound

            else:
                updated_pheromone_trail = updated_pheromone_trail

            state.graph.edges[edge]['pheromone'] = updated_pheromone_trail

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

    def _update_pheromone_bounds(self, state, best_solution):
        best_length = best_solution.cost
        n = len(state.graph.nodes())

        upper_bound = 1.0 / ((1 - self.rho) * best_length)
        lower_bound = (upper_bound * (1.0 - (self.pBest ** (1.0 / n)))) / (
                ((n / 2.0) - 1) * (self.pBest ** (1.0 / n)))
        state.current_upper_bound = upper_bound
        state.current_lower_bound = lower_bound
