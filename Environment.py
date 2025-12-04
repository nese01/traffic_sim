"""
Environment.py
Main simulation environment for 4-way intersection traffic control
"""

import numpy as np
import random
from Car import Car
from TrafficLight import TrafficLightSet


class Environment:
    """Main simulation environment for 4-way intersection."""

    def __init__(self, traffic_mode="time_cycle", grid_width=20, grid_height=20,
                 ns_spawn_rate=0.3, ew_spawn_rate=0.3, max_cars=None,
                 num_lanes=1, simulation_duration=None,
                 y_green_time=30, x_green_time=30):
        """
        Initialize the simulation environment.

        Args:
            traffic_mode: "time_cycle" or "detection_cycle"
            grid_width: Width of the simulation grid
            grid_height: Height of the simulation grid
            ns_spawn_rate: Spawn rate for north-south traffic
            ew_spawn_rate: Spawn rate for east-west traffic
            max_cars: Maximum total cars to spawn (None = unlimited)
            num_lanes: Number of lanes in each direction
            simulation_duration: Max timesteps to run (None = unlimited)
            y_green_time: Green light duration for NS direction
            x_green_time: Green light duration for EW direction
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cars = []
        self.time = 0

        # Spawn rates for different directions
        self.ns_spawn_rate = ns_spawn_rate
        self.ew_spawn_rate = ew_spawn_rate

        self.max_cars = max_cars
        self.num_lanes = num_lanes
        self.simulation_duration = simulation_duration

        # Initialize traffic light system
        self.light_set = TrafficLightSet(
            grid_width, grid_height, num_lanes,
            y_green_time=y_green_time,
            x_green_time=x_green_time,
            detection=traffic_mode
        )

        # Counters
        self.car_id_counter = 0
        self.total_cars_spawned = 0
        self.total_cars_completed = 0
        self.cumulative_idle_time_completed = 0  # NEW: Track idle time of completed cars
        self.is_running = True

    def step(self):
        """Advances the simulation by one timestep."""
        # Update traffic lights
        self.light_set.step(self.cars)

        # Spawn new cars from all directions
        if self.max_cars is None or self.total_cars_spawned < self.max_cars:
            self.spawn_cars()

        # Update all cars
        all_lights = self.light_set.get_all_lights()
        for car in self.cars:
            car.step(all_lights, self.cars)

        # Remove completed cars
        self.remove_completed_cars()

        # Increment time
        self.time += 1

        # Check if simulation should end
        if self.simulation_duration and self.time >= self.simulation_duration:
            self.is_running = False

    def spawn_cars(self):
        """Spawn cars from all four directions based on spawn rates."""
        y_mid = self.grid_height // 2
        x_mid = self.grid_width // 2

        # Spawn from south (moving north)
        if random.random() < self.ns_spawn_rate:
            for lane in range(self.num_lanes):
                spawn_pos = [x_mid + lane, 0]
                direction = [0, 1]  # Moving north
                if not self.is_position_occupied(spawn_pos):
                    self._create_car(spawn_pos, direction)

        # Spawn from north (moving south)
        if random.random() < self.ns_spawn_rate:
            for lane in range(self.num_lanes):
                spawn_pos = [x_mid - lane - 1, self.grid_height - 1]
                direction = [0, -1]  # Moving south
                if not self.is_position_occupied(spawn_pos):
                    self._create_car(spawn_pos, direction)

        # Spawn from west (moving east)
        if random.random() < self.ew_spawn_rate:
            for lane in range(self.num_lanes):
                spawn_pos = [0, y_mid - lane - 1]
                direction = [1, 0]  # Moving east
                if not self.is_position_occupied(spawn_pos):
                    self._create_car(spawn_pos, direction)

        # Spawn from east (moving west)
        if random.random() < self.ew_spawn_rate:
            for lane in range(self.num_lanes):
                spawn_pos = [self.grid_width - 1, y_mid + lane]
                direction = [-1, 0]  # Moving west
                if not self.is_position_occupied(spawn_pos):
                    self._create_car(spawn_pos, direction)

    def _create_car(self, position, direction):
        """Helper to create a new car."""
        new_car = Car(self.car_id_counter, position, direction)
        self.cars.append(new_car)
        self.car_id_counter += 1
        self.total_cars_spawned += 1

    def is_position_occupied(self, position):
        """Checks if any car occupies a given position."""
        for car in self.cars:
            if car.position[0] == position[0] and car.position[1] == position[1]:
                return True
        return False

    def remove_completed_cars(self):
        """Removes cars that have moved off the grid."""
        cars_to_keep = []
        for car in self.cars:
            if car.is_off_grid(self.grid_width, self.grid_height):
                self.total_cars_completed += 1
                self.cumulative_idle_time_completed += car.idle_time  # FIXED: Save idle time before removing
            else:
                cars_to_keep.append(car)
        self.cars = cars_to_keep

    def get_average_idle_time(self):
        """Calculates average idle time across all completed cars."""
        if self.total_cars_completed == 0:
            return 0.0
        
        # FIXED: Calculate average from cumulative idle time of completed cars
        return self.cumulative_idle_time_completed / self.total_cars_completed

    def get_total_idle_time(self):
        """Gets the total idle time summed across all cars (active + completed)."""
        # Total = completed cars + currently active cars
        active_idle = sum(car.idle_time for car in self.cars)
        return self.cumulative_idle_time_completed + active_idle

    def get_statistics(self):
        """Gathers comprehensive statistics about simulation state."""
        all_lights = self.light_set.get_all_lights()
        ns_state = self.light_set.north_south_lights[0].state if self.light_set.north_south_lights else "N/A"
        ew_state = self.light_set.east_west_lights[0].state if self.light_set.east_west_lights else "N/A"

        return {
            'time': self.time,
            'total_cars_active': len(self.cars),
            'total_cars_spawned': self.total_cars_spawned,
            'total_cars_completed': self.total_cars_completed,
            'average_idle_time': self.get_average_idle_time(),
            'total_idle_time': self.get_total_idle_time(),
            'ns_light_state': ns_state,
            'ew_light_state': ew_state,
            'cars_moving': sum(1 for car in self.cars if car.has_moved),
            'cars_stopped': sum(1 for car in self.cars if not car.has_moved)
        }

    def reset(self):
        """Resets simulation to initial state."""
        self.cars = []
        self.light_set.reset()
        self.time = 0
        self.car_id_counter = 0
        self.total_cars_spawned = 0
        self.total_cars_completed = 0
        self.cumulative_idle_time_completed = 0  # FIXED: Reset cumulative idle time
        self.is_running = True

    def get_grid_state(self):
        """
        Returns 2D numpy array representation of the environment.
        0 = empty, 1 = car, 2 = red light, 3 = yellow light, 4 = green light
        """
        grid = np.zeros((self.grid_height, self.grid_width))

        # Place cars
        for car in self.cars:
            x = int(car.position[0])
            y = int(car.position[1])
            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                grid[y, x] = 1

        # Place traffic lights
        for light in self.light_set.get_all_lights():
            x = int(light.position[0])
            y = int(light.position[1])
            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                if light.state == "RED":
                    grid[y, x] = 2
                elif light.state == "YELLOW":
                    grid[y, x] = 3
                elif light.state == "GREEN":
                    grid[y, x] = 4

        return grid

    def print_state(self):
        """Prints current simulation state to console."""
        stats = self.get_statistics()
        print(f"Time: {self.time}")
        print(f"NS Lights: {stats['ns_light_state']}, EW Lights: {stats['ew_light_state']}")
        print(f"Active Cars: {len(self.cars)}")
        print(f"Average Idle Time: {self.get_average_idle_time():.2f}")
        print(f"Cars Spawned: {self.total_cars_spawned}")
        print(f"Cars Completed: {self.total_cars_completed}")
        print(f"Moving: {stats['cars_moving']}, Stopped: {stats['cars_stopped']}")
        print("-" * 40)