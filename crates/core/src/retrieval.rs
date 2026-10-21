use crate::association_cache::AssociationCache;
use crate::candidate::CandidateView;
use crate::dictionary::{
    distinct_mandarin_words, normalize_pinyin, paired_alternates_for_stored, pinyin_segments,
    strip_tone, Dictionary, DictionaryEntry, PairKind, PairedReading,
};
use crate::syllable::{FuzzyMap, SyllableScheme};
use ahash::{AHashMap as HashMap, AHashSet as HashSet};
use serde::Serialize;
use std::cell::RefCell;
use std::rc::Rc;

type RetrieveCache = HashMap<(u64, String, bool, usize), Vec<RankedCandidate>>;

thread_local! {
    /// Per-thread cache for gan_annotation_for_mandarin_entry results,
    /// cleared at the start of each retrieve_inner call.
    static ANNOTATION_CACHE: RefCell<HashMap<String, Option<String>>> = RefCell::new(HashMap::new());
    /// Per-thread cache for retrieve_inner_limited results, keyed by
    /// (dictionary_id, normalized_input, skip_step7, max_candidates).  Capped at 512
    /// entries to bound memory.
    static INNER_RETRIEVE_CACHE: RefCell<RetrieveCache> = RefCell::new(HashMap::new());
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum RetrievalLayer {
    /// Exact hit via dialect (Gan) pinyin — including tone-stripped and
    /// checked-tone variants.
    GannyuExact,
    /// Exact hit via Mandarin pinyin — including tone-stripped variants.
    MandarinExact,
    /// Fuzzy hit via onset/nucleus/coda/tone substitution rules.
    Fuzzy,
    /// Synonym cross-reference.
    Synonym,
}

impl RetrievalLayer {
    pub fn base_weight(self) -> f64 {
        match self {
            RetrievalLayer::GannyuExact => 5.0,
            RetrievalLayer::MandarinExact => 4.5,
            RetrievalLayer::Fuzzy => 4.0,
            RetrievalLayer::Synonym => 4.0,
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct RankedCandidate {
    pub text: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub annotation: Option<String>,
    pub ipa: Option<String>,
    pub layer: RetrievalLayer,
    pub mandarin_only: bool,
    pub weight: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reading: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mandarin_reading: Option<String>,
    #[serde(skip_serializing_if = "is_zero")]
    pub consumed_bytes: usize,
}

impl CandidateView for RankedCandidate {
    fn text(&self) -> &str {
        &self.text
    }

    fn reading(&self) -> Option<&str> {
        self.reading.as_deref()
    }
}

fn is_zero(n: &usize) -> bool {
    *n == 0
}

include!("retrieval/candidates.rs");
include!("retrieval/segmentation.rs");
include!("retrieval/query.rs");
