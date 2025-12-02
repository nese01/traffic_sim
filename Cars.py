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
        # Unique identifier for tracking this specific car
        self.id = unique_id

        # Current position [x, y] on the grid
        self.position = position

        # Direction of travel as [dx, dy] vector
        # [1, 0] = moving east, [0, 1] = moving south, etc.
        self.direction = direction

        # Movement speed (cells per timestep) - constant for all cars
        self.speed = 1

        # Cumulative time spent idle (stopped at red/yellow lights)
        # This is our key performance metric for traffic efficiency
        self.idle_time = 0

        # Flag to track if car successfully moved this timestep
        self.has_moved = False

        # Flag to track if this car has completed its journey
        self.completed = False

    de step(self, TrafficLight, other_cars):
        """
        Called every timestep to update the car's state.
        Decides whether to move forward or wait based on conditions.

        Args:
            TrafficLight: TrafficLight object controlling this intersection
            other_cars: List of other Car objects to check for collisions
        """
        # Reset the movement flag at the start of each timestep
        self.has_moved = False

        # CONDITION 1: Check if another car is directly ahead (collision avoidance)
        # Look for cars in the next position we want to move to
        next_position = [self.position[0] + self.direction[0],
                         self.position[1] + self.direction[1]]

        # Check if any other car occupies the next position
        if self.is_position_occupied(next_position, other_cars):
            # Must wait behind the car ahead
            self.idle_time += 1
            return

        # CONDITION 2: Check if we're at the traffic light intersection
        # If we're at the light position, check the light's state
        if self.at_traffic_light(TrafficLight):
            # RED light: must stop and wait
            if TrafficLight.state == "RED":
                self.idle_time += 1
                return

            # YELLOW light: must stop (conservative approach)
            elif TrafficLight.state == "YELLOW":
                self.idle_time += 1
                return

            # GREEN light: proceed (falls through to move_forward)

        # If no conditions block movement, move forward
        self.move_forward()

    def move_forward(self):
        """
        Advances the car's position by one step in its direction.
        """
        # Calculate new position by adding direction vector to current position
        self.position[0] += self.direction[0] * self.speed
        self.position[1] += self.direction[1] * self.speed

        # Mark that this car successfully moved this timestep
        self.has_moved = True

    def at_traffic_light(self, TrafficLight):
        """
        Checks if this car is currently at the traffic light position.

        Args:
            TrafficLight: TrafficLight object to check against

        Returns:
            Boolean: True if car is at light position, False otherwise
        """
        # Compare car position with traffic light position
        return (self.position[0] == TrafficLight.position[0] and
                self.position[1] == TrafficLight.position[1])

    def is_position_occupied(self, position, other_cars):
        """
        Checks if a given position is occupied by another car.

        Args:
            position: [x, y] position to check
            other_cars: List of other Car objects

        Returns:
            Boolean: True if position is occupied, False otherwise
        """
        # Loop through all other cars
        for car in other_cars:
            # Skip checking against ourselves
            if car.id == self.id:
                continue

            # Check if this car occupies the position
            if car.position[0] == position[0] and car.position[1] == position[1]:
                return True

        # Position is clear
        return False

    def is_off_grid(self, grid_width, grid_height):
        """
        Checks if this car has moved off the grid (completed journey).

        Args:
            grid_width: Maximum x coordinate
            grid_height: Maximum y coordinate

        Returns:
            Boolean: True if car is off grid, False otherwise
        """
        # Check if position is outside grid boundaries
        if (self.position[0] < 0 or self.position[0] >= grid_width or
                self.position[1] < 0 or self.position[1] >= grid_height):
            self.completed = True
            return True
        return False

    def get_stats(self):
        """
        Returns performance statistics for this car.

        Returns:
            Dictionary containing car's metrics
        """
        return {
            'id': self.id,
            'idle_time': self.idle_time,
            'position': self.position.copy(),
            'has_moved': self.has_moved,
            'completed': self.completed
        }