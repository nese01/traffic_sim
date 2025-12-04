# Traffic Light Simulation

**Authors:** Enes Ozcan & Saif Alhasan Sahib

Compares fixed-time vs. adaptive traffic signal control across different traffic scenarios.

## Quick Start

**Install dependencies:**
```bash
pip install numpy matplotlib pillow
```

**Run simulation:**
```bash
python Simulation.py
```

## Files

- `Car.py` - Vehicle agent class
- `TrafficLight.py` - Signal control logic
- `Environment.py` - Simulation engine
- `Simulation.py` - Run experiments & generate plots

## Output

- `traffic_comparison.png` - Performance comparison graphs
- `traffic_animation_*.gif` - Visual simulations (optional)

## Key Findings

- **Light traffic:** Adaptive wins (19.7% faster)
- **Rush hour:** Fixed-time wins (5.6% faster)
- **Asymmetric flow:** Fixed-time wins (4.0% faster)

**Conclusion:** No universal winner—optimal system depends on traffic conditions.