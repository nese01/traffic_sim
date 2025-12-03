
import numpy as np
import matplotlib as plt

import Environment as env
import TrafficLight as tl

"""
Simulation
Main driver to visualize the data from our mini simulation

"""
# ----------------------------------------------------
# ---------------Initialized Variables----------------
WIDTH = 30
HEIGHT = 60
SIMULATION_UPTIME = 100
Y_LANE_CHANCE = 0.4
X_LANE_CHANCE = 0.1
#-----------------------------------------------------


def run_one_sim(type_sim="time_cycle", light_times = (45, 15), seconds = 40, animate=True):
    """
    If animate is true, each cycle record the colors and positions of the light, alongside the locations
    of cars from the environment, and add it to 2 lists which will be used after the simulation with the
    animate_plot method.
    Light times = (int1, int2) ; where first int is the x green light uptime and second int is y green light uptime
    """
    print("Starting Simulation")
    data = env.Environment(type_sim, grid_width=WIDTH, grid_height=HEIGHT, spawn_rate=Y_LANE_CHANCE)
    if animate:
        light_list = []
        cat_positions = []
        for i in range(seconds):
            data.step()
            car_positions = data.get_grid_state()
            light_list = data.get_light_grid()
    else:
        for i in range(seconds):
            data.step()

    print("Ending Simulation")
    print("Average idle time = " + data.get_average_idle_time())
    return

def run_multiple_simulations():
    return None

def animate_plot(traffic_states, car_states, number_lanes):
    return None


