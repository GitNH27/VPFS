import json
import math
import heapq
from urllib import request

    # Function to calculate Euclidean distance between two coordinates
    def calculate_distance(self, coord1, coord2):
        return math.sqrt((coord2[0] - coord1[0]) ** 2 + (coord2[1] - coord1[1]) ** 2)

    # Function to find the closest intersection to a fare location
    def find_closest_intersection(self, fare_location, intersections):
        closest_intersection = None
        closest_distance = float('inf')

        for intersection, coord in intersections.items():
            distance = self.calculate_distance(fare_location, coord)
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
            "Mallard_Dabbler": ["Mallard_Pondside", "Beak_Duckling"],
            "Mallard_Drake": ["Mallard_Dabbler"],
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

# Coordinates for intersections (X, Y)
intersections = {
    "Beak_Aquatic": (452, 29),
    "Feather_Aquatic": (305, 29),
    "Waddle_Aquatic": (129, 29),
    "Waterfoul_Aquatic": (213, 29),
    "Circle_Breadcrumb": (284, 393),
    "Waddle_Breadcrumb": (181, 459),
    "Feather_Circle": (305, 296),
    "Waterfoul_Circle": (273, 307),
    "Beak_Dabbler": (452, 293),
    "Circle_Dabbler": (350, 324),
    "Mallard_Dabbler": (585, 293),
    "Beak_Drake": (452, 402),
    "Mallard_Drake": (576, 354),
    "Beak_Duckling": (452, 474),
    "Mallard_Duckling": (593, 354),
    "Beak_Migration": (452, 135),
    "Feather_Migration": (305, 135),
    "Mallard_Migration": (585, 135),
    "Quack_Migration": (29, 135),
    "Waddle_Migration": (129, 135),
    "Waterfoul_Migration": (213, 135),
    "Beak_Pondside": (452, 233),
    "Feather_Pondside": (305, 233),
    "Mallard_Pondside": (585, 233),
    "Quack_Pondside": (28, 329),
    "Waterfoul_Pondside": (214, 241),
    "Waddle_Pondside": (157, 266),
    "Beak_Tail": (452, 465),
    "Circle_Tail": (335, 387)
}

# Server details will change between lab, home, and competition, so saving them somehwere easy to edit
server_ip = "localhost"
server = f"http://{server_ip}:5000"
authKey = "32" # For the lab, your auth key is your team number, at competition this will be a secret key
team = 32

# Make request to fares endpoint
res = request.urlopen(server + "/fares")
# Verify that we got HTTP OK
if res.status == 200:
  # Decode JSON data
  fares = json.loads(res.read())
  # Loop over the available fares
  for fare in fares:
    # If the fare is claimed, skip it
    if not fare['claimed']:
      # Get the ID of the fare
      toClaim = fare['id']
      
      # Make request to claim endpoint
      res = request.urlopen(server + "/fares/claim/" + str(toClaim) + "?auth=" + authKey)
      # Verify that we got HTTP OK
      if res.status == 200:
        # Decond JSON data
        data = json.loads(res.read())
        if data['success']:
          # If we have a fare, exit the loop
          print("Claimed fare id", toClaim)
          break
        else:
          # If the claim failed, report it and let the loop continue to the next
          print("Failed to claim fare", toClaim, "reason:", data['message'])
      else:
        # Report HTTP request error
        print("Got status", str(res.status), "claiming fare")
else:
  # Report HTTP request error
  print("Got status", str(res.status), "requesting fares")
  

  
# Check the status of our fare
res = request.urlopen(server + "/fares/current/" + str(team))
# Verify that we got HTTP OK
if res.status == 200:
  # Decode JSON data
  data = json.loads(res.read())
  # Report fare status
  if fare is not None:
    print("Have fare", data['fare'])
  else:
    print("No fare claimed", data['message'])
else:
  # Report HTTP request error
  print("Got status", str(res.status), "checking fare")
  
# After claiming the fare, perform pathfinding (if fare is claimed)
if fare:
    pickup_location = (fare['src']['x'], fare['src']['y'])
    dropoff_location = (fare['dest']['x'], fare['dest']['y'])

    # Create an instance of PathFinder and run the graph creation
    path_finder = PathFinder()

    # Create the graph
    graph = path_finder.create_graph(intersections)

    # Find the closest intersection for pickup and dropoff
    start_intersection = path_finder.find_closest_intersection(pickup_location, intersections)
    goal_intersection = path_finder.find_closest_intersection(dropoff_location, intersections)

    print(f"Closest pickup intersection: {start_intersection}")
    print(f"Closest dropoff intersection: {goal_intersection}")

    # Run Dijkstra's algorithm to find the shortest path
    distances, path = path_finder.dijkstra(graph, start_intersection, goal_intersection)

    # Print the results
    if distances:
        print(f"\nShortest distance from {start_intersection} to {goal_intersection}: {distances[goal_intersection]:.2f}")
        print(f"Shortest path from {start_intersection} to {goal_intersection}:")
        print(" -> ".join(path))
else:
    print("No fare was claimed.")