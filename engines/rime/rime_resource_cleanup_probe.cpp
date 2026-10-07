#include "gannyu_rime_engine.cpp"

#include <iostream>
#include <new>
#include <stdexcept>

namespace {
int allocation_failure_countdown = 0;
}

void* operator new(std::size_t size) {
  if (allocation_failure_countdown > 0 && --allocation_failure_countdown == 0) {
    throw std::bad_alloc();
  }
  if (void* value = std::malloc(size ? size : 1)) return value;
  throw std::bad_alloc();
}

void* operator new[](std::size_t size) { return ::operator new(size); }
void operator delete(void* value) noexcept { std::free(value); }
void operator delete[](void* value) noexcept { std::free(value); }
void operator delete(void* value, std::size_t) noexcept { std::free(value); }
void operator delete[](void* value, std::size_t) noexcept { std::free(value); }

namespace {
enum class Fault { none, status, input, allocation, iterator, page_down, page_up, reacquire, commit_copy };
RimeApi api{};
Fault fault = Fault::none;
bool context_available = true;
bool status_available = true;
bool commit_available = true;
bool context_live = false;
bool status_live = false;
bool commit_live = false;
int context_calls = 0;
int contexts_acquired = 0;
int contexts_freed = 0;
int statuses_acquired = 0;
int statuses_freed = 0;
int commits_acquired = 0;
int commits_freed = 0;
int iterators_started = 0;
int iterators_ended = 0;
int page = 0;
const std::string long_text(2048, 'x');

void Check(bool condition) {
  if (!condition) {
    std::cerr << "fault=" << static_cast<int>(fault)
              << " contexts=" << contexts_acquired << '/' << contexts_freed
              << " statuses=" << statuses_acquired << '/' << statuses_freed
              << " commits=" << commits_acquired << '/' << commits_freed
              << " iterators=" << iterators_started << '/' << iterators_ended << '\n';
    throw std::runtime_error("resource cleanup check failed");
  }
}

char* CopyText(const char* text) {
  const size_t size = std::strlen(text) + 1;
  auto* copy = new char[size];
  std::memcpy(copy, text, size);
  return copy;
}

Bool GetContext(RimeSessionId, RimeContext* context) {
  ++context_calls;
  if (fault == Fault::reacquire && context_calls > 1) throw std::runtime_error("context reacquisition failed");
  if (!context_available) return False;
  Check(!context_live);
  context->composition.preedit = CopyText("gau");
  context->composition.cursor_pos = 2;
  context->menu.page_size = 9;
  context->menu.page_no = page;
  context->menu.is_last_page = page >= 2;
  context->menu.num_candidates = 1;
  context->menu.candidates = new RimeCandidate[1]{};
  context->menu.candidates[0].text = CopyText("赣");
  context->menu.candidates[0].comment = CopyText("gan4");
  context_live = true;
  ++contexts_acquired;
  return True;
}

Bool FreeContext(RimeContext* context) {
  Check(context_live);
  delete[] context->composition.preedit;
  delete[] context->menu.candidates[0].text;
  delete[] context->menu.candidates[0].comment;
  delete[] context->menu.candidates;
  RIME_STRUCT_CLEAR(*context);
  context_live = false;
  ++contexts_freed;
  return True;
}

Bool GetStatus(RimeSessionId, RimeStatus* status) {
  if (fault == Fault::status) throw std::runtime_error("status failed");
  if (!status_available) return False;
  Check(!status_live);
  status->schema_id = CopyText("gannyu_test");
  status->schema_name = CopyText("test");
  status_live = true;
  ++statuses_acquired;
  return True;
}

Bool FreeStatus(RimeStatus* status) {
  Check(status_live);
  delete[] status->schema_id;
  delete[] status->schema_name;
  RIME_STRUCT_CLEAR(*status);
  status_live = false;
  ++statuses_freed;
  return True;
}

const char* GetInput(RimeSessionId) {
  if (fault == Fault::input) throw std::runtime_error("input failed");
  if (fault == Fault::allocation) {
    allocation_failure_countdown = 2;
    return long_text.c_str();
  }
  return "gau";
}

size_t GetCaret(RimeSessionId) { return 2; }

Bool ProcessKey(RimeSessionId, int key, int) {
  if ((fault == Fault::page_down && key == kPageDown) ||
      (fault == Fault::page_up && key == kPageUp)) throw std::runtime_error("paging failed");
  page += key == kPageDown ? 1 : -1;
  return True;
}

Bool Begin(RimeSessionId, RimeCandidateListIterator* iterator, int index) {
  iterator->index = index - 1;
  ++iterators_started;
  return True;
}

Bool Next(RimeCandidateListIterator* iterator) {
  if (fault == Fault::iterator) throw std::runtime_error("iterator failed");
  if (++iterator->index >= 2) return False;
  delete[] iterator->candidate.text;
  delete[] iterator->candidate.comment;
  iterator->candidate.text = CopyText("赣");
  iterator->candidate.comment = CopyText("gan4");
  return True;
}

void End(RimeCandidateListIterator* iterator) {
  delete[] iterator->candidate.text;
  delete[] iterator->candidate.comment;
  ++iterators_ended;
}

Bool GetCommit(RimeSessionId, RimeCommit* commit) {
  if (!commit_available) return False;
  Check(!commit_live);
  commit->text = CopyText(long_text.c_str());
  commit_live = true;
  ++commits_acquired;
  if (fault == Fault::commit_copy) allocation_failure_countdown = 1;
  return True;
}

Bool FreeCommit(RimeCommit* commit) {
  Check(commit_live);
  delete[] commit->text;
  commit_live = false;
  ++commits_freed;
  return True;
}

void Reset(Fault next_fault) {
  Check(!context_live && !status_live && !commit_live);
  fault = next_fault;
  allocation_failure_countdown = 0;
  context_available = status_available = commit_available = true;
  contexts_acquired = contexts_freed = statuses_acquired = statuses_freed = 0;
  commits_acquired = commits_freed = iterators_started = iterators_ended = 0;
  context_calls = page = 0;
}

void Balanced() {
  Check(!context_live && !status_live && !commit_live);
  Check(contexts_acquired == contexts_freed && statuses_acquired == statuses_freed);
  Check(commits_acquired == commits_freed && iterators_started == iterators_ended);
}
}

