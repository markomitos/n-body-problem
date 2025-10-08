import pandas as pd
import numpy as np
import os

S = 0.15
P = 0.85

RAW_DATA_FILES = [
    'strong_scaling_python_results.csv',
    'strong_scaling_rust_results.csv',
    'weak_scaling_python_results.csv',
    'weak_scaling_rust_results.csv'
]


def create_strong_scaling_df(df):
    stats = df.groupby('cores')['time'].agg(['mean', 'std']).reset_index()
    baseline_time = stats.loc[stats['cores'] == 1, 'mean'].iloc[0]

    stats['measured_speedup'] = baseline_time / stats['mean']
    stats['theoretical_speedup'] = 1 / (S + P / stats['cores'])

    output_df = pd.DataFrame({
        'Broj jezgara (N)': stats['cores'],
        'Srednje vreme (s)': stats['mean'],
        'Standardna devijacija': stats['std'],
        'Izmereno ubrzanje': stats['measured_speedup'],
        'Teorijsko ubrzanje (Amdal)': stats['theoretical_speedup']
    })
    return output_df


def create_weak_scaling_df(df):
    stats = df.groupby(['cores', 'n_bodies'])['time'].agg(['mean', 'std']).reset_index()
    baseline_time = stats.loc[stats['cores'] == 1, 'mean'].iloc[0]

    stats['efficiency'] = baseline_time / stats['mean']

    output_df = pd.DataFrame({
        'Broj jezgara (P)': stats['cores'],
        'Veličina problema (N)': stats['n_bodies'],
        'Srednje vreme (s)': stats['mean'],
        'Standardna devijacija': stats['std'],
        'Efikasnost': stats['efficiency']
    })
    return output_df


def main():

    for filename in RAW_DATA_FILES:
        if not os.path.exists(filename):
            continue

        try:
            df = pd.read_csv(filename)

            scaling_type = 'strong' if 'strong' in filename else 'weak'

            if scaling_type == 'strong':
                table_df = create_strong_scaling_df(df)
            else:
                table_df = create_weak_scaling_df(df)

            output_filename = filename.replace('_results.csv', '').replace('scaling_', 'scaling_table_') + '.csv'

            table_df.to_csv(output_filename, index=False, sep=';', decimal=',', encoding='utf-8-sig')

            print(f"'{filename}' saved to '{output_filename}'")

        except Exception as e:
            print(f"Error during creating '{filename}': {e}")


if __name__ == '__main__':
    main()