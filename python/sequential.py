import numpy as np
import time
import argparse

from utils import (
    G, DT, EPSILON,
    initialize_system,
    update_velocities,
    update_positions,
    save_results
)

def calculate_forces(positions, masses):
    """Calculates the gravitational forces between all pairs of bodies."""
    n_bodies = positions.shape[0]
    forces = np.zeros_like(positions)
    for i in range(n_bodies):
        for j in range(n_bodies):
            if i == j:
                continue
            r_vec = positions[j] - positions[i]
            dist_sq = np.sum(r_vec**2) + EPSILON**2
            force_mag = G * masses[i] * masses[j] / dist_sq
            force_vec = force_mag * r_vec / np.sqrt(dist_sq)
            forces[i] += force_vec
    return forces

def main():
    parser = argparse.ArgumentParser(description="Sequential N-body simulation.")
    parser.add_argument('--n-bodies', type=int, default=100, help='Number of bodies.')
    parser.add_argument('--timesteps', type=int, default=1000, help='Number of time steps.')
    parser.add_argument('--output-file', type=str, default='data/sequential_output.csv', help='Output CSV file.')
    args = parser.parse_args()

    positions, velocities, masses = initialize_system(args.n_bodies)
    position_history = [positions.copy()]

    print("Starting sequential simulation...")
    start_time = time.perf_counter()

    for step in range(args.timesteps):
        forces = calculate_forces(positions, masses)
        velocities = update_velocities(velocities, forces, masses, DT)
        positions = update_positions(positions, velocities, DT)
        position_history.append(positions.copy())
        if (step + 1) % 100 == 0:
            print(f"  ... Step {step + 1}/{args.timesteps}")

    end_time = time.perf_counter()
    print("Simulation finished.")
    print(f"Total execution time (sequential): {end_time - start_time:.4f} seconds")

    save_results(args.output_file, position_history)

if __name__ == "__main__":
    main()