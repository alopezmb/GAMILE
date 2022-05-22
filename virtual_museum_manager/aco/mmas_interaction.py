from aco.objects.Ant import Ant


class MMASInteraction:

    def __init__(self, alpha=0, beta=0, rho=0.0, n_ants=0, exhibits=None, pBest=0.0):
        """
        MinMax Ant System Interaction
        """

        self.finish_iteration = None
        self._alpha = alpha
        self._beta = beta
        self._rho = rho
        self._n_ants = n_ants
        self.exhibits = exhibits
        self._pBest = pBest

        self.ants = [Ant(i, len(self.exhibits), 0, []) for i in range(0, n_ants)]
        self.distances = []
        self.pheromones = []

    def global_pheromone_update_min_max(self):
        best_ant_index = self.find_best_ant().id
        self._evaporate_pheromones()
        increase_factor = (1.0/self.ants[best_ant_index].tour_length) * self._rho
        self.deposit_pheromones(best_ant_index, increase_factor)
        self._finish_iteration()

    def find_best_ant(self):
        pass

    def _ant_init_update(self):
        return None

    def _init_ants(self):

        return None

    def _calculate_transition_probability(self, random_location: bool):
        pass

    def _exploration_decision(self):
        pass

    def deposit_pheromones(self, best_ant_index, increase_factor):
        pass

    def _finish_iteration(self):
        pass

    def _evaporate_pheromones(self):
        pass

    def _complete_tours(self):
        pass






