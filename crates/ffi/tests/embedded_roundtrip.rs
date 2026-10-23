use gannyu_input_ffi::{
    gannyu_engine_candidates, gannyu_engine_create, gannyu_engine_process_key,
    gannyu_engine_select_candidate, gannyu_engine_snapshot, gannyu_ffi_status_ok,
    gannyu_pipeline_compose, gannyu_pipeline_create, gannyu_pipeline_destroy,
    gannyu_pipeline_retrieve, gannyu_string_destroy, GannyuEngineConfig,
};
use serde_json::Value;
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

fn cstr(ptr: *mut c_char) -> String {
    unsafe { CStr::from_ptr(ptr).to_string_lossy().into_owned() }
}

#[test]
fn candidate_ranges_preserve_composition_and_snapshot() {
    let mut handle = std::ptr::null_mut();
    assert_eq!(
        unsafe { gannyu_pipeline_create(std::ptr::null(), std::ptr::null(), &mut handle) },
        gannyu_ffi_status_ok()
    );
    let event = CString::new(r#"{"type":"text","text":"lancong"}"#).unwrap();
    let mut output = std::ptr::null_mut();
    assert_eq!(
        unsafe { gannyu_engine_process_key(handle, event.as_ptr(), &mut output) },
        gannyu_ffi_status_ok()
    );
    unsafe { gannyu_string_destroy(output) };
    let snapshot = || {
        let mut json = std::ptr::null_mut();
        assert_eq!(unsafe { gannyu_engine_snapshot(handle, &mut json) }, 0);
        let value: Value = serde_json::from_str(&cstr(json)).unwrap();
        unsafe { gannyu_string_destroy(json) };
        value
    };
    let before = snapshot();
    assert!(!before["candidates"].as_array().unwrap().is_empty());
    for offset in [0, 1, 9, 100] {
        output = std::ptr::null_mut();
        assert_eq!(
            unsafe { gannyu_engine_candidates(handle, offset, 7, &mut output) },
            0
        );
        let batch: Value = serde_json::from_str(&cstr(output)).unwrap();
        unsafe { gannyu_string_destroy(output) };
        assert_eq!(batch["rawInput"], before["rawInput"]);
        assert_eq!(batch["schemaId"], before["schemaId"]);
        let candidates = batch["candidates"].as_array().unwrap();
        assert!(candidates.len() <= 7);
        for (index, candidate) in candidates.iter().enumerate() {
            assert_eq!(candidate["globalIndex"], offset + index);
            if offset + index < before["candidates"].as_array().unwrap().len() {
                assert_eq!(
                    candidate["text"],
                    before["candidates"][offset + index]["text"]
                );
            }
        }
        assert_eq!(snapshot(), before);
    }
    for (offset, limit) in [(0, 0), (0, 101), (usize::MAX, 100)] {
        assert_ne!(
            unsafe { gannyu_engine_candidates(handle, offset, limit, &mut output) },
            0
        );
        assert!(output.is_null());
    }
    unsafe { gannyu_pipeline_destroy(handle) };
}

#[test]
fn common_engine_config_owns_one_destroyable_handle() {
    let region = CString::new("fenni").unwrap();
    let config = GannyuEngineConfig {
        struct_size: std::mem::size_of::<GannyuEngineConfig>(),
        region_id: region.as_ptr(),
        shared_data_dir: std::ptr::null(),
        prebuilt_data_dir: std::ptr::null(),
        user_data_dir: std::ptr::null(),
    };
    let mut handle: *mut gannyu_input_ffi::GannyuPipelineHandle = std::ptr::null_mut();
    let status = unsafe { gannyu_engine_create(&config, &mut handle) };
    assert_eq!(status, gannyu_ffi_status_ok());
    assert!(!handle.is_null());
    unsafe { gannyu_pipeline_destroy(handle) };
}

#[test]
fn embedded_resources_load_and_compose() {
    let mut handle: *mut gannyu_input_ffi::GannyuPipelineHandle = std::ptr::null_mut();
    let status = unsafe { gannyu_pipeline_create(std::ptr::null(), std::ptr::null(), &mut handle) };
    assert_eq!(status, gannyu_ffi_status_ok(), "pipeline_create failed");

    let input = CString::new("lancong").unwrap();
    let mut out: *mut c_char = std::ptr::null_mut();
    let status = unsafe { gannyu_pipeline_compose(handle, input.as_ptr(), &mut out) };
    assert_eq!(status, gannyu_ffi_status_ok(), "compose failed");
    let json = cstr(out);
    unsafe { gannyu_string_destroy(out) };
    assert!(!json.is_empty(), "compose returned empty JSON");

    let mut out2: *mut c_char = std::ptr::null_mut();
    let status = unsafe { gannyu_pipeline_retrieve(handle, input.as_ptr(), &mut out2) };
    assert_eq!(status, gannyu_ffi_status_ok(), "retrieve failed");
    let json2 = cstr(out2);
    unsafe { gannyu_string_destroy(out2) };
    assert!(!json2.is_empty(), "retrieve returned empty JSON");

    let handle_addr = handle as usize;
    let workers: Vec<_> = (0..4)
        .map(|_| {
            std::thread::spawn(move || {
                let input = CString::new("lancong").unwrap();
                let mut out: *mut c_char = std::ptr::null_mut();
                let status = unsafe {
                    gannyu_pipeline_retrieve(
                        handle_addr as *mut gannyu_input_ffi::GannyuPipelineHandle,
                        input.as_ptr(),
                        &mut out,
                    )
                };
                assert_eq!(status, gannyu_ffi_status_ok());
                assert!(!out.is_null());
                unsafe { gannyu_string_destroy(out) };
            })
        })
        .collect();
    for worker in workers {
        worker.join().unwrap();
    }

    unsafe { gannyu_pipeline_destroy(handle) };
}

#[test]
fn stateful_engine_snapshot_tracks_composition_and_commit() {
    let mut handle: *mut gannyu_input_ffi::GannyuPipelineHandle = std::ptr::null_mut();
    let status = unsafe { gannyu_pipeline_create(std::ptr::null(), std::ptr::null(), &mut handle) };
    assert_eq!(status, gannyu_ffi_status_ok(), "pipeline_create failed");

    let event = CString::new(r#"{"type":"text","text":"lancongwa"}"#).unwrap();
    let mut out: *mut c_char = std::ptr::null_mut();
    let status = unsafe { gannyu_engine_process_key(handle, event.as_ptr(), &mut out) };
    assert_eq!(status, gannyu_ffi_status_ok(), "process_key failed");
    let snapshot: Value = serde_json::from_str(&cstr(out)).unwrap();
    unsafe { gannyu_string_destroy(out) };
    assert_eq!(snapshot["rawInput"], "lancongwa");
    assert!(
        snapshot["candidates"]
            .as_array()
            .is_some_and(|candidates| !candidates.is_empty()),
        "snapshot must include candidates"
    );

    let first_index = snapshot["candidates"][0]["globalIndex"].as_u64().unwrap();
    let mut out2: *mut c_char = std::ptr::null_mut();
    let status = unsafe { gannyu_engine_select_candidate(handle, first_index as usize, &mut out2) };
    assert_eq!(status, gannyu_ffi_status_ok(), "select_candidate failed");
    let committed: Value = serde_json::from_str(&cstr(out2)).unwrap();
    unsafe { gannyu_string_destroy(out2) };
    assert!(
        committed["commitText"]
            .as_str()
            .is_some_and(|text| !text.is_empty()),
        "candidate selection must commit text"
    );

    unsafe { gannyu_pipeline_destroy(handle) };
}

#[test]
fn punctuation_event_commits_current_candidate_then_symbol() {
    let mut handle: *mut gannyu_input_ffi::GannyuPipelineHandle = std::ptr::null_mut();
    let status = unsafe { gannyu_pipeline_create(std::ptr::null(), std::ptr::null(), &mut handle) };
    assert_eq!(status, gannyu_ffi_status_ok(), "pipeline_create failed");

    let input = CString::new(r#"{"type":"text","text":"lancong"}"#).unwrap();
    let mut ignored: *mut c_char = std::ptr::null_mut();
    let status = unsafe { gannyu_engine_process_key(handle, input.as_ptr(), &mut ignored) };
    assert_eq!(status, gannyu_ffi_status_ok());
    unsafe { gannyu_string_destroy(ignored) };

    let punct = CString::new(r#"{"type":"text","text":"，"}"#).unwrap();
    let mut out: *mut c_char = std::ptr::null_mut();
    let status = unsafe { gannyu_engine_process_key(handle, punct.as_ptr(), &mut out) };
    assert_eq!(
        status,
        gannyu_ffi_status_ok(),
        "punctuation process_key failed"
    );
    let snapshot: Value = serde_json::from_str(&cstr(out)).unwrap();
    unsafe { gannyu_string_destroy(out) };
    let commit = snapshot["commitText"].as_str().unwrap_or_default();
    assert!(
        commit.ends_with('，'),
        "commitText must include trailing punctuation"
    );
    assert_eq!(snapshot["rawInput"], "");

    unsafe { gannyu_pipeline_destroy(handle) };
}

#[test]
fn engine_snapshot_api_returns_current_state() {
    let mut handle: *mut gannyu_input_ffi::GannyuPipelineHandle = std::ptr::null_mut();
    let status = unsafe { gannyu_pipeline_create(std::ptr::null(), std::ptr::null(), &mut handle) };
    assert_eq!(status, gannyu_ffi_status_ok(), "pipeline_create failed");

    let mut out: *mut c_char = std::ptr::null_mut();
    let status = unsafe { gannyu_engine_snapshot(handle, &mut out) };
    assert_eq!(status, gannyu_ffi_status_ok(), "engine_snapshot failed");
    let snapshot: Value = serde_json::from_str(&cstr(out)).unwrap();
    unsafe { gannyu_string_destroy(out) };
    assert_eq!(snapshot["rawInput"], "");
    assert_eq!(snapshot["pageNumber"], 0);

    unsafe { gannyu_pipeline_destroy(handle) };
}

#[test]
fn engine_cursor_events_edit_inside_composition() {
    let mut handle: *mut gannyu_input_ffi::GannyuPipelineHandle = std::ptr::null_mut();
    let status = unsafe { gannyu_pipeline_create(std::ptr::null(), std::ptr::null(), &mut handle) };
    assert_eq!(status, gannyu_ffi_status_ok(), "pipeline_create failed");

    let process = |event: &str| {
        let event = CString::new(event).unwrap();
        let mut out: *mut c_char = std::ptr::null_mut();
        let status = unsafe { gannyu_engine_process_key(handle, event.as_ptr(), &mut out) };
        assert_eq!(
            status,
            gannyu_ffi_status_ok(),
            "process_key failed for {event:?}"
        );
        let snapshot: Value = serde_json::from_str(&cstr(out)).unwrap();
        unsafe { gannyu_string_destroy(out) };
        snapshot
    };

    process(r#"{"type":"text","text":"lan"}"#);
    process(r#"{"type":"move-left"}"#);
    let inserted = process(r#"{"type":"text","text":"c"}"#);
    assert_eq!(inserted["rawInput"], "lacn");
    assert_eq!(inserted["caret"], 4);
    let deleted = process(r#"{"type":"delete-forward"}"#);
    assert_eq!(deleted["rawInput"], "lac");
    let deleted = process(r#"{"type":"backspace"}"#);
    assert_eq!(deleted["rawInput"], "la");

    unsafe { gannyu_pipeline_destroy(handle) };
}
