import json
import math
import heapq
import time
import requests
from Utils import Point
from urllib import request
from Team import Team
from Fare import Fare, FareType

# Server details
server_ip = "10.216.29.48"
server = f"http://{server_ip}:5000"
authKey = "32"
team = 32

class PathFinder:
    def calculate_distance(self, coord1, coord2):
        # Ensure both coord1 and coord2 are Point objects
        if isinstance(coord1, Point) and isinstance(coord2, Point):
            return coord1.dist(coord2)  # Use the dist method of the Point class
        else:
            # If coord1 or coord2 isn't a Point, use the old method (not likely to happen, but it's good to have)
            return math.sqrt((coord2[0] - coord1[0]) ** 2 + (coord2[1] - coord1[1]) ** 2)


    def find_closest_intersection(self, fare_location, intersections):
        closest_intersection = None
        closest_distance = float('inf')

        # Ensure fare_location is a Point object
        if isinstance(fare_location, dict):  # If it's still a dictionary
            fare_location = Point(fare_location['x'], fare_location['y'])  # Convert to a Point object

        # Calculate the distance from the fare location (Point) to each intersection (Point)
        for intersection, coord in intersections.items():
            distance = self.calculate_distance((fare_location.x, fare_location.y), (coord.x, coord.y))
            if distance < closest_distance:
                closest_distance = distance
                closest_intersection = intersection

        return closest_intersection


    # Function to create the graph by adding distances between intersections in all 4 directions
    def create_graph(self, intersections):
        # Initialize a directed graph with nodes and directed edges
        graph = {}

        # Initialize graph with empty dictionaries for each node
        for intersection in intersections:
            graph[intersection] = {}

        # Define the one-way directed paths (edges)
        directed_paths = {
            "Waddle_Aquatic": ["Waterfoul_Aquatic", "Waddle_Migration"],
            "Waterfoul_Aquatic": ["Feather_Aquatic", "Waterfoul_Migration", "Waddle_Aquatic"],
            "Waterfoul_Migration": ["Waddle_Migration", "Waterfoul_Pondside", "Feather_Migration"],
            "Waterfoul_Pondside": ["Waddle_Pondside", "Feather_Pondside", "Waterfoul_Circle"],
            "Feather_Aquatic": ["Beak_Aquatic", "Feather_Migration", "Waterfoul_Aquatic"],
            "Beak_Aquatic": ["Feather_Aquatic", "Beak_Migration", "Mallard_Migration"],
            "Beak_Tail": ["Circle_Tail", "Beak_Drake"],
            "Mallard_Migration": ["Beak_Aquatic", "Beak_Migration", "Mallard_Pondside"],
            "Mallard_Pondside": ["Mallard_Migration", "Beak_Pondside", "Mallard_Dabbler"],
            "Mallard_Dabbler": ["Mallard_Pondside", "Mallard_Duckling", "Beak_Dabbler"],
            "Mallard_Drake": ["Mallard_Dabbler"],
            "Mallard_Duckling": ["Beak_Duckling"],
            "Beak_Duckling": ["Beak_Tail", "Beak_Drake"],
            "Beak_Drake": ["Mallard_Drake", "Beak_Dabbler"],
            "Beak_Dabbler": ["Beak_Pondside"],
            "Beak_Pondside": ["Feather_Pondside", "Beak_Migration", "Mallard_Pondside", "Beak_Dabbler"],
            "Beak_Migration": ["Feather_Migration", "Beak_Aquatic", "Mallard_Migration", "Beak_Pondside"],
            "Feather_Migration": ["Waterfoul_Migration", "Feather_Aquatic", "Beak_Migration", "Feather_Pondside"],
            "Feather_Pondside": ["Waterfoul_Pondside", "Feather_Migration", "Beak_Pondside"],
            "Feather_Circle": ["Feather_Pondside", "Circle_Dabbler"],
            "Circle_Dabbler": ["Circle_Tail", "Beak_Dabbler"],
            "Circle_Tail": ["Circle_Breadcrumb", "Beak_Tail"],
            "Circle_Breadcrumb": ["Waddle_Breadcrumb", "Waterfoul_Circle"],
            "Waterfoul_Circle": ["Feather_Circle"],
            "Waddle_Breadcrumb": ["Waddle_Pondside", "Circle_Breadcrumb", "Quack_Pondside"],
            "Waddle_Pondside": ["Waddle_Migration", "Waterfoul_Pondside", "Quack_Pondside"],
            "Waddle_Migration": ["Waddle_Aquatic", "Waterfoul_Migration", "Quack_Migration"],
            "Quack_Migration": ["Waddle_Migration", "Waddle_Aquatic", "Quack_Pondside"],
            "Quack_Pondside": ["Waddle_Pondside", "Quack_Migration", "Waddle_Breadcrumb"]
        }

        # Add the directed paths to the graph with calculated distances
        for from_intersection, to_intersections in directed_paths.items():
            for to_intersection in to_intersections:
                # Calculate the Euclidean distance between the two intersections (which are now Point objects)
                distance = self.calculate_distance(intersections[from_intersection], intersections[to_intersection])
                # Add the directed edge with distance to the graph
                graph[from_intersection][to_intersection] = distance

        return graph

    def dijkstra(self, graph, start, goal):
        # If the start and goal are the same, return the start node
        if start == goal:
            return {start: 0}, [start]

        # Min-heap priority queue for storing the nodes to visit
        queue = [(0, start)]  # (distance, node)
        distances = {node: float('inf') for node in graph}  # Initialize all nodes with infinity
        distances[start] = 0  # Starting node has a distance of 0
        shortest_path = {}  # Dictionary to track the shortest path

        while queue:
            current_distance, current_node = heapq.heappop(queue)

            # Skip if this node's distance has already been updated
            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in graph[current_node].items():
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(queue, (distance, neighbor))
                    shortest_path[neighbor] = current_node

            # Stop the search when we reach the goal node
            if current_node == goal:
                break

        # Reconstruct the path from start to goal
        path = []
        current_node = goal
        while current_node != start:
            path.insert(0, current_node)
            current_node = shortest_path.get(current_node, None)
            if current_node is None:
                print("No path found")
                return None, None

        path.insert(0, start)
        return distances, path



    # Method to print the graph for debugging purposes
    def print_graph(self, graph):
        for intersection, neighbors in graph.items():
            print(f"{intersection}: {neighbors}")
            
