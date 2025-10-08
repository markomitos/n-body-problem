use nbody_lib::{
    initialize_system, calculate_forces, calculate_forces_parallel,
    save_results, Body, DT
};
use nalgebra::Vector2;
use clap::{Parser, ValueEnum};
use std::time::{Duration, Instant};

/// Enum to represent the simulation mode
#[derive(ValueEnum, Debug, Clone, Copy)]
enum Mode {
    Sequential,
    Parallel,
}

/// A simple N-body simulation in Rust
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Cli {
    /// Number of bodies in the simulation
    #[arg(long, default_value_t = 100)]
    n_bodies: usize,

    /// Number of timesteps to simulate
    #[arg(long, default_value_t = 1000)]
    timesteps: usize,

    /// Simulation mode
    #[arg(long, value_enum, default_value_t = Mode::Sequential)]
    mode: Mode,

    /// Output CSV file path
    #[arg(long, default_value_t = String::from("data/output.csv"))]
    output_file: String,

    /// Number of threads to use in parallel mode. Defaults to all available cores.
    #[arg(long)]
    cores: Option<usize>,
}

/// Parses CLI arguments and configures the global thread pool.
fn setup_environment() -> Cli {
    let cli = Cli::parse();
    if let Some(num_cores) = cli.cores {
        rayon::ThreadPoolBuilder::new()
            .num_threads(num_cores)
            .build_global()
            .unwrap();
    }
    cli
}

/// Runs the N-body simulation and returns the history of body positions.
fn run_simulation(bodies: &mut Vec<Body>, timesteps: usize, mode: Mode) -> Vec<Vec<Vector2<f64>>> {
    let mut position_history: Vec<Vec<Vector2<f64>>> = Vec::with_capacity(timesteps + 1);
    let get_positions = |b: &[Body]| b.iter().map(|body| body.position).collect();

    position_history.push(get_positions(bodies));

    println!("Starting {:?} simulation for {} timesteps...", mode, timesteps);
    let mut force_calculation_duration = Duration::ZERO;

    for step in 0..timesteps {
        let force_timer = Instant::now();
        let forces = match mode {
            Mode::Sequential => calculate_forces(bodies),
            Mode::Parallel => calculate_forces_parallel(bodies),
        };
        force_calculation_duration += force_timer.elapsed();

        for (i, body) in bodies.iter_mut().enumerate() {
            let acceleration = forces[i] / body.mass;
            body.velocity += acceleration * DT;
            body.position += body.velocity * DT;
        }

        position_history.push(get_positions(bodies));

        if (step + 1) % 100 == 0 {
            println!("... Step {}/{}", step + 1, timesteps);
        }
    }
    println!("Total force calculation time: {:.4?}", force_calculation_duration);

    position_history
}

fn main() {
    let cli = setup_environment();
    println!("Initializing system with {} bodies...", cli.n_bodies);

    let mut bodies = initialize_system(cli.n_bodies);

    let start_time = Instant::now();
    let position_history = run_simulation(&mut bodies, cli.timesteps, cli.mode);
    let duration = start_time.elapsed();

    println!("Simulation finished.");
    println!("Total execution time ({:?}): {:.4?}", cli.mode, duration);

    save_results(&cli.output_file, &position_history).expect("Failed to save results");
    println!("Results saved successfully to {}.", cli.output_file);
}