
import json
from copy import deepcopy
import sys


def load_floorplan(floorplan_path):
	with open(floorplan_path, 'r') as f:
		ramen_floorplan = json.load(f)

	return deepcopy(ramen_floorplan)

def create_json(data, json_path):
	with open(json_path, "w") as jsonfile:
		json.dump(data, jsonfile, indent=2)


def convert(ramen_floorplan_path, mesa_output_floorplan_path=None, get_dimensions=False):
	ramen_floorplan = load_floorplan(ramen_floorplan_path)

	# Corners
	corners = ramen_floorplan["floorplan"]["corners"]

	if get_dimensions:
		x_vals, y_vals = zip(*[(val["x"], val["y"]) for (k,val) in corners.items()])
		max_x = max(x_vals)
		max_y = max(y_vals)
		print(f"Grid Dimensions (x,y) = ({max_x},{max_y})")
		return

	# Doors
	doors = list(filter(lambda x: x["item_name"] == "Open Door", ramen_floorplan["items"]))

	# Paintings (Exhibits)
	paintings = list(filter(lambda x: x["item_name"] != "Open Door", ramen_floorplan["items"]))

	# Count number of different rooms
	room_count = len(set([c.split("-")[-1] for c in corners.keys()]))

	# Parse rooms
	rooms = []
	for i in range(1, room_count + 1):
		corners_of_room = [corners[k] for k in corners.keys() if (k.split("-")[-1] == str(i))]
		doors_of_room = list(filter(lambda d: d["name"].split("-")[0][1:] == str(i), doors))
		paintings_of_room = list(filter(lambda x: x["room"] == f'room_{i}', paintings))
		
		room_name = f"room_{i}"
		connected_rooms = set()
		formatted_doors = []
		formatted_exhibits = []
		
		# Parse paintings of the room
		for exhibit in paintings_of_room:
			formatted_painting = {
				"name":exhibit["item_name"],
				"location": {"x":exhibit["xpos"],"y":exhibit["zpos"]}
			}
			formatted_exhibits.append(formatted_painting)
		# Parse doors of the room
		for door in doors_of_room:
			
			horizontal_door = False
			vertical_door = False
			connected_room_id = door["name"].split("-")[-1]
			connected_rooms.add(int(connected_room_id))


			# The only door that has the orientation property is the main entrance door
			if door.get("orientation") is not None:
				vertical_door = door["orientation"] == "vertical"
				horizontal_door = door["orientation"] == "horizontal"

			# Applies to rest of doors
			else:
				
				reciprocal_door_name = f"D{connected_room_id}-{i}"
				reciprocal_door = list(filter(lambda d: d["name"] == reciprocal_door_name, doors))[0]
				
				vertical_door = (0 <= abs(door["xpos"] - reciprocal_door["xpos"]) < 2) and (door["zpos"] == reciprocal_door["zpos"])
				horizontal_door = (0 < abs(door["zpos"] - reciprocal_door["zpos"]) < 2) and (door["xpos"] == reciprocal_door["xpos"])

			if not vertical_door and not horizontal_door:
				door_name = door["name"]
				print(f"Problems with door {door_name} and its reciprocal {reciprocal_door_name}")
			midpoint_x = door["xpos"]
			midpoint_y = door["zpos"]
			door_width = door["width"]

			start_x = end_x = start_y = end_y = 0

			if vertical_door:
				start_x = end_x = midpoint_x
				start_y = midpoint_y - (door_width/2)
				end_y = midpoint_y + (door_width/2)

			elif horizontal_door:
				start_y = end_y = midpoint_y
				start_x = midpoint_x - (door_width/2)
				end_x = midpoint_x + (door_width/2)

			prepared_door = {
			"p_start": {"x":start_x,"y":start_y},
			"p_end": {"x":end_x,"y":end_y},
			"connects_to_room": connected_room_id
			}
			formatted_doors.append(prepared_door)

		room_dict = {
		"room_name": room_name,
		"vertices": corners_of_room,
		"connected_rooms": sorted(list(connected_rooms)),
		"doors": formatted_doors,
		"exhibits": formatted_exhibits
		}
		rooms.append(room_dict)

	create_json(rooms, mesa_output_floorplan_path)
	return rooms


# Execute conversion function
ramen_floorplan_path = sys.argv[1]
second_argument = sys.argv[2]

if second_argument == "--get-grid-dimensions":
	# Reuse convert function to return dimensions
	convert(ramen_floorplan_path, get_dimensions=True)

elif ".json" in second_argument:
	# This will adapt the ramen floorplan to a valid mesa floorplan
	convert(ramen_floorplan_path, mesa_output_floorplan_path=second_argument)
else:
	print("ERROR! Specify a valid second argument!")