"""
Simulation.py
Main driver to run and visualize traffic simulation data
Compares time-cycle vs detection-cycle traffic control
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
from Environment import Environment

# Simulation parameters
WIDTH = 20
HEIGHT = 20
SIMULATION_DURATION = 200

# Traffic scenarios
SCENARIOS = {
    'light': {'ns_rate': 0.1, 'ew_rate': 0.1},
    'rush_hour': {'ns_rate': 0.5, 'ew_rate': 0.5},
    'ns_heavy': {'ns_rate': 0.5, 'ew_rate': 0.1},  # Rush hour in NS direction
}


def run_single_simulation(traffic_mode="time_cycle", scenario='light',
                          duration=200, y_green=30, x_green=30,
                          num_lanes=1, animate=False):
    """
    Run a single simulation and return statistics.

    Args:
        traffic_mode: "time_cycle" or "detection_cycle"
        scenario: Traffic density scenario
        duration: Number of timesteps
        y_green: Green time for NS direction
        x_green: Green time for EW direction
        num_lanes: Number of lanes
        animate: Whether to save animation frames

    Returns:
        Dictionary of results and optional animation data
    """
    print(f"Running {traffic_mode} simulation - {scenario} traffic")

    # Get spawn rates for scenario
    rates = SCENARIOS[scenario]

    # Create environment
    env = Environment(
        traffic_mode=traffic_mode,
        grid_width=WIDTH,
        grid_height=HEIGHT,
        ns_spawn_rate=rates['ns_rate'],
        ew_spawn_rate=rates['ew_rate'],
        num_lanes=num_lanes,
        simulation_duration=duration,
        y_green_time=y_green,
        x_green_time=x_green
    )

    # Storage for statistics and animation
    time_series = {
        'time': [],
        'active_cars': [],
        'completed_cars': [],
        'avg_idle_time': [],
        'total_idle_time': [],
        'cars_moving': [],
        'cars_stopped': []
    }

    animation_frames = [] if animate else None

    # Run simulation
    for step in range(duration):
        env.step()

        # Collect statistics
        stats = env.get_statistics()
        time_series['time'].append(stats['time'])
        time_series['active_cars'].append(stats['total_cars_active'])
        time_series['completed_cars'].append(stats['total_cars_completed'])
        time_series['avg_idle_time'].append(stats['average_idle_time'])
        time_series['total_idle_time'].append(stats['total_idle_time'])
        time_series['cars_moving'].append(stats['cars_moving'])
        time_series['cars_stopped'].append(stats['cars_stopped'])

        # Save animation frame with light states
        if animate and step % 2 == 0:
            animation_frames.append({
                'grid': env.get_grid_state(),
                'ns_state': stats['ns_light_state'],
                'ew_state': stats['ew_light_state'],
                'time': stats['time'],
                'cars_stopped': stats['cars_stopped'],
                'cars_moving': stats['cars_moving']
            })

    # Final statistics
    final_stats = env.get_statistics()
    print(f"Completed: {final_stats['total_cars_completed']} cars")
    print(f"Final avg idle time: {final_stats['average_idle_time']:.2f}")
    print()

    return {
        'time_series': time_series,
        'final_stats': final_stats,
        'animation_frames': animation_frames,
        'env': env
    }


def run_comparison_study(scenarios=['light', 'rush_hour'], duration=200):
    results = {}

    for scenario in scenarios:
        print(f"\n{'=' * 50}")
        print(f"SCENARIO: {scenario.upper()}")
        print(f"{'=' * 50}\n")

        # Run time-cycle simulation
        results[f'{scenario}_time'] = run_single_simulation(
            traffic_mode="time_cycle",
            scenario=scenario,
            duration=duration
        )

        # Run detection-cycle simulation
        results[f'{scenario}_detection'] = run_single_simulation(
            traffic_mode="detection_cycle",
            scenario=scenario,
            duration=duration
        )

    return results


def plot_comparison_results(results):
    # Use a clean style
    plt.style.use('seaborn-v0_8-darkgrid')
    
    fig = plt.figure(figsize=(18, 13))
    gs = fig.add_gridspec(4, 2, hspace=0.35, wspace=0.25, 
                          height_ratios=[1, 1, 1, 0.8])

    # Extract scenario names and sort them consistently
    scenarios = sorted(list(set([k.rsplit('_', 1)[0] for k in results.keys()])))

    colors = {
        'time': '#E74C3C',      # Red
        'detection': '#2ECC71',  # Green
        'time_fill': '#F5B7B1',
        'detection_fill': '#A9DFBF'
    }

    # Title
    fig.suptitle('Traffic Light Control System Comparison\nTime-Cycle vs Detection-Cycle', 
                 fontsize=20, fontweight='bold', y=0.98)

    # Plot for each scenario
    for idx, scenario in enumerate(scenarios):
        time_result = results[f'{scenario}_time']
        detect_result = results[f'{scenario}_detection']

        # === PLOT 1: Average Idle Time Over Time (with fill) ===
        ax = fig.add_subplot(gs[idx, 0])
        
        time_data = time_result['time_series']['avg_idle_time']
        detect_data = detect_result['time_series']['avg_idle_time']
        time_axis = time_result['time_series']['time']
        
        ax.plot(time_axis, time_data, label='Time-Cycle', 
                color=colors['time'], linewidth=2.5, alpha=0.9)
        ax.fill_between(time_axis, 0, time_data, alpha=0.2, color=colors['time'])
        
        ax.plot(time_axis, detect_data, label='Detection-Cycle', 
                color=colors['detection'], linewidth=2.5, alpha=0.9)
        ax.fill_between(time_axis, 0, detect_data, alpha=0.2, color=colors['detection'])
        
        ax.set_xlabel('Time (steps)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Avg Idle Time (steps)', fontsize=11, fontweight='bold')
        ax.set_title(f'{scenario.replace("_", " ").title()} Traffic - Idle Time Over Time', 
                    fontsize=13, fontweight='bold', pad=10)
        ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(bottom=0)

        # === PLOT 2: Final Statistics Comparison ===
        ax = fig.add_subplot(gs[idx, 1])
        
        metrics = ['Avg Idle\nTime', 'Total\nCompleted', 'Active\nCars']
        time_values = [
            time_result['final_stats']['average_idle_time'],
            time_result['final_stats']['total_cars_completed'],
            time_result['final_stats']['total_cars_active']
        ]
        detect_values = [
            detect_result['final_stats']['average_idle_time'],
            detect_result['final_stats']['total_cars_completed'],
            detect_result['final_stats']['total_cars_active']
        ]
        
        x_pos = np.arange(len(metrics))
        bar_width = 0.35
        
        bars1 = ax.bar(x_pos - bar_width/2, time_values, bar_width, label='Time-Cycle', 
                      color=colors['time'], alpha=0.8, edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x_pos + bar_width/2, detect_values, bar_width, label='Detection-Cycle', 
                      color=colors['detection'], alpha=0.8, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_ylabel('Value', fontsize=11, fontweight='bold')
        ax.set_title(f'{scenario.replace("_", " ").title()} Traffic - Final Statistics', 
                    fontsize=13, fontweight='bold', pad=10)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(metrics, fontsize=10)
        ax.legend(fontsize=10, framealpha=0.9, loc='upper left')
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')

    # === BOTTOM ROW: Overall Summary ===
    
    # Overall Idle Time Comparison
    ax = fig.add_subplot(gs[3, 0])
    x_pos = np.arange(len(scenarios))
    bar_width = 0.35
    
    time_idle = [results[f'{s}_time']['final_stats']['average_idle_time'] for s in scenarios]
    detect_idle = [results[f'{s}_detection']['final_stats']['average_idle_time'] for s in scenarios]
    
    bars1 = ax.bar(x_pos - bar_width/2, time_idle, bar_width, label='Time-Cycle', 
                   color=colors['time'], alpha=0.85, edgecolor='black', linewidth=2)
    bars2 = ax.bar(x_pos + bar_width/2, detect_idle, bar_width, label='Detection-Cycle', 
                   color=colors['detection'], alpha=0.85, edgecolor='black', linewidth=2)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_ylabel('Average Idle Time (steps)', fontsize=13, fontweight='bold')
    ax.set_title('Overall Average Idle Time Comparison', fontsize=15, fontweight='bold', pad=15)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([s.replace('_', ' ').title() for s in scenarios], fontsize=12)
    ax.legend(fontsize=12, framealpha=0.95, loc='upper left')
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax.set_ylim(bottom=0)
    
    # Efficiency Improvement
    ax = fig.add_subplot(gs[3, 1])
    improvements = [(time_idle[i] - detect_idle[i]) / time_idle[i] * 100 
                    if time_idle[i] > 0 else 0
                    for i in range(len(scenarios))]
    colors_bar = ['#27AE60' if imp > 0 else '#E74C3C' for imp in improvements]
    
    bars = ax.bar(x_pos, improvements, bar_width*2, color=colors_bar, 
                  alpha=0.85, edgecolor='black', linewidth=2)
    
    # Add value labels
    for i, (bar, imp) in enumerate(zip(bars, improvements)):
        height = bar.get_height()
        y_offset = 2 if height > 0 else -2
        v_align = 'bottom' if height > 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2., height + y_offset,
               f'{imp:.1f}%',
               ha='center', va=v_align, 
               fontsize=12, fontweight='bold', 
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='black'))
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=2.5)
    ax.set_ylabel('Efficiency Improvement (%)', fontsize=13, fontweight='bold')
    ax.set_title('Detection-Cycle Performance Gain', fontsize=15, fontweight='bold', pad=15)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([s.replace('_', ' ').title() for s in scenarios], fontsize=12)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    # Add legend for improvement colors
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#27AE60', alpha=0.85, edgecolor='black', 
                            label='Detection Better'),
                      Patch(facecolor='#E74C3C', alpha=0.85, edgecolor='black', 
                            label='Time Better')]
    ax.legend(handles=legend_elements, fontsize=11, framealpha=0.95, loc='upper left')

    plt.savefig('traffic_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Saved comparison plot as 'traffic_comparison.png'")
    plt.show()


def animate_simulation(frames, scenario_name, traffic_mode, fps=10):
    """
    Create an enhanced animation of the simulation.

    Args:
        frames: List of frame dictionaries with grid and metadata
        scenario_name: Name for the animation
        traffic_mode: "time_cycle" or "detection_cycle"
        fps: Frames per second
    """
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[3, 1], hspace=0.3, wspace=0.3)
    
    # Main grid view
    ax_main = fig.add_subplot(gs[0, :])
    
    # Stats displays
    ax_stats = fig.add_subplot(gs[1, 0])
    ax_legend = fig.add_subplot(gs[1, 1])
    
    # Custom colormap with better colors
    colors_map = ['#2C3E50', '#3498DB', '#E74C3C', '#F39C12', '#27AE60']  # empty, car, red, yellow, green
    cmap = ListedColormap(colors_map)
    
    # Initial frame
    im = ax_main.imshow(frames[0]['grid'], cmap=cmap, vmin=0, vmax=4, 
                       interpolation='nearest', aspect='equal')
    
    # Add grid lines for intersection
    grid_size = frames[0]['grid'].shape[0]
    mid = grid_size // 2
    ax_main.axhline(y=mid-0.5, color='yellow', linewidth=3, alpha=0.5, linestyle='--')
    ax_main.axvline(x=mid-0.5, color='yellow', linewidth=3, alpha=0.5, linestyle='--')
    
    # Title with mode
    mode_text = traffic_mode.replace("_", " ").title()
    title = ax_main.text(0.5, 1.05, f'{scenario_name.replace("_", " ").title()} Traffic - {mode_text}',
                        transform=ax_main.transAxes, ha='center', 
                        fontsize=16, fontweight='bold')
    
    # Time display
    time_text = ax_main.text(0.02, 0.98, '', transform=ax_main.transAxes,
                            fontsize=14, fontweight='bold', va='top',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Traffic light status indicators
    ns_light_circle = Circle((0.15, 0.92), 0.03, transform=ax_main.transAxes, 
                            facecolor='gray', edgecolor='black', linewidth=2)
    ew_light_circle = Circle((0.15, 0.85), 0.03, transform=ax_main.transAxes,
                            facecolor='gray', edgecolor='black', linewidth=2)
    ax_main.add_patch(ns_light_circle)
    ax_main.add_patch(ew_light_circle)
    
    ns_label = ax_main.text(0.19, 0.92, 'N-S:', transform=ax_main.transAxes,
                           fontsize=12, fontweight='bold', va='center')
    ew_label = ax_main.text(0.19, 0.85, 'E-W:', transform=ax_main.transAxes,
                           fontsize=12, fontweight='bold', va='center')
    
    ax_main.set_xlabel('East →', fontsize=12, fontweight='bold')
    ax_main.set_ylabel('North ↑', fontsize=12, fontweight='bold')
    ax_main.set_xticks([])
    ax_main.set_yticks([])
    
    # Stats panel
    ax_stats.axis('off')
    stats_text = ax_stats.text(0.1, 0.5, '', transform=ax_stats.transAxes,
                              fontsize=12, va='center', family='monospace',
                              bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    # Legend panel
    ax_legend.axis('off')
    legend_items = [
        ('Empty Road', colors_map[0]),
        ('Car (Moving)', colors_map[1]),
        ('Red Light', colors_map[2]),
        ('Yellow Light', colors_map[3]),
        ('Green Light', colors_map[4])
    ]
    
    y_pos = 0.9
    for label, color in legend_items:
        rect = Rectangle((0.1, y_pos - 0.05), 0.1, 0.1, transform=ax_legend.transAxes,
                        facecolor=color, edgecolor='black', linewidth=1.5)
        ax_legend.add_patch(rect)
        ax_legend.text(0.25, y_pos, label, transform=ax_legend.transAxes,
                      fontsize=11, va='center', fontweight='bold')
        y_pos -= 0.18
    
    def update(frame_num):
        frame = frames[frame_num]
        
        # Update grid
        im.set_array(frame['grid'])
        
        # Update time
        time_text.set_text(f"Time: {frame['time']}")
        
        # Update traffic lights with colors
        light_colors = {'RED': '#E74C3C', 'YELLOW': '#F39C12', 'GREEN': '#27AE60'}
        ns_light_circle.set_facecolor(light_colors.get(frame['ns_state'], 'gray'))
        ew_light_circle.set_facecolor(light_colors.get(frame['ew_state'], 'gray'))
        
        # Update stats
        stats = f"Cars Stopped: {frame['cars_stopped']:2d}\nCars Moving:  {frame['cars_moving']:2d}"
        stats_text.set_text(stats)
        
        return [im, time_text, ns_light_circle, ew_light_circle, stats_text]
    
    anim = animation.FuncAnimation(fig, update, frames=len(frames),
                                  interval=1000/fps, blit=True, repeat=True)
    
    filename = f'traffic_animation_{scenario_name}_{traffic_mode}.gif'
    anim.save(filename, writer='pillow', fps=fps)
    print(f"✓ Saved animation as '{filename}'")
    plt.close()


if __name__ == "__main__":
    print("="*60)
    print("  TRAFFIC LIGHT SIMULATION COMPARISON")
    print("="*60)
    print("\n📊 Comparing Time-Cycle vs Detection-Cycle traffic control")
    print("   across different traffic scenarios\n")

    # Run full comparison study
    results = run_comparison_study(
        scenarios=['light', 'rush_hour', 'ns_heavy'],
        duration=SIMULATION_DURATION
    )

    # Generate comparison plots
    print("\n Generating comparison plots...")
    plot_comparison_results(results)

    # Optional: Generate animations (can be slow)
    print("\n" + "="*60)
    generate_animations = input("Generate animations? (y/n): ").lower() == 'y'

    if generate_animations:
        print("\n Generating animations (this may take a minute)...")
        for scenario in ['light', 'rush_hour']:
            print(f"  • Creating {scenario} animations...")
            # Animate time-cycle
            result = run_single_simulation(
                traffic_mode="time_cycle",
                scenario=scenario,
                duration=100,
                animate=True
            )
            animate_simulation(result['animation_frames'], scenario, 'time_cycle')

            # Animate detection-cycle
            result = run_single_simulation(
                traffic_mode="detection_cycle",
                scenario=scenario,
                duration=100,
                animate=True
            )
            animate_simulation(result['animation_frames'], scenario, 'detection_cycle')

    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)
    print("\n Output files:")
    print("   • traffic_comparison.png - Detailed comparison graphs")
    if generate_animations:
        print("   • traffic_animation_*.gif - Animated visualizations")
    print("\n")