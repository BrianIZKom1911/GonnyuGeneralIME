package.path = os.getenv("GANNYU_RIME_LUA_DIR") .. "/?.lua;" .. package.path
local options = require("gannyu_input_options")
local function environment(names, values)
  return {engine = {
    schema = {schema_id = "gannyu_test", config = {
      get_list = function(_, key) assert(key == "switches"); return {size = #names} end,
      get_string = function(_, key)
        local index = assert(key:match("switches/@(%d+)/name"))
        return names[tonumber(index) + 1]
      end,
    }},
    context = {get_option = function(_, key) return values[key] == true end},
  }}
end
for _, names in ipairs({{"ascii_mode", "gannyu_no_annotations"}, {"gannyu_no_fuzzy", "ascii_mode", "gannyu_no_annotations"}}) do
  local env = environment(names, {gannyu_no_fuzzy = true, gannyu_old = true})
  local dictionary, suffix = options.names(env)
  assert(dictionary == "gannyu_test_old_rel")
  assert(suffix == "_old_rel_special_gan")
  env.engine.context = {get_option = function(_, key) return key == "gannyu_no_annotations" end}
  dictionary, suffix = options.names(env)
  assert(dictionary == "gannyu_test_both_norel" and suffix == "_both_norel")
  assert(not options.enabled(env, "annotations"))
end
local legacy = environment({"ascii_mode"}, {gannyu_no_annotations = true, gannyu_old = true})
local dictionary, suffix = options.names(legacy)
assert(dictionary == "gannyu_test" and suffix == "")
assert(options.enabled(legacy, "annotations"))
print("switch declarations control hot options without an additional marker")