def calculate_angle(prev, curr, next):
    """Calculate the angle between three points: prev -> curr -> next"""
    # Vector from prev to curr
    vec1 = (curr.x - prev.x, curr.y - prev.y)
    # Vector from curr to next
    vec2 = (next.x - curr.x, next.y - curr.y)

    # Dot product and magnitude
    dot_product = vec1[0] * vec2[0] + vec1[1] * vec2[1]
    mag1 = math.sqrt(vec1[0] ** 2 + vec1[1] ** 2)
    mag2 = math.sqrt(vec2[0] ** 2 + vec2[1] ** 2)

    # Calculate the angle using the dot product formula
    angle = math.acos(dot_product / (mag1 * mag2)) * 180 / math.pi  # Convert to degrees

    return angle

def print_turns(path, intersections):
    """Print out left or right turns along the path"""
    for i in range(1, len(path) - 1):
        prev_intersection = intersections[path[i - 1]]
        curr_intersection = intersections[path[i]]
        next_intersection = intersections[path[i + 1]]
    
        angle = calculate_angle(prev_intersection, curr_intersection, next_intersection)
    
        if angle < 45:  # Going straight
            print(f"Going straight at {path[i]}")
        elif angle > 135:  # Right turn
            print(f"Turn right at {path[i]}")
        else:  # Left turn
            print(f"Turn left at {path[i]}")
                
# def get_vehicle_position(team_id):
#     server_ip = "10.216.29.48"  # Replace with the actual server IP
#     url = f"http://{server_ip}:5000/whereami/{team_id}"

#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             position = data.get("position", None)
#             if position:
#                 return position
#             else:
#                 print(f"Error: {data.get('message', 'No position data available')}")
#         else:
#             print(f"Error: {response.status_code} - {response.text}")
#     except requests.exceptions.RequestException as e:
#         print(f"Error connecting to server: {e}")

#     return None

