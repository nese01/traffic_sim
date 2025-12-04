"""
Car.py
Individual vehicle agent for traffic simulation
"""

class Car:
    """
    Represents an individual vehicle agent in the traffic simulation.
    Each car moves forward and interacts with traffic lights.
    """

    def __init__(self, unique_id, position, direction):
        """
        Initialize a new car agent.

        Args:
            unique_id: Unique identifier for this car
            position: Starting position as [x, y] coordinates
            direction: Movement direction as [dx, dy] (e.g., [1, 0] for east)
        """
        self.id = unique_id
        self.position = list(position)  # Ensure it's a mutable list
        self.direction = list(direction)
        self.speed = 1
        self.idle_time = 0
        self.has_moved = False
        self.completed = False

    def step(self, traffic_lights, other_cars):
        """
        Called every timestep to update the car's state.

        Args:
            traffic_lights: List of TrafficLight objects
            other_cars: List of other Car objects to check for collisions
        """
        self.has_moved = False

        # Check for car ahead
        next_position = [self.position[0] + self.direction[0],
                         self.position[1] + self.direction[1]]

        if self.is_position_occupied(next_position, other_cars):
            self.idle_time += 1
            return

        # Check traffic lights
        for light in traffic_lights:
            if self.at_traffic_light(light):
                if light.state in ["RED", "YELLOW"]:
                    self.idle_time += 1
                    return

        # Move forward if no obstacles
        self.move_forward()

    def move_forward(self):
        """Advances the car's position by one step in its direction."""
        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed
        self.has_moved = True

    def at_traffic_light(self, traffic_light):
        """Checks if this car is currently at the traffic light position."""
        return (self.position[0] == traffic_light.position[0] and
                self.position[1] == traffic_light.position[1])

    def is_position_occupied(self, position, other_cars):
        """Checks if a given position is occupied by another car."""
        for car in other_cars:
            if car.id == self.id:
                continue
            if car.position[0] == position[0] and car.position[1] == position[1]:
                return True
        return False

    def is_off_grid(self, grid_width, grid_height):
        """Checks if this car has moved off the grid."""
        if (self.position[0] < 0 or self.position[0] >= grid_width or
                self.position[1] < 0 or self.position[1] >= grid_height):
            self.completed = True
            return True
        return False

    def get_stats(self):
        """Returns performance statistics for this car."""
        return {
            'id': self.id,
            'idle_time': self.idle_time,
            'position': self.position.copy(),
            'has_moved': self.has_moved,
            'completed': self.completed
        }