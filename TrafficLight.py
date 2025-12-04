"""
TrafficLight.py
Traffic light control system for 4-way intersection
"""

import numpy as np

class TrafficLight:
    """Individual traffic light with position and state."""

    def __init__(self, position, state="RED", direction="NS"):
        """
        Args:
            position: [x, y] coordinates
            state: "RED", "YELLOW", or "GREEN"
            direction: "NS" (north-south) or "EW" (east-west)
        """
        self.position = list(position)
        self.state = state
        self.direction = direction  # Which flow this light controls

    def set_state(self, new_state):
        """Update the light state."""
        self.state = new_state

    def get_pos(self):
        """Returns position as tuple."""
        return tuple(self.position)


class TrafficLightSet:
    """Manages a set of traffic lights for a 4-way intersection."""

    def __init__(self, grid_width, grid_height, num_lanes=1,
                 y_green_time=30, x_green_time=30, yellow_time=3,
                 detection="time_cycle"):
        """
        Initialize traffic light set for intersection.

        Args:
            grid_width: Width of simulation grid
            grid_height: Height of simulation grid
            num_lanes: Number of lanes in each direction
            y_green_time: Green light duration for N-S traffic
            x_green_time: Green light duration for E-W traffic
            yellow_time: Yellow light duration
            detection: "time_cycle" or "detection_cycle"
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.num_lanes = num_lanes
        self.detection = detection

        # Timing parameters
        self.y_green_time = y_green_time
        self.x_green_time = x_green_time
        self.yellow_time = yellow_time

        # Current cycle state
        self.y_turn = True  # True = NS green, False = EW green
        self.current_timer = y_green_time
        self.current_state = "GREEN"  # GREEN, YELLOW, RED

        # Initialize lights
        self.north_south_lights = []
        self.east_west_lights = []
        self._initialize_lights()

    def _initialize_lights(self):
        """Create traffic lights at intersection positions."""
        y_mid = self.grid_height // 2
        x_mid = self.grid_width // 2

        # Create lights for each lane
        for lane in range(self.num_lanes):
            # North-South lights (start GREEN)
            # South approach (cars moving north)
            south_pos = [x_mid + lane, y_mid - self.num_lanes - 1]
            self.north_south_lights.append(TrafficLight(south_pos, "GREEN", "NS"))

            # North approach (cars moving south)
            north_pos = [x_mid - lane - 1, y_mid + self.num_lanes]
            self.north_south_lights.append(TrafficLight(north_pos, "GREEN", "NS"))

            # East-West lights (start RED)
            # West approach (cars moving east)
            west_pos = [x_mid - self.num_lanes - 1, y_mid - lane - 1]
            self.east_west_lights.append(TrafficLight(west_pos, "RED", "EW"))

            # East approach (cars moving west)
            east_pos = [x_mid + self.num_lanes, y_mid + lane]
            self.east_west_lights.append(TrafficLight(east_pos, "RED", "EW"))

    def step(self, cars=None):
        """
        Update traffic light states based on detection mode.

        Args:
            cars: List of Car objects (used for detection_cycle mode)
        """
        if self.detection == "time_cycle":
            self._time_cycle_step()
        elif self.detection == "detection_cycle":
            self._detection_cycle_step(cars)

    def _time_cycle_step(self):
        """Update lights based on fixed timing."""
        self.current_timer -= 1

        if self.current_state == "GREEN":
            if self.current_timer <= 0:
                # Switch to yellow
                self.current_state = "YELLOW"
                self.current_timer = self.yellow_time
                self._set_active_lights("YELLOW")

        elif self.current_state == "YELLOW":
            if self.current_timer <= 0:
                # Switch to red, then swap directions
                self._set_active_lights("RED")
                self.y_turn = not self.y_turn
                self.current_state = "GREEN"

                # Set new green time based on direction
                if self.y_turn:
                    self.current_timer = self.y_green_time
                else:
                    self.current_timer = self.x_green_time

                self._set_active_lights("GREEN")

    def _detection_cycle_step(self, cars):
        """
        Update lights based on traffic detection.
        Switch when no cars waiting or after max time.
        """
        # Count waiting cars in each direction
        ns_waiting = self._count_waiting_cars(cars, "NS")
        ew_waiting = self._count_waiting_cars(cars, "EW")

        self.current_timer -= 1

        if self.current_state == "GREEN":
            # Check if should switch (no waiting cars or timer expired)
            active_waiting = ns_waiting if self.y_turn else ew_waiting
            other_waiting = ew_waiting if self.y_turn else ns_waiting

            max_time = self.y_green_time if self.y_turn else self.x_green_time

            if (active_waiting == 0 and other_waiting > 0) or self.current_timer <= 0:
                self.current_state = "YELLOW"
                self.current_timer = self.yellow_time
                self._set_active_lights("YELLOW")

        elif self.current_state == "YELLOW":
            if self.current_timer <= 0:
                self._set_active_lights("RED")
                self.y_turn = not self.y_turn
                self.current_state = "GREEN"

                if self.y_turn:
                    self.current_timer = self.y_green_time
                else:
                    self.current_timer = self.x_green_time

                self._set_active_lights("GREEN")

    def _count_waiting_cars(self, cars, direction):
        """Count cars waiting at lights in given direction."""
        if not cars:
            return 0

        lights = self.north_south_lights if direction == "NS" else self.east_west_lights
        waiting = 0

        for car in cars:
            for light in lights:
                # Check if car is near light and not moving
                if (abs(car.position[0] - light.position[0]) <= 2 and
                    abs(car.position[1] - light.position[1]) <= 2 and
                    not car.has_moved):
                    waiting += 1
                    break

        return waiting

    def _set_active_lights(self, state):
        """Set state for currently active direction."""
        if self.y_turn:
            for light in self.north_south_lights:
                light.set_state(state)
        else:
            for light in self.east_west_lights:
                light.set_state(state)

    def get_all_lights(self):
        """Returns list of all traffic light objects."""
        return self.north_south_lights + self.east_west_lights

    def reset(self):
        """Reset to initial state."""
        self.y_turn = True
        self.current_timer = self.y_green_time
        self.current_state = "GREEN"

        for light in self.north_south_lights:
            light.set_state("GREEN")
        for light in self.east_west_lights:
            light.set_state("RED")