use gannyu_input_core::{FuzzyMap, SyllableScheme};
use std::{collections::BTreeMap, env, fs, hint::black_box, time::Instant};

fn main() {
    let args: Vec<String> = env::args().collect();
    assert_eq!(args.len(), 3, "fuzzy_benchmark TABLE WORKLOAD_JSON");
    let workload: Vec<(String, String)> =
        serde_json::from_str(&fs::read_to_string(&args[2]).unwrap()).unwrap();
    let mut maps = BTreeMap::new();
    for (region, _) in &workload {
        maps.entry(region.clone()).or_insert_with(|| {
            FuzzyMap::load_tsv_for_region(&args[1], region).expect("load rules")
        });
    }
    let run = || {
        let mut outputs = 0;
        for (region, input) in &workload {
            for scheme in [SyllableScheme::GonPin, SyllableScheme::GonFuzzy] {
                outputs += black_box(maps[region].normalize(black_box(input), scheme)).len();
            }
        }
        outputs
    };
    run();
    let mut samples = Vec::new();
    for _ in 0..7 {
        let start = Instant::now();
        let outputs = run();
        samples.push((start.elapsed().as_secs_f64(), outputs));
    }
    samples.sort_by(|a, b| a.0.total_cmp(&b.0));
    println!(
        "{}",
        serde_json::json!({
            "inputs": workload.len(), "calls_per_sample": workload.len() * 2,
            "median_seconds": samples[3].0, "samples": samples,
            "microseconds_per_input": samples[3].0 * 1e6 / workload.len() as f64
        })
    );
}
