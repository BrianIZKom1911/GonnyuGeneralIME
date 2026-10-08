#include "gannyu_input.h"
#include <rime_api.h>

#include <mach/mach.h>

#include <cstdint>
#include <cstdio>

namespace {

bool Footprint(uint64_t* bytes) {
  task_vm_info_data_t info{};
  mach_msg_type_number_t count = TASK_VM_INFO_COUNT;
  if (task_info(mach_task_self(), TASK_VM_INFO,
                reinterpret_cast<task_info_t>(&info), &count) != KERN_SUCCESS) {
    return false;
  }
  *bytes = info.phys_footprint;
  return true;
}

}

int main(int argc, char** argv) {
  if (argc != 5) {
    std::fprintf(stderr, "usage: %s SHARED_DATA_DIR PREBUILT_DATA_DIR USER_DATA_DIR REGION\n", argv[0]);
    return 2;
  }
  RimeApi* api = rime_get_api();
  if (api == nullptr || api->find_module == nullptr || api->find_module("lua") == nullptr) {
    std::fprintf(stderr, "memory probe requires the linked Lua plugin\n");
    return 6;
  }
  uint64_t baseline = 0;
  uint64_t latest = 0;
  for (int round = 1; round <= 25; ++round) {
    GannyuEngineConfig config = GANNYU_ENGINE_CONFIG_INIT;
    config.shared_data_dir = argv[1];
    config.prebuilt_data_dir = argv[2];
    config.user_data_dir = argv[3];
    config.region_id = argv[4];
    GannyuPipelineHandle* handle = nullptr;
    if (gannyu_engine_create(&config, &handle) != 0 || handle == nullptr) {
      char* error = nullptr;
      gannyu_last_error(&error);
      std::fprintf(stderr, "engine creation failed: %s\n", error ? error : "unknown");
      gannyu_string_destroy(error);
      gannyu_pipeline_destroy(handle);
      return 3;
    }
    char* snapshot = nullptr;
    const bool snapshot_ok = gannyu_engine_snapshot(handle, &snapshot) == 0 && snapshot != nullptr;
    gannyu_string_destroy(snapshot);
    gannyu_pipeline_destroy(handle);
    if (!snapshot_ok || !Footprint(&latest)) return 4;
    if (round == 5) baseline = latest;
    std::printf("round=%d closedFootprintMiB=%.3f\n", round, latest / 1048576.0);
    std::fflush(stdout);
    if (round > 5 && latest > baseline + 8 * 1024 * 1024) {
      std::fprintf(stderr, "closed-engine footprint grew by more than 8 MiB after warmup\n");
      return 5;
    }
  }
  return 0;
}
