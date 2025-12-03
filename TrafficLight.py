
import Environment as env
import numpy as np
import Cars as cr
"""
Traffic light class
Traffic light is an object that should be placed right before an intersection
Three states: "RED", "YELLOW", and "GREEN"
"""

class TrafficLight:
    def __init__(self, x_pos, y_pos, weight=30, counterweight=30, init_state="RED", yellow_timer=2):
        self.xpos = x_pos
        self.ypos = y_pos
        self.timer = weight
        self.red_timer = counterweight
        self.state = init_state
        if init_state == "RED": self.current_time = counterweight
        else: self.current_time = weight
        self.yellow_timer = yellow_timer
        self.priority = 0 #dummy code, will implement fully later

    """
    Step function, default mode
    Will decrement the timer it has on itself and switch states automatically
    Perfect for global independent function
    For advanced simulations, requires location and nearby traffic analysis with detect_car
    """
    def step(self, type=None):
        match type:
            case None: return "Error, please enter a type"

            case "time_cycle":
                self.current_time = self.current_time - 1
                if self.state == "RED":
                    if self.current_time < 0:
                        self.state = "GREEN"
                        self.current_time = self.timer

                elif self.state == "GREEN":
                    if self.current_time < 2:
                        self.state = "YELLOW"

                elif self.state == "YELLOW":
                    if self.current_time < 0:
                        self.state = "RED"
                        self.current_time = self.red_timer
            case "detection cycle":
                return #implement later




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
