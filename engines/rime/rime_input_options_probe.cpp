#include "gannyu_input.h"

#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

int main(int argc, char** argv) {
  if (argc != 4) return 2;
  GannyuEngineConfig config = GANNYU_ENGINE_CONFIG_INIT;
  config.region_id = "lancong";
  config.shared_data_dir = argv[1];
  config.prebuilt_data_dir = argv[2];
  config.user_data_dir = argv[3];
  GannyuPipelineHandle* handle = nullptr;
  GannyuPipelineHandle* second = nullptr;
  auto check = [](bool result, const char* message) {
    if (!result) throw std::runtime_error(message);
  };
  auto snapshot = [&](const char* event = nullptr) {
    char* json = nullptr;
    const int status = event ? gannyu_engine_process_key(handle, event, &json)
                             : gannyu_engine_snapshot(handle, &json);
    check(status == 0 && json != nullptr, "snapshot failed");
    std::string result(json);
    gannyu_string_destroy(json);
    return result;
  };
  auto input = [&](const char* text) {
    char* cleared = nullptr;
    check(gannyu_engine_clear_composition(handle, &cleared) == 0, "clear failed");
    gannyu_string_destroy(cleared);
    const std::string event = std::string("{\"type\":\"text\",\"text\":\"") + text + "\"}";
    return snapshot(event.c_str());
  };
  try {
    check(gannyu_engine_create(&config, &handle) == 0, "create failed");
    check(gannyu_engine_create(&config, &second) == 0, "second session failed");
    char* second_snapshot = nullptr;
    check(gannyu_engine_process_key(second, "{\"type\":\"text\",\"text\":\"chema\"}", &second_snapshot) == 0, "second session input failed");
    gannyu_string_destroy(second_snapshot);
    check(gannyu_engine_set_candidate_limit(handle, 100) == 0, "candidate limit failed");
    auto result = snapshot("{\"type\":\"text\",\"text\":\"chema\"}");
    check(result.find("\"text\":\"车马\"") != std::string::npos, "source Mandarin lookup missing");
    check(gannyu_engine_set_input_options(handle, 1, 1, 0, 1, 1, 0) == 0, "fuzzy toggle failed");
    result = snapshot();
    check(result.find("\"rawInput\":\"chema\"") != std::string::npos, "hot toggle lost input");
    check(result.find("\"text\":\"车马\"") == std::string::npos, "disabled Mandarin lookup leaked");
    second_snapshot = nullptr;
    check(gannyu_engine_snapshot(second, &second_snapshot) == 0 && second_snapshot != nullptr, "second snapshot failed");
    const std::string independent(second_snapshot);
    gannyu_string_destroy(second_snapshot);
    check(independent.find("\"text\":\"车马\"") != std::string::npos, "options leaked into another live session");
    gannyu_pipeline_destroy(second);
    second = nullptr;
    check(gannyu_engine_set_input_options(handle, 1, 1, 1, 1, 1, 0) == 0, "restore failed");
    check(snapshot().find("\"text\":\"车马\"") != std::string::npos, "restored lookup missing");
    check(gannyu_engine_set_input_options(handle, 0, 1, 1, 1, 1, 0) == 0, "annotation toggle failed");
    result = snapshot();
    check(result.find("\"rawInput\":\"chema\"") != std::string::npos, "annotation toggle lost input");
    check(result.find("\"annotation\"") == std::string::npos, "hidden annotations leaked");
    check(result.find("\"text\":\"车马\"") != std::string::npos, "Gan word lost after annotation toggle");
    check(gannyu_engine_set_input_options(handle, 1, 1, 1, 1, 1, 0) == 0, "final restore failed");
    check(snapshot().find("\"annotation\"") != std::string::npos, "restored annotations missing");
    result = input("yangniu");
    check(result.find("\"text\":\"放牛\"") != std::string::npos, "source relation missing");
    check(gannyu_engine_set_input_options(handle, 1, 0, 1, 1, 1, 0) == 0, "relation toggle failed");
    result = snapshot();
    check(result.find("\"text\":\"䁐牛\"") != std::string::npos, "source Gan word missing");
    check(result.find("放牛") == std::string::npos, "disabled Mandarin word or annotation leaked");
    check(input("fangniu").find("\"text\":\"放牛\"") == std::string::npos, "direct Mandarin word lookup leaked");
    check(gannyu_engine_set_input_options(handle, 1, 1, 0, 1, 1, 1) == 0, "new mode failed");
    result = input("yi");
    check(result.find("\"text\":\"义\"") != std::string::npos, "source new reading missing");
    check(result.find("[老]") == std::string::npos, "old annotation leaked into new mode");
    check(input("ni").find("\"text\":\"义\"") == std::string::npos, "old lookup leaked into new mode");
    check(gannyu_engine_set_input_options(handle, 1, 1, 0, 1, 1, 2) == 0, "old mode failed");
    check(snapshot().find("\"text\":\"义\"") != std::string::npos, "source old reading missing after hot toggle");
    check(input("yi").find("\"text\":\"义\"") == std::string::npos, "new lookup leaked into old mode");
    for (const char* suffix : {"", "_both_norel", "_new_rel", "_new_norel", "_old_rel", "_old_norel"}) {
      const auto path = std::filesystem::path(argv[3]) / (std::string("gannyu_lancong") + suffix + ".userdb");
      std::filesystem::create_directories(path);
      std::ofstream(path / "input-options-cleanup-marker").put('1');
    }
    char* reset = nullptr;
    check(gannyu_engine_reset_user_data(handle, GANNYU_USER_DATA_ALL, &reset) == 0, "reset failed");
    gannyu_string_destroy(reset);
    for (const char* suffix : {"", "_both_norel", "_new_rel", "_new_norel", "_old_rel", "_old_norel"}) {
      const auto marker = std::filesystem::path(argv[3]) / (std::string("gannyu_lancong") + suffix + ".userdb") / "input-options-cleanup-marker";
      check(!std::filesystem::exists(marker), "variant user data survived reset");
    }
    check(input("ni").find("\"text\":\"义\"") != std::string::npos, "reset lost reading mode");
    gannyu_pipeline_destroy(handle);
    std::cout << "hot input options preserve input and update matching and annotations\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    if (handle) gannyu_pipeline_destroy(handle);
    if (second) gannyu_pipeline_destroy(second);
    return 1;
  }
}
