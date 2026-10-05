package.path = os.getenv("GANNYU_RIME_LUA_DIR") .. "/?.lua;" .. package.path
local filters = {
  require("gannyu_annotation_filter"),
  require("gannyu_single_char_filter"),
  (require("gannyu_relation_filter")),
}
local loads = {}
local weak = setmetatable({}, {__mode = "v"})
for _, name in ipairs({"test_a", "test_b"}) do
  package.preload[name .. "_data"] = function()
    loads[name] = (loads[name] or 0) + 1
    local data = {annotations = {}, readings = {}, before = {}, after = {}}
    weak[name] = data
    return data
  end
end
local function open(name)
  local envs = {}
  for i, filter in ipairs(filters) do
    envs[i] = {engine = {schema = {schema_id = name}}}
    filter.init(envs[i])
  end
  assert(envs[1].data == envs[2].data and envs[2].data == envs[3].data)
  return envs
end
local function close(envs)
  for i, filter in ipairs(filters) do
    filter.fini(envs[i])
    filter.fini(envs[i])
    assert(envs[i].data == nil)
  end
end
for iteration = 1, 100 do
  local first = open("test_a")
  local second = open("test_a")
  local other = open("test_b")
  assert(loads.test_a == iteration and loads.test_b == iteration)
  close(first)
  assert(package.loaded.test_a_data == second[1].data)
  assert(weak.test_a ~= nil)
  close(second)
  assert(package.loaded.test_a_data == nil and weak.test_a == nil)
  assert(package.loaded.test_b_data == other[1].data)
  close(other)
  assert(package.loaded.test_b_data == nil and weak.test_b == nil)
end
print("100 shared-session lifecycle cycles passed")
