import json
import math
import heapq
import time
import requests
from Utils import Point
from urllib import request

# Server details
server_ip = "10.216.29.48"
server = f"http://{server_ip}:5000"
authKey = "32"
team = 32

class PathFinder:
    # Function to calculate Euclidean distance between two coordinates
    def calculate_distance(self, coord1, coord2):
        return math.sqrt((coord2[0] - coord1[0]) ** 2 + (coord2[1] - coord1[1]) ** 2)

    # Function to find the closest intersection to a fare location
    def find_closest_intersection(self, fare_location, intersections):
        closest_intersection = None
        closest_distance = float('inf')

        for intersection, coord in intersections.items():
            # Ensure fare_location is a Point object
            if isinstance(fare_location, dict):  # If it's still a dictionary
                fare_location = Point(fare_location['x'], fare_location['y'])  # Convert it to a Point object

            # Calculate distance using fare_location (which is now a Point object)
            distance = self.calculate_distance((fare_location.x, fare_location.y), coord)
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
                # Calculate the Euclidean distance between the two intersections
                distance = self.calculate_distance(intersections[from_intersection], intersections[to_intersection])
                # Add the directed edge with distance to the graph
                graph[from_intersection][to_intersection] = distance

        return graph

    # Function to implement Dijkstra's algorithm
    def dijkstra(self, graph, start, goal):
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
        vec1 = (curr[0] - prev[0], curr[1] - prev[1])
        # Vector from curr to next
        vec2 = (next[0] - curr[0], next[1] - curr[1])

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
    "Beak_Aquatic": (452 / 100, 29 / 100),
    "Feather_Aquatic": (305 / 100, 29 / 100),
    "Waddle_Aquatic": (129 / 100, 29 / 100),
    "Waterfoul_Aquatic": (213 / 100, 29 / 100),
    "Circle_Breadcrumb": (284 / 100, 393 / 100),
    "Waddle_Breadcrumb": (181 / 100, 459 / 100),
    "Feather_Circle": (305 / 100, 296 / 100),
    "Waterfoul_Circle": (273 / 100, 307 / 100),
    "Beak_Dabbler": (452 / 100, 293 / 100),
    "Circle_Dabbler": (350 / 100, 324 / 100),
    "Mallard_Dabbler": (585 / 100, 293 / 100),
    "Beak_Drake": (452 / 100, 402 / 100),
    "Mallard_Drake": (576 / 100, 354 / 100),
    "Beak_Duckling": (452 / 100, 474 / 100),
    "Mallard_Duckling": (593 / 100, 354 / 100),
    "Beak_Migration": (452 / 100, 135 / 100),
    "Feather_Migration": (305 / 100, 135 / 100),
    "Mallard_Migration": (585 / 100, 135 / 100),
    "Quack_Migration": (29 / 100, 135 / 100),
    "Waddle_Migration": (129 / 100, 135 / 100),
    "Waterfoul_Migration": (213 / 100, 135 / 100),
    "Beak_Pondside": (452 / 100, 233 / 100),
    "Feather_Pondside": (305 / 100, 233 / 100),
    "Mallard_Pondside": (585 / 100, 233 / 100),
    "Quack_Pondside": (28 / 100, 329 / 100),
    "Waterfoul_Pondside": (214 / 100, 241 / 100),
    "Waddle_Pondside": (157 / 100, 266 / 100),
    "Beak_Tail": (452 / 100, 465 / 100),
    "Circle_Tail": (335 / 100, 387 / 100)
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
                        return fare
                    else:
                        print("Failed to claim fare", toClaim, "reason:", data['message'])
    else:
        print("Got status", str(res.status), "requesting fares")
    return None

def find_shortest_path(path_finder, intersections, start, goal):
    graph = path_finder.create_graph(intersections)
    start_intersection = path_finder.find_closest_intersection(start, intersections)
    goal_intersection = path_finder.find_closest_intersection(goal, intersections)

    print(f"Closest start intersection: {start_intersection}")
    print(f"Closest goal intersection: {goal_intersection}")

    distances, path = path_finder.dijkstra(graph, start_intersection, goal_intersection)

    if distances:
        print(f"\nShortest distance from {start_intersection} to {goal_intersection}: {distances[goal_intersection]:.2f}")
        print(f"Shortest path from {start_intersection} to {goal_intersection}:")
        print(" -> ".join(path))
    else:
        print("No path found")
        
        
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
    
    
def main():    
    # Claim a fare
    fare = claim_fare(server, authKey)
    if not fare:
        return
    
    while(True):
        # Fetch the vehicle's current position from the WhereAmI endpoint
        vehicle_position = get_vehicle_position(server, team)
        if vehicle_position:
            print(f"Vehicle {team} position: {vehicle_position}")

            vehicle_position = Point(vehicle_position['x'], vehicle_position['y'])

            # # The actual pickup location should come from the fare object
            # pickup_location = Point(fare['src']['x'], fare['src']['y'])  # The fare's pickup location
            # dropoff_location = Point(fare['dest']['x'], fare['dest']['y'])  # The fare's drop-off location

            # # Create an instance of PathFinder
            # path_finder = PathFinder()

            # # Find the shortest path from the vehicle's position to the pickup location
            # find_shortest_path(path_finder, intersections, vehicle_position, pickup_location)

            # # Find the shortest path from the pickup location to the dropoff location
            # find_shortest_path(path_finder, intersections, pickup_location, dropoff_location)
            time.sleep(2)
        else:
            print("No position data available for vehicle.")

if __name__ == "__main__":
    main()