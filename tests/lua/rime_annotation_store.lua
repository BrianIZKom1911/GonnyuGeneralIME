local resources, reference, name = arg[1], arg[2], arg[3]
package.path = resources .. "/lua/?.lua;" .. package.path
local expected = assert(loadfile(reference))()
collectgarbage("collect")
local baseline = collectgarbage("count")
local actual = require(name .. "_data")
collectgarbage("collect")
local retained = collectgarbage("count") - baseline

local function equal(left, right)
  if type(left) ~= type(right) then
    return false
  end
  if type(left) ~= "table" then
    return left == right
  end
  for key, value in pairs(left) do
    if not equal(value, right[key]) then
      return false
    end
  end
  for key in pairs(right) do
    if left[key] == nil then
      return false
    end
  end
  return true
end

assert(equal(expected, actual), "metadata differs from canonical data")
local count = 0
for word, annotation in pairs(expected.annotations) do
  assert(actual.annotations[word] == annotation, "annotation mismatch: " .. word)
  count = count + 1
end
assert(actual.annotations[false] == nil and actual.annotations[1] == nil)
assert(actual.annotations["__gonnyu_missing_annotation__"] == nil)

Candidate = function(kind, first, last, text, comment)
  return {type = kind, start = first, _end = last, text = text, comment = comment}
end
yield = coroutine.yield
local filters = {
  require("gannyu_annotation_filter"),
  require("gannyu_single_char_filter"),
  (require("gannyu_relation_filter")),
}
local function pipeline(data)
  local words = {"蔬菜", "青", "我们嗰", "䁐牛", "银行卡", "未知词"}
  local candidates = {}
  for index, word in ipairs(words) do
    candidates[index] = {
      text = word, type = "phrase", start = 0, _end = index == 2 and 1 or 6,
      quality = 10 - index, preedit = "example", comment = "Gngo3 Gmen4",
    }
  end
  for _, filter in ipairs(filters) do
    local input = candidates
    candidates = {}
    local stream = {
      iter = function()
        local index = 0
        return function()
          index = index + 1
          return input[index]
        end
      end,
    }
    local worker = coroutine.create(function() filter.func(stream, {data = data}) end)
    while coroutine.status(worker) ~= "dead" do
      local ok, candidate = coroutine.resume(worker)
      assert(ok, candidate)
      if candidate then
        candidates[#candidates + 1] = candidate
      end
    end
  end
  return candidates
end
assert(equal(pipeline(expected), pipeline(actual)), "candidate filter output changed")

local weak = setmetatable({actual.annotations}, {__mode = "v"})
local envs = {}
for index, filter in ipairs(filters) do
  envs[index] = {engine = {schema = {schema_id = name}}}
  filter.init(envs[index])
  assert(envs[index].data == actual, "filters did not share regional data")
end
actual = nil
for index, filter in ipairs(filters) do
  filter.fini(envs[index])
end
collectgarbage("collect")
assert(package.loaded[name .. "_data"] == nil and weak[1] == nil, "annotation store retained after close")
print(string.format("%s: %d annotations identical; candidate filters identical; released; %.3f MiB retained", name, count, retained / 1024))
