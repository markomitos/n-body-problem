import numpy as np
import time
import argparse
import os
import multiprocessing
from functools import partial

from utils import (
    G, DT, EPSILON,
    initialize_system,
    update_velocities,
    update_positions,
    save_results
)


def calculate_force_for_body(body_index, positions, masses):
    """Worker function: calculates force for a single body."""
    force_vec = np.zeros(2)
    my_pos = positions[body_index]
    my_mass = masses[body_index]
    for j in range(len(positions)):
        if body_index == j:
            continue
        r_vec = positions[j] - my_pos
        dist_sq = np.sum(r_vec ** 2) + EPSILON ** 2
        force_mag = G * my_mass * masses[j] / dist_sq
        force_vec += force_mag * r_vec / np.sqrt(dist_sq)
    return force_vec


def main():
    parser = argparse.ArgumentParser(description="Parallel N-body simulation.")
    parser.add_argument('--n-bodies', type=int, default=100, help='Number of bodies.')
    parser.add_argument('--timesteps', type=int, default=1000, help='Number of time steps.')
    parser.add_argument('--cores', type=int, default=os.cpu_count(), help='Number of CPU cores.')
    parser.add_argument('--output-file', type=str, default='data/parallel_output.csv', help='Output CSV file.')
    args = parser.parse_args()

    positions, velocities, masses = initialize_system(args.n_bodies)
    position_history = [positions.copy()]

    print(f"Starting parallel simulation on {args.cores} cores...")
    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=args.cores) as pool:
        for step in range(args.timesteps):
            worker_func = partial(calculate_force_for_body, positions=positions, masses=masses)
            forces_list = pool.map(worker_func, range(args.n_bodies))
            forces = np.array(forces_list)

            velocities = update_velocities(velocities, forces, masses, DT)
            positions = update_positions(positions, velocities, DT)
            position_history.append(positions.copy())
            if (step + 1) % 100 == 0:
                print(f"  ... Step {step + 1}/{args.timesteps}")

    end_time = time.perf_counter()
    print("Simulation finished.")
    print(f"Total execution time (parallel, {args.cores} cores): {end_time - start_time:.4f} seconds")

    save_results(args.output_file, position_history)


if __name__ == "__main__":
    main()