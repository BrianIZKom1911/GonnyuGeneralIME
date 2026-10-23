use ahash::AHashMap as HashMap;
use gannyu_input_core::{
    retrieve, retrieve_sentence_input, retrieve_with_manual_segments, segment_sentence, Dictionary,
    FuzzyMap, RetrievalLayer,
};
use std::path::PathBuf;

fn lancong_resources() -> PathBuf {
    PathBuf::from(concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../resources/regions/lancong"
    ))
}

fn lancong_dictionary() -> Dictionary {
    let directory = lancong_resources().join("dictionaries");
    let mut files = ["chars.tsv", "words.tsv", "gan_chars.tsv", "gan_words.tsv"]
        .into_iter()
        .map(|name| directory.join(name));
    let mut dictionary = Dictionary::load_tsv(files.next().unwrap()).expect("load source chars");
    for path in files {
        dictionary
            .extend_from_tsv(&path)
            .expect("load source dictionary");
    }
    dictionary
}

fn lancong_fuzzy() -> FuzzyMap {
    let root = PathBuf::from(concat!(env!("CARGO_MANIFEST_DIR"), "/../../resources"));
    FuzzyMap::load_tsv_for_region(root.join("fuzzy_scheme.tsv"), "lancong")
        .expect("load Lancong fuzzy rules")
}

#[test]
fn source_word_is_retrievable_by_its_dictionary_reading() {
    // Source: resources/regions/lancong/dictionaries/words.tsv, 车马.
    let dictionary = lancong_dictionary();
    let results = retrieve(&dictionary, &lancong_fuzzy(), &HashMap::new(), "ca1ma1");
    let candidate = results
        .iter()
        .find(|candidate| candidate.text == "车马")
        .expect("source dictionary word should be retrieved");
    assert_eq!(candidate.layer, RetrievalLayer::GannyuExact);
    assert_eq!(candidate.ipa.as_deref(), Some("tsʰa1 ma1"));
}

#[test]
fn source_word_is_retrievable_by_its_mandarin_reading() {
    // Source: resources/regions/lancong/dictionaries/words.tsv, 车马.
    let dictionary = lancong_dictionary();
    let results = retrieve(&dictionary, &lancong_fuzzy(), &HashMap::new(), "che1ma3");
    assert!(results.iter().any(|candidate| candidate.text == "车马"));
}

#[test]
fn manual_segments_accept_the_source_word_syllables() {
    // Source: resources/regions/lancong/dictionaries/words.tsv, 车马.
    let dictionary = lancong_dictionary();
    let results = retrieve_with_manual_segments(
        &dictionary,
        &lancong_fuzzy(),
        &HashMap::new(),
        "ca1 ma1",
        None,
    );
    assert!(results.iter().any(|candidate| candidate.text == "车马"));
}

#[test]
fn sentence_input_segments_a_source_dictionary_word() {
    // Source: resources/regions/lancong/dictionaries/words.tsv, 车马.
    let dictionary = lancong_dictionary();
    let segments = segment_sentence(&dictionary, &lancong_fuzzy(), &HashMap::new(), "ca1ma1");
    assert!(segments
        .iter()
        .flatten()
        .any(|candidate| candidate.text == "车马"));
}

#[test]
fn sentence_input_returns_a_source_word_candidate() {
    // Source: resources/regions/lancong/dictionaries/words.tsv, 车马.
    let dictionary = lancong_dictionary();
    let candidates = retrieve_sentence_input(
        &dictionary,
        &lancong_fuzzy(),
        &HashMap::new(),
        "ca1ma1",
        None,
    );
    assert!(candidates.iter().any(|candidate| candidate.text == "车马"));
}