extern "C" RimeApi* rime_get_api() { return &api; }

int main() {
  RIME_STRUCT_INIT(RimeApi, api);
  api.get_context = GetContext;
  api.free_context = FreeContext;
  api.get_status = GetStatus;
  api.free_status = FreeStatus;
  api.get_input = GetInput;
  api.get_caret_pos = GetCaret;
  api.process_key = ProcessKey;
  api.candidate_list_next = Next;
  api.candidate_list_end = End;
  api.get_commit = GetCommit;
  api.free_commit = FreeCommit;
  GlobalRuntime().api = &api;
  GannyuPipelineHandle handle;
  handle.session = 1;
  handle.schema_id = "gannyu_test";
  int cases = 0;
  for (size_t limit : {size_t{0}, size_t{100}}) {
    for (bool use_iterator : {false, true}) {
      for (Fault next_fault : {Fault::none, Fault::status, Fault::input, Fault::allocation,
                               Fault::iterator, Fault::page_down, Fault::page_up, Fault::reacquire}) {
        Reset(next_fault);
        handle.candidate_limit = limit;
        api.candidate_list_from_index = use_iterator ? Begin : nullptr;
        char* output = nullptr;
        const int status = gannyu_engine_snapshot(&handle, &output);
        const bool expected_failure = next_fault == Fault::status || next_fault == Fault::input ||
            next_fault == Fault::allocation || (limit > 0 &&
            ((use_iterator && next_fault == Fault::iterator) ||
             (!use_iterator && (next_fault == Fault::page_down || next_fault == Fault::page_up ||
                                next_fault == Fault::reacquire))));
        Check((status != kOk) == expected_failure);
        Check(expected_failure ? output == nullptr : output != nullptr);
        gannyu_string_destroy(output);
        Balanced();
        ++cases;
      }
    }
  }
  for (bool available : {false, true}) {
    Reset(Fault::none);
    context_available = status_available = available;
    handle.candidate_limit = 0;
    char* output = nullptr;
    Check(gannyu_engine_snapshot(&handle, &output) == kOk);
    gannyu_string_destroy(output);
    Balanced();
    ++cases;
  }
  for (Fault next_fault : {Fault::none, Fault::commit_copy}) {
    Reset(next_fault);
    const int status = AbiStatus([] {
      auto text = TakeCommit(1);
      Check(text.has_value() && *text == long_text);
      return kOk;
    });
    Check((status != kOk) == (next_fault == Fault::commit_copy));
    Balanced();
    ++cases;
  }
  Reset(Fault::none);
  commit_available = false;
  Check(!TakeCommit(1).has_value());
  Balanced();
  ++cases;
  std::cout << cases << " normal/exception resource ownership cases passed\n";
}
