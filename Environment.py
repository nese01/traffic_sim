import numpy as np
import random
from Cars import Cars
from TrafficLight import TrafficLightSet

class Environment:
    """
    Main simulation environment that coordinates cars and traffic lights.
    Simplified version with no lanes - just cars moving toward a traffic light.
    """

    def __init__(self, traffic_mode="time_cycle", grid_width=20, grid_height=20, spawn_rate=0.3,
                 max_cars=None, num_lanes=1, simulation_duration=None):
        """
        Initialize the simulation environment.

        Args:
            traffic_light: TrafficLight object controlling the intersection
            grid_width: Width of the simulation grid
            grid_height: Height of the simulation grid
            spawn_rate: Probability of spawning a new car per timestep (0.0 - 1.0)
            max_cars: Maximum total cars to spawn (None = unlimited)
            num_lanes: Number of parallel lanes (1-3 recommended)
            simulation_duration: Max timesteps to run (None = unlimited)
        """
        # List to store all the traffic lights
        self.light_type = traffic_mode
        self.west_east_traffic_lights = []
        self.north_south_traffic_lights = []

        # Grid dimensions for the simulation space
        self.grid_width = grid_width
        self.grid_height = grid_height

        # List to store all active cars in the simulation
        self.cars = []

        # Current simulation time (measured in discrete timesteps)
        self.time = 0

        # Probability that a new car spawns each timestep
        # 0.3 = 30% chance per timestep (adjust for traffic density)
        # 0.1 = light traffic, 0.5 = moderate, 0.8 = heavy traffic
        self.spawn_rate = spawn_rate

        # Maximum number of cars to spawn in total (None = no limit)
        # Useful for comparing scenarios with exact same car count
        self.max_cars = max_cars

        # Number of parallel lanes cars can travel in
        # More lanes = more throughput capacity
        self.num_lanes = num_lanes

        #uses the number of lanes to store the light set
        self.light_set = self.initialize_light_set()

        # Maximum simulation duration in timesteps (None = run indefinitely)
        # Useful for consistent comparison periods (e.g., 300 = 5 minutes)
        self.simulation_duration = simulation_duration

        # Counter for assigning unique IDs to cars
        self.car_id_counter = 0

        # Statistics tracking for analysis
        self.total_cars_spawned = 0
        self.total_cars_completed = 0

        # Flag to track if simulation should continue
        self.is_running = True

        """
        Initialize lights
        Run at least once if adding multiple lanes. Focus on later
        """
    def initialize_light_set(self):
        ymiddle = int(self.grid_height/2)
        xmiddle = int(self.grid_width/2)
        positions = np.zeros((self.num_lanes*4,2), dtype='i')
        for i in range(self.num_lanes):
            #southern traffic light positions
            positions[i] = xmiddle+1+i
            positions[i,1] = ymiddle-self.num_lanes

            #northern traffic light positions
            positions[i+1] = xmiddle-i
            positions[i+1, 1] = ymiddle+self.num_lanes+1

            #western traffic light positions
            positions[i+2, 0] = self.num_lanes, ymiddle-i
            positions[i+2, 1] = ymiddle-i

            #eastern traffic light positions
            positions[i+3, 0] = self.num_lanes + 1
            positions[i+3, 1] = ymiddle + i + 1

        return TrafficLightSet(positions, lanes=self.num_lanes)


    def step(self):
        """
        Advances the simulation by one timestep.
        Order of operations:
        1. Update traffic light state
        2. Spawn new cars
        3. Move all existing cars
        4. Remove cars that finished
        5. Increment time
        """
        # STEP 1: Update traffic light first
        # Light changes independently based on timing cycle
        self.traffic_light.step()

        # STEP 2: Attempt to spawn a new car
        # Random chance based on spawn_rate
        if random.random() < self.spawn_rate:
            self.spawn_car()

        # STEP 3: Update all cars
        # Each car decides whether to move or wait
        for car in self.cars:
            # Pass traffic light and other cars for decision-making
            car.step(self.traffic_light, self.cars)

        # STEP 4: Remove completed cars (off-grid)
        self.remove_completed_cars()

        # STEP 5: Increment simulation clock
        self.time += 1

    def spawn_car(self):
        """
        Creates a new car at a spawn position.
        Cars spawn at the edge of the grid moving toward the traffic light.
        """
        # Spawn position at the left edge of the grid
        # All cars start at x=0 and move right toward the traffic light
        spawn_x = 0
        spawn_y = self.grid_height // 2  # Middle of the grid vertically

        # Direction vector: [1, 0] means moving east (right)
        direction = [1, 0]

        # Check if spawn position is clear (no car already there)
        spawn_position = [spawn_x, spawn_y]
        if not self.is_position_occupied(spawn_position):
            # Create new car with unique ID
            new_car = Cars(self.car_id_counter, spawn_position, direction)

            # Add car to the simulation
            self.cars.append(new_car)

            # Increment counters
            self.car_id_counter += 1
            self.total_cars_spawned += 1

    def is_position_occupied(self, position):
        """
        Checks if any car occupies a given position.

        Args:
            position: [x, y] coordinates to check

        Returns:
            Boolean: True if occupied, False if clear
        """
        # Check each car's position
        for car in self.cars:
            if car.position[0] == position[0] and car.position[1] == position[1]:
                return True
        return False

    def remove_completed_cars(self):
        """
        Removes cars that have moved off the grid.
        These cars have completed their journey through the intersection.
        """
        # Create list of cars to keep (still on grid)
        cars_to_keep = []

        # Check each car
        for car in self.cars:
            # If car is off grid, it's completed
            if car.is_off_grid(self.grid_width, self.grid_height):
                self.total_cars_completed += 1
            else:
                # Keep this car in the simulation
                cars_to_keep.append(car)

        # Update car list to only include active cars
        self.cars = cars_to_keep

    def get_average_idle_time(self):
        """
        Calculates average idle time across all cars.
        This is the primary performance metric.

        Returns:
            Float: Average idle time per car, or 0 if no cars
        """
        # Handle case with no cars (avoid division by zero)
        if len(self.cars) == 0:
            return 0.0

        # Sum idle time from all cars
        total_idle = sum(car.idle_time for car in self.cars)

        # Calculate and return average
        return total_idle / len(self.cars)

    def get_total_idle_time(self):
        """
        Gets the total idle time summed across all cars.

        Returns:
            Integer: Total idle time across all cars
        """
        return sum(car.idle_time for car in self.cars)

    def get_statistics(self):
        """
        Gathers comprehensive statistics about simulation state.

        Returns:
            Dictionary with performance metrics
        """
        return {
            'time': self.time,
            'total_cars_active': len(self.cars),
            'total_cars_spawned': self.total_cars_spawned,
            'total_cars_completed': self.total_cars_completed,
            'average_idle_time': self.get_average_idle_time(),
            'total_idle_time': self.get_total_idle_time(),
            'traffic_light_state': self.traffic_light.state,
            'cars_moving': sum(1 for car in self.cars if car.has_moved),
            'cars_stopped': sum(1 for car in self.cars if not car.has_moved)
        }

    def reset(self):
        """
        Resets simulation to initial state.
        Useful for running multiple experiments.
        """
        # Clear all cars
        self.cars = []

        # Reset traffic light
        self.traffic_light.reset()

        # Reset counters
        self.time = 0
        self.car_id_counter = 0
        self.total_cars_spawned = 0
        self.total_cars_completed = 0

    def get_grid_state(self):
        """
        Returns 2D numpy array representation of the environment.
        Used for visualization with matplotlib.

        Returns:
            2D numpy array where:
            0 = empty space
            1 = car present
            2 = red light
            3 = yellow light
            4 = green light
        """
        # Create empty grid
        grid = np.zeros((self.grid_height, self.grid_width))

        # Place all cars on the grid
        for car in self.cars:
            x = int(car.position[0])
            y = int(car.position[1])

            # Check bounds before placing
            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                grid[y, x] = 1  # 1 represents a car

        # Place traffic light on grid with color encoding
        light_x = int(self.traffic_light.position[0])
        light_y = int(self.traffic_light.position[1])

        # Check bounds for traffic light
        if 0 <= light_x < self.grid_width and 0 <= light_y < self.grid_height:
            # Different values for different light states
            if self.traffic_light.state == "RED":
                grid[light_y, light_x] = 2
            elif self.traffic_light.state == "YELLOW":
                grid[light_y, light_x] = 3
            elif self.traffic_light.state == "GREEN":
                grid[light_y, light_x] = 4

        return grid

    def print_state(self):
        """
        Prints current simulation state to console.
        Useful for debugging and quick checks.
        """
        print(f"Time: {self.time}")
        print(f"Traffic Light: {self.traffic_light.state}")
        print(f"Active Cars: {len(self.cars)}")
        print(f"Average Idle Time: {self.get_average_idle_time():.2f}")
        print(f"Cars Spawned: {self.total_cars_spawned}")
        print(f"Cars Completed: {self.total_cars_completed}")
        print("-" * 40)