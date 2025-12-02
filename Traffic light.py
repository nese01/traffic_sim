
import Environment as env
import numpy as np
import Cars as cr
"""
Traffic light class
Traffic light is an object that should be placed right before an intersection
Three states: "RED", "YELLOW", and "GREEN"
"""

class TrafficLight:
    def __init__(self, x_pos, y_pos, weight, counterweight, init_state):
        self.xpos = x_pos
        self.ypos = y_pos
        self.timer = weight
        self.red_timer = counterweight
        self.state = init_state
        if init_state == "RED": self.current_time = counterweight
        else: self.current_time = weight
        self.nsew = None
        self.priority = 0 #dummy code, will implement fully later


    """
    Initialize location.
    Sets the value so it can check for every
    """
    def initialize_location(self, lights_environment):
        all_light_positions = lights_environment
        np.where(lights_environment.has_light(lights_environment.get_pos - (3,0)), self.set_cardinal(0))
        np.where(lights_environment.has_light(lights_environment.get_pos + (3, 0)), self.set_cardinal(1))
        np.where(lights_environment.has_light(lights_environment.get_pos - (0, 3)), self.set_cardinal(2))
        np.where(lights_environment.has_light(lights_environment.get_pos + (0, 3)), self.set_cardinal(3))
    """
    set cardinal
    """
    def set_cardinal(self, number):
        self.nsew = number

    """
    Timer function, default mode
    Will decrement the timer it has on itself and switch states automatically
    Perfect for global independent function
    For advanced simulations, requires location and nearby traffic analysis with detect_car
    """
    def global_timer(self):
        self.current_time = self.current_time - 1
        if self.state == "RED":
            if self.current_time < 0:
                self.state = "GREEN"
                self.current_time = self.timer

        if self.state == "GREEN":
            if self.current_time < 2:
                self.state = "YELLOW"

        elif self.state == "YELLOW":
            if self.current_time < 0:
                self.state = "RED"
                self.current_time = self.red_timer

    """
    Placeholder for potential additional mode
    Function to detect car, a dummy version for now that will try and search for nearby traffic lights in the
    Environment class for more accurate simulations.
    This makes more sense to do in environment class, might delete later
    """
    def detect_car(self, environment_grid):
        if environment_grid(self.get_pos()).has_car(): return False

    """
    Get Position
    Returns the position in numpy tuple format to make numpy calculation regarding position easier
    """
    def get_pos(self):
        return self.ypos, self.xpos
