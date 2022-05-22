from aco.mmas_interaction import MMASInteraction


class MMAS:

    def __init__(self, alpha=0, beta=0, q=0.0, n_ants=0, pBest=0.0):
        """
        Min Max Algorithm Implementation
        """

        # private
        self._alpha = alpha
        self._beta = beta
        self._q = q
        self._n_ants = n_ants
        self._pBest = pBest

        self._pheromone_trail_initial_value = 0.1

        self._algorithm_step = 0
        self._current_iteration = 0

        # accessible from outside classes
        self.ant_interaction = None
        self.rooms = []
        self.tour_length = 0
        self.best_tour = []
        self.best_iteration = []

    def init(self):
        self.ant_interaction = MMASInteraction(self.alpha, self.beta, self.q, self.n_ants, self.rooms, self._pBest)
        self.tour_length = float('+inf')
        self._check_best_tour()
        self._algorithm_step = 1

    def iteration(self):
        self._current_iteration += 1
        self.ant_interaction.update_ants()
        self.ant_interaction.update_pheromones()
        self._check_best_tour()

    def step(self):
        if self.ant_interaction.update_ants_stepwise(self._algorithm_step):
            self._algorithm_step = 1
            self.ant_interaction.update_pheromones()
            self._check_best_tour()
        else:
            self._algorithm_step += 1

    def _check_best_tour(self):
        best_ant = self.ant_interaction.find_best_ant()
        tour_length_best_ant = best_ant.tour_length

        if tour_length_best_ant < self.tour_length:
            self.tour_length = tour_length_best_ant
            self.best_tour = []
            for tour in best_ant.tour:
                self.best_tour.append(tour)
                self.best_iteration = self._current_iteration

            return True
        else:
            return False