# Coordinates for intersections (X, Y) divided by 100
intersections = {
    "Beak_Aquatic": Point(452 / 100, 29 / 100),
    "Feather_Aquatic": Point(305 / 100, 29 / 100),
    "Waddle_Aquatic": Point(129 / 100, 29 / 100),
    "Waterfoul_Aquatic": Point(213 / 100, 29 / 100),
    "Circle_Breadcrumb": Point(284 / 100, 393 / 100),
    "Waddle_Breadcrumb": Point(181 / 100, 459 / 100),
    "Feather_Circle": Point(305 / 100, 296 / 100),
    "Waterfoul_Circle": Point(273 / 100, 307 / 100),
    "Beak_Dabbler": Point(452 / 100, 293 / 100),
    "Circle_Dabbler": Point(350 / 100, 324 / 100),
    "Mallard_Dabbler": Point(585 / 100, 293 / 100),
    "Beak_Drake": Point(452 / 100, 402 / 100),
    "Mallard_Drake": Point(576 / 100, 354 / 100),
    "Beak_Duckling": Point(452 / 100, 474 / 100),
    "Mallard_Duckling": Point(593 / 100, 354 / 100),
    "Beak_Migration": Point(452 / 100, 135 / 100),
    "Feather_Migration": Point(305 / 100, 135 / 100),
    "Mallard_Migration": Point(585 / 100, 135 / 100),
    "Quack_Migration": Point(29 / 100, 135 / 100),
    "Waddle_Migration": Point(129 / 100, 135 / 100),
    "Waterfoul_Migration": Point(213 / 100, 135 / 100),
    "Beak_Pondside": Point(452 / 100, 233 / 100),
    "Feather_Pondside": Point(305 / 100, 233 / 100),
    "Mallard_Pondside": Point(585 / 100, 233 / 100),
    "Quack_Pondside": Point(28 / 100, 329 / 100),
    "Waterfoul_Pondside": Point(214 / 100, 241 / 100),
    "Waddle_Pondside": Point(157 / 100, 266 / 100),
    "Beak_Tail": Point(452 / 100, 465 / 100),
    "Circle_Tail": Point(335 / 100, 387 / 100)
}

def claim_fare(server, authKey):
    # Make request to fares endpoint to claim a fare
    res = request.urlopen(server + "/fares")
    if res.status == 200:
        fares = json.loads(res.read())
        for fare in fares:
            if not fare['claimed']:
                toClaim = fare['id']
                res = request.urlopen(server + "/fares/claim/" + str(toClaim) + "?auth=" + authKey)
                if res.status == 200:
                    data = json.loads(res.read())
                    if data['success']:
                        print("Claimed fare id", toClaim)
                        src = Point(fare['src']['x'], fare['src']['y'])
                        dest = Point(fare['dest']['x'], fare['dest']['y'])
                        fare_type = FareType(fare.get('fare_type', 0))  # Use a default value if 'fare_type' is not present
                        return Fare(src, dest, fare_type)  # Return an instance of Fare
                    else:
                        print("Failed to claim fare", toClaim, "reason:", data['message'])
    else:
        print("Got status", str(res.status), "requesting fares")
    return None

def find_shortest_path(path_finder, intersections, start, goal):
    graph = path_finder.create_graph(intersections)
    start_intersection = path_finder.find_closest_intersection(start, intersections)
    goal_intersection = path_finder.find_closest_intersection(goal, intersections)

    # print(f"Closest start intersection: {start_intersection}")
    # print(f"Closest goal intersection: {goal_intersection}")

    distances, path = path_finder.dijkstra(graph, start_intersection, goal_intersection)

    if distances:
        # print(f"\nShortest distance from {start_intersection} to {goal_intersection}: {distances[goal_intersection]:.2f}")
        # print(f"Shortest path from {start_intersection} to {goal_intersection}:")
        # print(" -> ".join(path))
        # print("\n")
        return path
    else:
        print("No path found")
        return []
        
        
def get_vehicle_position(server, team_id):
    url = f"{server}/whereami/{team_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            position = data.get("position", None)
            if position:
                return position
            else:
                print(f"Error: {data.get('message', 'No position data available')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")

    return None

# Function to check if the vehicle has reached the intersection
def has_reached_intersection(vehicle_position, intersection):
    # Calculate the distance between the vehicle's position and the intersection
    distance = math.sqrt((vehicle_position.x - intersection.x) ** 2 + (vehicle_position.y - intersection.y) ** 2)
    return distance < 0.1  # Return True if the distance is less than 0.1, else False

