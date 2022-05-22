from .server_config.main_server_configurations import MuseumServer

import json
from model.MuseumModel import Museum
from visualization.SimpleContinuousModule import SimpleCanvas
from agents.Exhibit import Exhibit
from agents.Visitor import Visitor


visitor_radius = 6
exhibit_radius = 2

with open('resources/space.json', 'r') as f:
    rooms_json = json.load(f)


def agent_portrayal(agent):
    portrayal = {}

    if type(agent) is Visitor:
        return {"type": "visitor", "r": visitor_radius,
                "Color": "yellow", "path_color": 'orange'}

    if type(agent) is Exhibit:

        color = "Red"
        opacity = 0.5

        if agent.popularity == "popular":
            color = "Purple"
        if agent.selected:
            color = "Green"
            opacity = 1
            return {"type": "exhibit", "r": 3, "Filled": "true", "Color": color, "Opacity": opacity}

        return {"type": "exhibit", "r": exhibit_radius, "Filled": "true", "Color": color, "Opacity": opacity}

    return portrayal


# height,width
museum_canvas = SimpleCanvas(agent_portrayal, 2900, 2400)
model_params = {
    "visitor_radius": visitor_radius,
    "exhibit_radius": exhibit_radius,
    "width": 2900,
    "height": 2400,
    "rooms_json": rooms_json
}

server = MuseumServer(Museum, [museum_canvas], "SIMLER", model_params)
