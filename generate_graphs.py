import subprocess
import re
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

RUNS_PER_CONFIG = 30

S = 0.15
P = 0.85

STRONG_SCALING_N_BODIES = 100

WEAK_SCALING_WORK_PER_CORE = 20

CORE_COUNTS = [1, 2, 4, 8, 16]

RUST_EXECUTABLE = os.path.join('rust', 'target', 'release', 'runner')
PYTHON_SCRIPT = os.path.join('python', 'parallel.py')


def parse_time_from_output(output):
    match = re.search(r"Total execution time.*: ([\d.]+)", output)
    if match:
        return float(match.group(1))
    return None


def run_benchmarks(configs, program_type):
    results = []

    print(f"\nRunning benchmarks for {program_type}...")
    for config in tqdm(configs, desc=f"Benchmarking {program_type}"):
        for run_num in range(RUNS_PER_CONFIG):
            if program_type == 'rust':
                command = [
                    RUST_EXECUTABLE,
                    '--n-bodies', str(config['n_bodies']),
                    '--timesteps', '500',
                    '--mode', config['mode'],
                    '--cores', str(config['cores'])
                ]
            elif program_type == 'python':
                command = [
                    'python', PYTHON_SCRIPT,
                    '--n-bodies', str(config['n_bodies']),
                    '--timesteps', '500',
                    '--cores', str(config['cores'])
                ]

            process = subprocess.run(command, capture_output=True, text=True)

            if process.returncode != 0:
                print(f"Error running command: {' '.join(command)}")
                print(process.stderr)
                continue

            time = parse_time_from_output(process.stdout)
            if time is not None:
                results.append({
                    'cores': config['cores'],
                    'n_bodies': config['n_bodies'],
                    'time': time
                })

    return pd.DataFrame(results)


def analyze_and_plot(df, s, p, scaling_type, program_name):
    if df.empty:
        print(f"No data to analyze for {program_name} {scaling_type} scaling.")
        return

    stats = df.groupby('cores')['time'].agg(['mean', 'std']).reset_index()
    stats.rename(columns={'mean': 'mean_time', 'std': 'std_dev'}, inplace=True)

    baseline_time = stats.loc[stats['cores'] == 1, 'mean_time'].iloc[0]

    if scaling_type == 'strong':
        stats['measured_speedup'] = baseline_time / stats['mean_time']
        stats['theoretical_speedup'] = 1 / (s + p / stats['cores'])
        title = f'Jako Skaliranje ({program_name})'
    else:  # weak
        stats['measured_speedup'] = stats['cores'] * baseline_time / stats['mean_time']
        stats['theoretical_speedup'] = s + p * stats['cores']
        title = f'Slabo Skaliranje ({program_name})'

    print(f"\n--- Tabela: {title} ---")
    print(stats.to_markdown(index=False))

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(stats['cores'], stats['measured_speedup'], marker='o', linestyle='-', label='Ostvareno ubrzanje')
    ax.plot(stats['cores'], stats['theoretical_speedup'], marker='x', linestyle='--', label='Teorijsko ubrzanje')
    ax.plot(stats['cores'], stats['cores'], linestyle=':', color='gray', label='Idealno (linearno) ubrzanje')
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Broj procesorskih jezgara (P)', fontsize=12)
    ax.set_ylabel('Ubrzanje (Speedup)', fontsize=12)
    ax.legend(fontsize=10)
    ax.set_xticks(stats['cores'])
    ax.grid(True)

    filename = f"{scaling_type}_scaling_{program_name.lower()}.png"
    plt.savefig(filename)
    print(f"Grafik sačuvan u '{filename}'")
    plt.close(fig)


def main():

    strong_configs_rust = [{'cores': c, 'n_bodies': STRONG_SCALING_N_BODIES, 'mode': 'parallel'} for c in CORE_COUNTS]
    strong_configs_rust.insert(0, {'cores': 1, 'n_bodies': STRONG_SCALING_N_BODIES, 'mode': 'sequential'})  # Baseline

    weak_configs_rust = [{'cores': c, 'n_bodies': c * WEAK_SCALING_WORK_PER_CORE, 'mode': 'parallel'} for c in
                         CORE_COUNTS]
    weak_configs_rust[0]['mode'] = 'sequential'

    strong_configs_python = [{'cores': c, 'n_bodies': STRONG_SCALING_N_BODIES} for c in CORE_COUNTS]
    weak_configs_python = [{'cores': c, 'n_bodies': c * WEAK_SCALING_WORK_PER_CORE} for c in CORE_COUNTS]

    strong_df_rust = run_benchmarks(strong_configs_rust, 'rust')
    strong_df_rust.to_csv('strong_scaling_rust_results.csv', index=False)
    analyze_and_plot(strong_df_rust, S, P, 'strong', 'Rust')

    weak_df_rust = run_benchmarks(weak_configs_rust, 'rust')
    weak_df_rust.to_csv('weak_scaling_rust_results.csv', index=False)
    analyze_and_plot(weak_df_rust, S, P, 'weak', 'Rust')

    strong_df_python = run_benchmarks(strong_configs_python, 'python')
    strong_df_python.to_csv('strong_scaling_python_results.csv', index=False)
    analyze_and_plot(strong_df_python, S, P, 'strong', 'Python')

    weak_df_python = run_benchmarks(weak_configs_python, 'python')
    weak_df_python.to_csv('weak_scaling_python_results.csv', index=False)
    analyze_and_plot(weak_df_python, S, P, 'weak', 'Python')


if __name__ == "__main__":
    main()