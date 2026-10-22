use gannyu_input_core::{load_region_from_manifest, InputOptions, InputPipeline, ReadingMode};
use std::path::Path;

#[test]
fn hot_options_filter_before_lookup_and_restore_original_candidates() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../resources");
    let region = load_region_from_manifest(root.join("manifest.toml"), "lancong").unwrap();
    let user = tempfile::tempdir().unwrap();
    let mut pipeline = InputPipeline::load_with_user_data_dir(&region, Some(user.path())).unwrap();
    let original = pipeline.retrieve("ca1ma1");
    assert!(original.iter().any(|candidate| candidate.text == "车马"));
    assert!(pipeline
        .retrieve("che1ma3")
        .iter()
        .any(|candidate| candidate.text == "车马"));
    let mut options = InputOptions {
        fuzzy: false,
        relations: false,
        ..InputOptions::default()
    };
    pipeline.set_input_options(options);
    assert!(pipeline
        .retrieve("ca1ma1")
        .iter()
        .any(|candidate| candidate.text == "车马"));
    assert!(!pipeline
        .retrieve("che1ma3")
        .iter()
        .any(|candidate| candidate.text == "车马"));
    assert!(pipeline
        .dictionary()
        .entries()
        .iter()
        .all(|entry| entry.category.as_ref() != "官"));
    assert!(!pipeline
        .retrieve("fang4niu2")
        .iter()
        .any(|candidate| candidate.text == "放牛"));
    assert!(pipeline.fuzzy_map().entries.iter().all(|entry| matches!(
        (entry.gon_fuzzy.as_str(), entry.gon_pin.as_str()),
        ("i", "ï") | ("e", "ê") | ("ee", "ê") | ("ir", "e")
    )));
    assert!(pipeline.fuzzy_map().entries.len() >= 3);
    assert!(pipeline
        .fuzzy_map()
        .entries
        .iter()
        .any(|entry| entry.gon_fuzzy == "ir" && entry.gon_pin == "e"));
    options.fuzzy = true;
    pipeline.set_input_options(options);
    assert!(pipeline
        .retrieve("che1ma3")
        .iter()
        .any(|candidate| candidate.text == "车马"));
    options.annotations = false;
    pipeline.set_input_options(options);
    assert!(pipeline
        .retrieve("ca1ma1")
        .iter()
        .all(|candidate| candidate.annotation.is_none()));
    options.reading_mode = ReadingMode::New;
    pipeline.set_input_options(options);
    assert!(pipeline
        .dictionary()
        .entries()
        .iter()
        .all(|entry| !entry.new_old.starts_with('老')));
    assert!(pipeline
        .dictionary()
        .by_dialect_pinyin("yi5")
        .iter()
        .any(|entry| entry.headword.as_ref() == "义"));
    assert!(!pipeline
        .dictionary()
        .by_dialect_pinyin("ni5")
        .iter()
        .any(|entry| entry.headword.as_ref() == "义"));
    options.reading_mode = ReadingMode::Old;
    pipeline.set_input_options(options);
    assert!(pipeline
        .dictionary()
        .entries()
        .iter()
        .all(|entry| !entry.new_old.starts_with('新')));
    pipeline.set_input_options(InputOptions::default());
    assert_eq!(
        serde_json::to_value(pipeline.retrieve("ca1ma1")).unwrap(),
        serde_json::to_value(original).unwrap()
    );
}
