//! GROBID client: Docker management and PDF → TEI conversion.

use std::path::Path;
use std::process::Command;
use std::time::Instant;

use crate::config;

/// Check if the GROBID server is alive.
pub async fn is_grobid_alive() -> bool {
    let url = config::health_url();
    let client = reqwest::Client::new();
    match client.get(&url).send().await {
        Ok(resp) => resp.status().as_u16() == 200,
        Err(_) => false,
    }
}

/// Start the GROBID Docker container if not already running.
pub async fn start_grobid() -> bool {
    if is_grobid_alive().await {
        tracing::info!("GROBID already running at {}", config::grobid_url());
        return true;
    }

    if which("docker").is_none() {
        tracing::warn!(
            "Docker not found. Start GROBID manually at {}",
            config::grobid_url()
        );
        return is_grobid_alive().await;
    }

    let container = config::grobid_container();
    let image = config::grobid_image();
    let port = config::grobid_port();

    // Remove any existing container.
    let _ = Command::new("docker")
        .args(["rm", "-f", &container])
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .status();

    let status = Command::new("docker")
        .args([
            "run",
            "-d",
            "--rm",
            "--init",
            "--ulimit",
            "core=0",
            "-p",
            &format!("{}:8070", port),
            "--name",
            &container,
            &image,
        ])
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .status();

    if let Err(e) = status {
        tracing::error!("Failed to start GROBID: {e}");
        return false;
    }

    tracing::info!("Starting GROBID container {}...", container);
    for i in 0..120 {
        if is_grobid_alive().await {
            tracing::info!("GROBID ready after {}s", i + 1);
            return true;
        }
        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
    }

    tracing::error!("GROBID did not become ready in time");
    false
}

fn which(cmd: &str) -> Option<std::path::PathBuf> {
    if let Some(paths) = std::env::var_os("PATH") {
        for dir in std::env::split_paths(&paths) {
            let candidate = dir.join(cmd);
            if candidate.is_file() {
                return Some(candidate);
            }
        }
    }
    None
}

/// Convert a PDF to TEI XML using the GROBID service.
pub async fn pdf_to_tei(
    client: &reqwest::Client,
    pdf_path: &Path,
    tei_path_fn: &dyn Fn(&Path) -> std::path::PathBuf,
) -> (u16, Option<std::path::PathBuf>, f64) {
    let started = Instant::now();
    let url = format!("{}/api/processFulltextDocument", config::grobid_url());

    let pdf_bytes = match std::fs::read(pdf_path) {
        Ok(b) => b,
        Err(e) => {
            tracing::error!("Failed to read PDF {}: {e}", pdf_path.display());
            return (0, None, elapsed(started));
        }
    };

    let part = reqwest::multipart::Part::bytes(pdf_bytes)
        .file_name(
            pdf_path
                .file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .to_string(),
        )
        .mime_str("application/pdf")
        .unwrap_or_else(|_| reqwest::multipart::Part::text(""));

    let form = reqwest::multipart::Form::new()
        .text(
            "consolidateHeader",
            config::GROBID_CONSOLIDATE_HEADER.to_string(),
        )
        .part("input", part);

    let resp = client.post(&url).multipart(form).send().await;
    let elapsed = elapsed(started);

    match resp {
        Ok(resp) => {
            let status = resp.status().as_u16();
            if status != 200 {
                return (status, None, elapsed);
            }
            let tei = resp.text().await.unwrap_or_default();
            if tei.is_empty() {
                return (status, None, elapsed);
            }
            let out_path = tei_path_fn(pdf_path);
            if let Err(e) = std::fs::write(&out_path, tei.as_bytes()) {
                tracing::error!("Failed to write TEI {}: {e}", out_path.display());
                return (status, None, elapsed);
            }
            (status, Some(out_path), elapsed)
        }
        Err(e) => {
            tracing::error!("GROBID request failed: {e}");
            (0, None, elapsed)
        }
    }
}

fn elapsed(start: Instant) -> f64 {
    start.elapsed().as_secs_f64()
}
