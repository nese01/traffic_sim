
import Environment as env
import numpy as np
import Cars as cr
"""
Traffic light class
Traffic light is an object that should be placed right before an intersection
Three states: "RED", "YELLOW", and "GREEN"
"""

class TrafficLightSet:
    def __init__(self, positions, y_green_time=30, x_green_time=30, lanes=1, detection="time_cycle"):
        #get all the maximum and minimum locations to determine where the traffic lights will be stored
        self.positions = positions
        self.north = []
        self.south = []
        self.west = []
        self.east = []
        for i in range(0, 4*lanes, 4):
            self.south.append(TrafficLight(positions[i], state="GREEN"))
            self.north.append(TrafficLight(positions[i+1], state="GREEN"))
            self.west.append(TrafficLight(positions[i+2], state="RED"))
            self.east.append(TrafficLight(positions[i+3], state="RED"))

        #decides whether y-axis is green or x-axis is green
        self.y_turn = True

        self.y_timer = y_green_time
        self.x_timer = x_green_time
        self.detection = detection

        self.yellow_timer = lanes*2
        self.priority = 0 #dummy code, will implement fully later


    def step(self):
        """
        Step function, default mode
        Will decrement the timer it has on itself and switch states automatically
        Perfect for global independent function
        For advanced simulations, requires location and nearby traffic analysis with detect_car
        """
        match self.detection:
            case None: return "Error, no detection type"

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

            case _:
                return "Error, detection type invalid"





    def detect_car(self, environment_grid):
        """
        Placeholder for potential additional mode
        Function to detect car, a dummy version for now that will try and search for nearby traffic lights in the
        Environment class for more accurate simulations.
        This makes more sense to do in environment class, might delete later
        """
        if environment_grid(self.get_pos()).has_car(): return False

    """
    Get Position
    Returns the position in numpy tuple format to make numpy calculation regarding position easier
    """

class TrafficLight():
    def __init__(self, position, state="RED"):
        self.position = position
        self.state = state



    def get_pos(self):
        return self.ypos, self.xpos
