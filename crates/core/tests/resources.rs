use gannyu_input_core::{
    default_region_entry, list_region_entries, load_region_from_manifest, ResourceError,
};

const MANIFEST_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/../../resources/manifest.toml");

#[test]
fn default_region_is_registered() {
    let region = default_region_entry(MANIFEST_PATH).expect("default region should load");
    assert_eq!(region.id, "lancong");
}

#[test]
fn region_entries_can_be_listed() {
    let regions = list_region_entries(MANIFEST_PATH).expect("regions should load");
    assert!(!regions.is_empty());
    assert!(regions.iter().any(|region| region.id == "lancong"));
}

#[test]
fn region_resource_files_exist() {
    let regions = list_region_entries(MANIFEST_PATH).expect("regions should load");
    for region in regions {
        load_region_from_manifest(MANIFEST_PATH, &region.id)
            .unwrap_or_else(|error| panic!("{} resource should load: {error}", region.id));
    }
}

#[test]
fn fungcen_validation_resources_load() {
    let resource =
        load_region_from_manifest(MANIFEST_PATH, "fungcen").expect("fungcen resource should load");
    assert_eq!(resource.config.region.name_zh, "丰城");
}

#[test]
fn xinyu_starred_tone_classes_load() {
    let resource =
        load_region_from_manifest(MANIFEST_PATH, "xinyu").expect("xinyu resource should load");
    assert_eq!(resource.config.tone_classes["1*"].name, "阴平乙");
    assert_eq!(resource.config.tone_classes["5*"].name, "入声乙");
    assert_eq!(resource.config.tone_classes["2"].name, "阳平");
    assert_eq!(resource.config.tone_classes["3"].name, "上声");
    assert_eq!(resource.config.tone_classes["4"].name, "去声");
}

#[test]
fn unknown_region_returns_error() {
    let error = load_region_from_manifest(MANIFEST_PATH, "unknown").unwrap_err();
    assert!(matches!(error, ResourceError::UnknownRegion(region) if region == "unknown"));
}

#[test]
fn manifest_registers_active_regions() {
    let regions = list_region_entries(MANIFEST_PATH).expect("regions should load");
    assert!(!regions.is_empty());
    assert!(regions.iter().all(|region| region.status == "active"));
    assert!(regions.iter().any(|region| region.id == "lancong"));
}
