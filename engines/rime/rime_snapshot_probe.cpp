#include "gannyu_rime_engine.cpp"

#include <stdexcept>
#include <iostream>
#include <thread>

namespace {
void Check(bool result) {
  if (!result) throw std::runtime_error("snapshot equivalence check failed");
}

RimeApi test_api{};
int finalize_calls = 0;
int initialize_calls = 0;
int destroyed_sessions = 0;
bool schema_available = true;
RimeSessionId next_session = 10;
RimeSessionId CreateSession() {
  Check(GlobalRuntime().initialized);
  return next_session++;
}
Bool SelectSchema(RimeSessionId, const char*) {
  Check(GlobalRuntime().initialized);
  return schema_available ? True : False;
}
void Finalize() { ++finalize_calls; }
void Initialize(RimeTraits*) { ++initialize_calls; }
Bool DestroySession(RimeSessionId) { ++destroyed_sessions; return True; }
int page = 0;
int page_size = 9;
int highlight = 0;
int key_calls = 0;
int iterator_calls = 0;
int iterator_ends = 0;
bool context_available = true;
bool iterator_available = true;
std::vector<std::string> texts;
std::vector<std::string> comments;

Bool GetContext(RimeSessionId, RimeContext* context) {
  if (!context_available) return False;
  context->composition.preedit = const_cast<char*>("赣êï");
  context->composition.cursor_pos = 3;
  context->menu.page_no = page;
  context->menu.page_size = page_size;
  context->menu.highlighted_candidate_index = highlight;
  const int start = page * page_size;
  const int count = std::max(0, std::min(page_size, static_cast<int>(texts.size()) - start));
  context->menu.num_candidates = count;
  context->menu.is_last_page = start + count >= static_cast<int>(texts.size());
  context->menu.candidates = new RimeCandidate[count]{};
  for (int index = 0; index < count; ++index) {
    context->menu.candidates[index].text = texts[start + index].data();
    context->menu.candidates[index].comment = comments[start + index].data();
  }
  return True;
}
Bool FreeContext(RimeContext* context) {
  delete[] context->menu.candidates;
  return True;
}
Bool GetStatus(RimeSessionId, RimeStatus* status) {
  status->is_ascii_mode = False;
  return True;
}
Bool FreeStatus(RimeStatus*) { return True; }
const char* GetInput(RimeSessionId) { return "êï"; }
size_t GetCaret(RimeSessionId) { return 4; }
Bool ProcessKey(RimeSessionId, int key, int) {
  ++key_calls;
  if (key == kPageDown) ++page;
  if (key == kPageUp) --page;
  return True;
}
Bool Begin(RimeSessionId, RimeCandidateListIterator* iterator, int index) {
  if (!iterator_available) return False;
  iterator->index = index - 1;
  return True;
}
Bool Next(RimeCandidateListIterator* iterator) {
  ++iterator_calls;
  ++iterator->index;
  if (iterator->index >= static_cast<int>(texts.size())) return False;
  iterator->candidate.text = texts[iterator->index].data();
  iterator->candidate.comment = comments[iterator->index].data();
  return True;
}
void End(RimeCandidateListIterator*) { ++iterator_ends; }
}

extern "C" RimeApi* rime_get_api() { return &test_api; }

