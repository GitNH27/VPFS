import math
import heapq
import requests

class PathFinder:
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

    # Fetch the fare locations from your Flask app
    def get_fare_locations():
        url = 'http://127.0.0.1:5000/fares'  # URL to your Flask API
        response = requests.get(url)

        if response.status_code == 200:
            fares_data = response.json()
            fare_locations = []
            for fare in fares_data:
                fare_locations.append({
                    "number": fare["number"],
                    "location": (fare["position"]["x"], fare["position"]["y"])
                })
            return fare_locations
        else:
            print("Error: Could not retrieve fare data")
            return []
        
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

# Create an instance of PathFinder and run the graph creation
path_finder = PathFinder()

# Create the graph
graph = path_finder.create_graph(intersections)

# Example usage
start_node = "Beak_Aquatic"  # Replace with your desired start intersection
goal_node = "Feather_Pondside"  # Replace with your desired goal intersection

# Run Dijkstra's algorithm
distances, path = path_finder.dijkstra(graph, start_node, goal_node)

# Debugging: Print the graph and distances to see what's happening
print("\nGraph (Intersections and Connections):")
path_finder.print_graph(graph)

# Print the results
if distances:
    print(f"\nShortest distance from {start_node} to {goal_node}: {distances[goal_node]:.2f}")
    print(f"Shortest path from {start_node} to {goal_node}:")
    print(" -> ".join(path))
