import itertools
import bisect
import random
import sys

from mmas.solvers import Solution


class Ant:

    def __init__(self, alpha=1, beta=3):
        self.alpha = alpha
        self.beta = beta

    def construct_tour(self, graph, start, chosen_exhibits):
        """
        Construct a tour including all chosen exhibits
        """

        solution = Solution(graph, start, ant=self)
        objectives = list(set(chosen_exhibits[:]))

        while objectives:
            neighbors = self._get_neighbor_nodes(graph, solution)  # neighbors (connected by links)
            # print(f"neighbors of current node ({solution.current}):")
            # print(neighbors)
            node = self._choose_destination(graph, solution.current, neighbors)
            # print(f"chosen node = {node}")
            solution.add_node(node)
            # print(f"objectives before = {objectives}")
            if node in objectives:
                objectives.remove(node)
            # print(f"objectives after = {objectives}")
            # solution.close()
        return solution

    def _get_neighbor_nodes(self, graph, solution):
        """
        Returns the possible transition nodes (neighbors) for the current node.
        """
        return [name for name, _ in graph[solution.current].items()
                if name not in solution]

    def _choose_destination(self, graph, current, unvisited):
        """
        Returns next node to visit
        """
        if len(unvisited) == 1:
            return unvisited[0]
        scores = self._get_scores(graph, current, unvisited)
        return self._choose_node(unvisited, scores)

    def _get_scores(self, graph, current, destinations):
        """
        Return scores for the given destinations
        """
        scores = []
        for node in destinations:
            edge = graph[current][node]
            score = self._score_edge(edge)
            scores.append(score)
        return scores

    def _choose_node(self, choices, scores):
        """
        Return one of the choices
        """
        total = sum(scores)
        cumdist = list(itertools.accumulate(scores)) + [total]
        chosen_node_index = bisect.bisect(cumdist, random.random() * total)
        return choices[min(chosen_node_index, len(choices) - 1)]

    def _score_edge(self, edge):

        weight = edge['weight']
        pheromone = edge['pheromone']

        if weight == 0:
            return sys.float_info.max
        eta = 1.0 / weight
        tau = pheromone

        return (tau ** self.alpha) * (eta ** self.beta)


class Colony:

    def __init__(self, alpha=1, beta=3):
        self.alpha = alpha
        self.beta = beta

    def __repr__(self):
        return f'{self.__class__.__name__}(alpha={self.alpha}, beta={self.beta})'

    def get_ants(self, num_ants):
        return [Ant(**vars(self)) for i in range(num_ants)]