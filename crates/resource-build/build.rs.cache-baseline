use sha2::{Digest, Sha256};
use std::path::Path;

fn collect(path: &Path, root: &Path, digest: &mut Sha256) {
    let mut paths = std::fs::read_dir(path)
        .unwrap()
        .map(|entry| entry.unwrap().path())
        .collect::<Vec<_>>();
    paths.sort();
    for path in paths {
        if path.is_dir() {
            collect(&path, root, digest);
        } else if path.extension().is_some_and(|extension| extension == "rs") {
            add(&path, root, digest);
        }
    }
}

fn add(path: &Path, root: &Path, digest: &mut Sha256) {
    println!("cargo:rerun-if-changed={}", path.display());
    digest.update(
        path.strip_prefix(root)
            .unwrap()
            .to_string_lossy()
            .replace('\\', "/")
            .as_bytes(),
    );
    digest.update(std::fs::read(path).unwrap());
}

fn main() {
    let manifest = std::path::PathBuf::from(std::env::var_os("CARGO_MANIFEST_DIR").unwrap());
    let root = manifest.parent().unwrap().parent().unwrap();
    let mut digest = Sha256::new();
    for relative in ["crates/core/src", "crates/resource-build/src"] {
        collect(&root.join(relative), root, &mut digest);
    }
    for relative in [
        "Cargo.lock",
        "crates/core/Cargo.toml",
        "crates/resource-build/Cargo.toml",
        "crates/resource-build/build.rs",
    ] {
        add(&root.join(relative), root, &mut digest);
    }
    let compiler = std::process::Command::new(std::env::var_os("RUSTC").unwrap())
        .arg("-vV")
        .output()
        .unwrap();
    assert!(compiler.status.success());
    digest.update(compiler.stdout);
    digest.update(std::env::var("TARGET").unwrap().as_bytes());
    println!(
        "cargo:rustc-env=GANNYU_RESOURCE_COMPILER_KEY={:x}",
        digest.finalize()
    );
}
