from mesa.visualization.ModularVisualization import VisualizationElement

from agents.Visitor import Visitor


class SimpleCanvas(VisualizationElement):
    local_includes = ["visualization/simple_continuous_canvas.js"]
    portrayal_method = None
    canvas_height = 500
    canvas_width = 500

    def __init__(self, portrayal_method, canvas_height=500, canvas_width=500):
        """
        Instantiate a new SimpleCanvas
        """
        self.portrayal_method = portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = "new Simple_Continuous_Module({}, {})".format(
            self.canvas_width, self.canvas_height
        )
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        space_state = []
        obstacle_state = []
        # agents
        for obj in model.schedule.agents:

            portrayal = self.portrayal_method(obj)

            # Normalize position vector in order to fit any canvas dimensions
            x, y = _normalize_coordinate(coordinate=obj.pos, x_min=model.space.x_min,
                                         x_max=model.space.x_max, y_min=model.space.y_min, y_max=model.space.y_max)
            portrayal["x"] = x
            portrayal["y"] = y

            if type(obj) is Visitor:

                normalized_path = []
                for pos in obj.total_path:
                    x_path, y_path = _normalize_coordinate(coordinate=pos, x_min=model.space.x_min,
                                                           x_max=model.space.x_max, y_min=model.space.y_min,
                                                           y_max=model.space.y_max)

                    normalized_path.append([x_path, y_path])
                    portrayal["path"] = normalized_path

            space_state.append(portrayal)

        # obstacles: rooms, walls, etc
        for room in model.obstacle_map:
            portrayal = self.portrayal_method(room)

            vertices_normalized = []
            doors_normalized = []

            for vertex in room.vertices:
                # Normalize position vector in order to fit any canvas dimensions
                x, y = _normalize_coordinate(coordinate=vertex, x_min=model.space.x_min,
                                             x_max=model.space.x_max, y_min=model.space.y_min,
                                             y_max=model.space.y_max)
                vertices_normalized.append([x, y])

            # room.doors = []  # apaño :
            for door in room.doors:
                x_start, y_start = _normalize_coordinate(coordinate=door.start_point, x_min=model.space.x_min,
                                                         x_max=model.space.x_max, y_min=model.space.y_min,
                                                         y_max=model.space.y_max)

                x_end, y_end = _normalize_coordinate(coordinate=door.end_point, x_min=model.space.x_min,
                                                     x_max=model.space.x_max, y_min=model.space.y_min,
                                                     y_max=model.space.y_max)
                doors_normalized.append([(x_start, y_start), (x_end, y_end)])

            # Save corner and door info in portrayal
            portrayal["vertices"] = vertices_normalized
            portrayal["doors"] = doors_normalized
            obstacle_state.append(portrayal)

        # this is the data object that is passed to the render function in simple_continuous_canvas.js
        return [space_state, obstacle_state]


def _normalize_coordinate(coordinate=None, x_min=None, x_max=None, y_min=None, y_max=None):
    # Normalize position vector in order to fit any canvas dimensions
    x, y = coordinate
    x = (x - x_min) / (x_max - x_min)
    y = (y - y_min) / (y_max - y_min)

    return x, y
