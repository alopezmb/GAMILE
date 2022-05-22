
class AlgorithmController:

    def __init__(self, model, exhibit_data=None):
        """
        Ant Algorithm Controller
        """
        self.algorithm = None
        self.model = model  # cargo el modelo para poder tener acceso a sus metodos
        self.N_ITERS = 5
        self.pheromone_history = []
        self.current_iteration = 0
        self.user_tour = []
        self.user_tour_rooms = []
        self._has_init_finished = None
        self.rooms = []
        self._next_best_room_position = ()  # tuple
        self.best_tour_length = 0.0
        self.best_tour = []
        self.best_iteration = 0
        self.best_algorithm_iteration = 0
        self.best_algorithm_length = 0.0
        self.best_algorithm_tour = ""

        self.exhibit_data = exhibit_data  # [ exhibits, room_graph]

    def _start(self):
        self.pheromone_history = None  # Creo nueva lista de objetos feromona
        self._has_init_finished = False
        self.rooms = []  # cargo lista de salas == ciudades --> INIT TSP

    def init(self):
        self.current_iteration = 0
        self.user_tour = []
        self.pheromone_history = []
        self.user_tour_rooms = []
        self.algorithm = None  # cargo algoritmo
        self.algorithm.rooms = self.rooms
        self.algorithm.init()

        # Precalculations for algorithm only solution

        self.do_n_iterations(len(self.rooms) * self.N_ITERS)
        self.best_algorithm_length = self.best_tour_length
        self.best_algorithm_tour = self.best_tour
        self._has_init_finished = True
        self.algorithm.init()

    def do_n_iterations(self, n_iterations):
        for i in range(0, n_iterations):
            self.algorithm.iteration()

    def on_exhibit_watched(self, exhibit_agent_id):
        self.do_n_iterations(self.N_ITERS)
        self.current_iteration += self.N_ITERS
        self.user_tour.append(exhibit_agent_id)
        self.user_tour_rooms.append(self.rooms[exhibit_agent_id])

        # eliminar obra, pero la elimino del mapa y del scheduler ? creo que no

        pheromones = self.algorithm.pheromones[exhibit_agent_id]
        new_pheromone = None # PheromoneEntry(self._get_remaining_max_index(pheromones),
                         #              exhibit_agent_id, self.current_iteration,
                         #              self._get_remaining_pheromones(pheromones))

        self.pheromone_history.append(new_pheromone)
        
        max = self._get_remaining_max(pheromones)
        min = self._get_remaining_min(pheromones)

        for idx, pheromone in enumerate(pheromones):
            if abs(max - pheromone < 1e-6 * max):
                # tengo que hacer algo con las obras aqui, acceder al array de obras
                self._next_best_room_position = None

        self._update_pheromones()

    def _update_pheromones(self):
        if len(self.user_tour) < 2:
            return None
        room_a = self.user_tour[-1]
        room_b = self.user_tour[-2]
        self.algorithm.pheromones.increase_pheromones(room_a, room_b,
                                                      self.algorithm.pheromones.get_pheromone(room_a, room_b))

    def _get_remaining_max(self, pheromone_list):

        pheromone_list_tmp = pheromone_list[:]
        for visited_room_idx in self.user_tour:
            pheromone_list_tmp[visited_room_idx] = float('-inf')

        return max(pheromone_list_tmp)

    def _get_remaining_pheromones(self, pheromone_list):

        pheromone_list_tmp = pheromone_list[:]

        for visited_room_idx in self.user_tour:
            pheromone_list_tmp[visited_room_idx] = float('-inf')

        return pheromone_list_tmp

    def _get_remaining_max_index(self, pheromone_list):

        pheromone_list_tmp = pheromone_list[:]

        for visited_room_idx in self.user_tour:
            pheromone_list_tmp[visited_room_idx] = float('-inf')

        max_value = max(pheromone_list_tmp)
        return pheromone_list_tmp.index(max_value)

    def _get_remaining_min(self, pheromone_list):

        pheromone_list_tmp = pheromone_list[:]
        for visited_room_idx in self.user_tour:
            pheromone_list_tmp[visited_room_idx] = float('+inf')

        return min(pheromone_list_tmp)
