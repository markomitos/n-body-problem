import numpy as np
import os

G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
DT = 0.01        # Time step (s)
EPSILON = 1e-6     # Softening factor to avoid division by zero

def initialize_system(n_bodies):
    """Initializes the system with n_bodies with random values."""
    print(f"Initializing system with {n_bodies} bodies.")
    positions = np.random.rand(n_bodies, 2) * 2 - 1
    velocities = (np.random.rand(n_bodies, 2) * 2 - 1) * 1e-3
    masses = (np.random.rand(n_bodies, 1) + 0.1) * 1e10
    return positions, velocities, masses

def update_velocities(velocities, forces, masses, dt):
    """Updates the velocities of the bodies."""
    return velocities + (forces / masses) * dt

def update_positions(positions, velocities, dt):
    """Updates the positions of the bodies."""
    return positions + velocities * dt

def save_results(filepath, history):
    """Saves the simulation history to a CSV file."""
    print(f"Saving results to file: {filepath}")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write("timestep,body_id,x,y\n")
        for timestep, positions in enumerate(history):
            for body_id, pos in enumerate(positions):
                f.write(f"{timestep},{body_id},{pos[0]},{pos[1]}\n")
    print("Results saved successfully.")