int main() {
  RIME_STRUCT_INIT(RimeApi, test_api);
  test_api.get_context = GetContext;
  test_api.free_context = FreeContext;
  test_api.get_status = GetStatus;
  test_api.free_status = FreeStatus;
  test_api.get_input = GetInput;
  test_api.get_caret_pos = GetCaret;
  test_api.process_key = ProcessKey;
  test_api.candidate_list_next = Next;
  test_api.candidate_list_end = End;
  GlobalRuntime().api = &test_api;
  int cases = 0;
  for (int count : {0, 1, 9, 10, 60, 100, 125}) {
    texts.clear();
    comments.clear();
    for (int index = 0; index < count; ++index) {
      texts.push_back("赣êï\\\"" + std::to_string(index));
      comments.push_back(index % 2 ? "注释\n读音" : "");
    }
    for (int initial_page : {0, 1, 3}) {
      for (size_t limit : {0, 1, 9, 60, 100}) {
        GannyuPipelineHandle handle;
        handle.session = 1;
        handle.schema_id = "gannyu_lancong";
        handle.candidate_limit = limit;
        highlight = 2;
        page = initial_page;
        test_api.candidate_list_from_index = nullptr;
        key_calls = 0;
        const std::string expected = Snapshot(&handle, true, std::string("上屏"));
        Check(page == initial_page);
        const int original_key_calls = key_calls;
        for (bool available : {false, true}) {
          iterator_available = available;
          key_calls = iterator_calls = iterator_ends = 0;
          test_api.candidate_list_from_index = Begin;
          const std::string actual = Snapshot(&handle, true, std::string("上屏"));
          Check(actual == expected);
          Check(page == initial_page);
          if (available && limit > 0) {
            Check(key_calls == 0);
            Check(iterator_ends == 1);
            Check(iterator_calls <= static_cast<int>(limit));
            if (count == 125 && initial_page == 0 && limit == 100) {
              std::cout << "100-candidate snapshot pagination keys: " << original_key_calls << " -> " << key_calls << '\n';
            }
          }
          ++cases;
        }
      }
    }
  }
  const int full_api_size = test_api.data_size;
  test_api.data_size = static_cast<int>(offsetof(RimeApi, candidate_list_from_index)) - sizeof(test_api.data_size);
  GannyuPipelineHandle legacy;
  legacy.session = 1;
  legacy.candidate_limit = 100;
  page = 0;
  key_calls = iterator_ends = 0;
  Snapshot(&legacy, false, std::nullopt);
  Check(key_calls > 0);
  Check(iterator_ends == 0);
  Check(page == 0);
  test_api.data_size = full_api_size;
  page_size = 0;
  key_calls = iterator_ends = 0;
  Snapshot(&legacy, false, std::nullopt);
  Check(key_calls == 0);
  Check(iterator_ends == 0);
  context_available = false;
  GannyuPipelineHandle handle;
  handle.candidate_limit = 100;
  Check(Snapshot(&handle, false, std::nullopt).find("\"candidates\":[]") != std::string::npos);
  std::cout << cases << " snapshot equivalence cases passed\n";
  test_api.finalize = Finalize;
  test_api.initialize = Initialize;
  test_api.destroy_session = DestroySession;
  auto& runtime = GlobalRuntime();
  runtime.setup = true;
  runtime.shared_data_dir = "shared";
  runtime.prebuilt_data_dir = "prebuilt";
  runtime.user_data_dir = "user";
  for (int cycle = 0; cycle < 100; ++cycle) {
    Check(EnsureRuntimeLocked("shared", "prebuilt", "user"));
    auto* first = new GannyuPipelineHandle;
    auto* second = new GannyuPipelineHandle;
    first->session = 1;
    second->session = 2;
    runtime.handles = {first, second};
    Check(gannyu_runtime_finalize() == kInvalidArgument);
    gannyu_pipeline_destroy(first);
    Check(runtime.initialized && finalize_calls == cycle);
    gannyu_pipeline_destroy(second);
    Check(!runtime.initialized && finalize_calls == cycle + 1);
    Check(gannyu_runtime_finalize() == kOk);
    Check(finalize_calls == cycle + 1);
  }
  Check(initialize_calls == 100 && destroyed_sessions == 200);
  std::cout << "100 last-handle shutdown/reinitialization cycles passed\n";
  test_api.create_session = CreateSession;
  test_api.select_schema = SelectSchema;
  std::vector<std::thread> workers;
  for (int worker = 0; worker < 4; ++worker) {
    workers.emplace_back([] {
      for (int iteration = 0; iteration < 100; ++iteration) {
        GannyuPipelineHandle* created = nullptr;
        Check(Create("shared", "prebuilt", "lancong", "user", &created) == kOk);
        Check(created != nullptr);
        gannyu_pipeline_destroy(created);
      }
    });
  }
  for (auto& worker : workers) worker.join();
  Check(runtime.handles.empty() && !runtime.initialized);
  Check(initialize_calls == finalize_calls && destroyed_sessions == 600);
  std::cout << "400 concurrent create/destroy operations passed\n";
  schema_available = false;
  GannyuPipelineHandle* failed = nullptr;
  Check(Create("shared", "prebuilt", "missing", "user", &failed) == kLoadFailure);
  Check(failed == nullptr && runtime.handles.empty() && !runtime.initialized);
  Check(initialize_calls == finalize_calls && destroyed_sessions == 601);
  std::cout << "failed creation shuts down unowned runtime\n";
}