def find_two_closest_intersections(vehicle_position, intersections):
    # Calculate the distances from the vehicle's position to all intersections
    distances = []
    for intersection, coord in intersections.items():
        distance = math.sqrt((vehicle_position.x - coord.x) ** 2 + (vehicle_position.y - coord.y) ** 2)
        distances.append((distance, intersection, coord))

    # Sort the distances in ascending order
    distances.sort()

    # Get the two closest intersections
    closest_intersections = distances[:2]

    # Print the actual coordinates of the two closest intersections
    for dist, intersection, coord in closest_intersections:
        print(f"Intersection: {intersection}, Coordinates: ({coord.x}, {coord.y}), Distance: {dist:.2f}")

    return [intersection for _, intersection, _ in closest_intersections]
    
def navigate_to_position(server, team, path_finder, intersections, target_location, target_name, fare):
    previous_intersection = None

    while True:
        vehicle_position = get_vehicle_position(server, team)
        if vehicle_position:
            vehicle_position = Point(vehicle_position['x'], vehicle_position['y'])
            print(f"\nVehicle {team} current position: ({vehicle_position.x}, {vehicle_position.y})")

            # Find the path to the target location (pickup or dropoff)
            path_to_target = find_shortest_path(path_finder, intersections, vehicle_position, target_location)
            #print(f"Path to {target_name} location: {path_to_target}")

            # Get the next intersection on the path
            next_intersection = path_to_target[1] if len(path_to_target) > 1 else None
            
            print(f"Next intersection coordinates: ({intersections[next_intersection].x}, {intersections[next_intersection].y})", next_intersection)

            next_intersection_coord = intersections[next_intersection] if next_intersection else None

            # Print details of the previous intersection
            if previous_intersection:
                print(f"Previous intersection coordinates: ({intersections[previous_intersection].x}, {intersections[previous_intersection].y}): ", previous_intersection)
                previous_intersection_coord = Point(intersections[previous_intersection].x, intersections[previous_intersection].y)

            # Check if the vehicle has reached the previous intersection
            if previous_intersection and has_reached_intersection(vehicle_position, previous_intersection_coord):
                previous_intersection = next_intersection  # Move to the next intersection
                
                # Print the navigation instruction for the next intersection
                if next_intersection:
                    current_instruction = intersections[next_intersection]
                    next_instruction = intersections[path_to_target[path_to_target.index(next_intersection) + 1]] if path_to_target.index(next_intersection) + 1 < len(path_to_target) else None
                    instruction = generate_navigation_instruction(vehicle_position, current_instruction, next_instruction)
                    print(f"Has reached the previous intersection. Instruction: {instruction}: ", next_intersection, "\n")
            else:
                print(f"Vehicle {team} has not reached the previous intersection yet.")

            # Set the first intersection as the previous intersection if it's the initial iteration
            if previous_intersection is None and len(path_to_target) > 1:
                previous_intersection = path_to_target[1]

            # If the vehicle has reached the target location
            if next_intersection == None:
                print(f"Vehicle {team} has reached the {target_name} location.")
                break  # Exit the loop once the target is reached

        else:
            print("No position data available for vehicle.")
        
        # Update fare status
        teamStatus = Team(team)
        teamStatus.update_position(vehicle_position)
        fare.periodic(team, [teamStatus])
        if fare.inPosition:
            print("In Position Badge")
        if fare.pickedUp:
            print("Picked Up Badge")
        if fare.completed:
            print("Completed Badge")
        if fare.paid:
            print("Paid Badge")

        time.sleep(10)


def generate_navigation_instruction(vehicle_position, current_intersection, next_intersection):
    """Generate the navigation instruction based on the current and next intersections."""
    if next_intersection:
        # Calculate the angle of turn
        angle = calculate_angle(vehicle_position, current_intersection, next_intersection)

        if angle < 45:  # Going straight
            return f"Go straight at ({current_intersection.x}, {current_intersection.y})"
        elif angle > 135:  # Right turn
            return f"Turn right at ({current_intersection.x}, {current_intersection.y})"
        else:  # Left turn
            return f"Turn left at ({current_intersection.x}, {current_intersection.y})"
    return "Continue straight"


def main():
    fare = claim_fare(server, authKey)
    if not fare:
        return

    pickup_location = fare.src
    dropoff_location = fare.dest

    path_finder = PathFinder()

    navigate_to_position(server, team, path_finder, intersections, pickup_location, "pickup", fare)
    navigate_to_position(server, team, path_finder, intersections, dropoff_location, "dropoff", fare)

if __name__ == "__main__":
    main()