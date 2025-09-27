pub const G: f64 = 6.67430e-11;
pub const DT: f64 = 0.01;
pub const EPSILON: f64 = 1e-6;

use std::error::Error;
use nalgebra::Vector2;
use serde::Serialize;
use rand::{random_range, Rng};
use rayon::prelude::{IntoParallelRefIterator, ParallelIterator};

#[derive(Debug, Clone, Copy)]
pub struct Body {
    pub mass: f64,
    pub position: Vector2<f64>,
    pub velocity: Vector2<f64>,
}

/// Randomly initializes bodies' position
pub fn initialize_system(n_bodies: usize) -> Vec<Body> {
    let mut rng = rand::rng();
    let mut bodies = Vec::with_capacity(n_bodies);
    for _ in 0..n_bodies {
        bodies.push(Body {
            position: Vector2::from([random_range(-1.0..1.0), random_range(-1.0..1.0)]),
            velocity: Vector2::from([random_range(-1e-3..1e-3), random_range(-1e-3..1e-3)]),
            mass: (rng.random::<f64>() + 0.1) * 1e10,
        });
    }
    bodies
}

/// Sequentially calculates bodies' forces
pub fn calculate_forces(bodies: &[Body]) -> Vec<nalgebra::Vector2<f64>> {
    let mut forces = vec![nalgebra::Vector2::from([0.,0.]); bodies.len()];
    for i in 0..bodies.len() {
        for j in 0..bodies.len() {
            if i == j {
                continue;
            }

            let r_vec = bodies[j].position - bodies[i].position;
            let dist_sq = r_vec.norm_squared() + EPSILON.powi(2);
            let force_mag = (G * bodies[i].mass * bodies[j].mass) / dist_sq;
            let force_vec = (r_vec / dist_sq.sqrt()) * force_mag;

            forces[i] += force_vec;
        }
    }
    forces
}


#[derive(Serialize)]
struct OutputRecord {
    timestep: usize,
    x: f64,
    y: f64,
}

/// Saves bodies' position history to csv
pub fn save_results(filepath: &str, history: &[Vec<Vector2<f64>>]) -> Result<(), Box<dyn Error>> {
    println!("Saving results to {}...", filepath);
    if let Some(dir) = std::path::Path::new(filepath).parent() {
        std::fs::create_dir_all(dir).expect("Could not create data directory");
    }
    let mut writer = csv::Writer::from_path(filepath)?;

    for (timestep, positions_at_step) in history.iter().enumerate() {
        for position in positions_at_step.iter() {
            let record = OutputRecord {
                timestep,
                x: position.x,
                y: position.y,
            };
            writer.serialize(record)?;
        }
    }

    writer.flush()?;
    Ok(())
}

/// Parallelly calculates  bodies' forces
pub fn calculate_forces_parallel(bodies: &[Body]) -> Vec<nalgebra::Vector2<f64>> {
    bodies.par_iter()
        .map(|current_body| {
            let mut total_force = nalgebra::Vector2::zeros();
            for other_body in bodies {
                if std::ptr::eq(current_body, other_body) {
                    continue;
                }

                let r_vec = other_body.position - current_body.position;
                let dist_sq = r_vec.norm_squared() + EPSILON.powi(2);
                let force_mag = (G * current_body.mass * other_body.mass) / dist_sq;
                let force_vec = (r_vec / dist_sq.sqrt()) * force_mag;

                total_force += force_vec;
            }
            total_force
        })
        .collect()
}