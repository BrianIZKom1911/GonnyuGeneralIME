local function clean_spelling(comment)
  return (comment or ""):gsub("^G", ""):gsub(" G", " ")
end

local function sentence_reading(text, data)
  local readings = {}
  for character in text:gmatch("[%z\1-\127\194-\244][\128-\191]*") do
    local reading = data.readings[character]
    if not reading then
      return nil
    end
    table.insert(readings, reading)
  end
  return table.concat(readings, " ")
end

local M = {}

function M.func(input, env)
  local lifecycle = require("gannyu_data_lifecycle")
  local data = lifecycle.current(env)
  local enabled = require("gannyu_input_options").enabled(env, "annotations")
  for candidate in input:iter() do
    candidate.comment = enabled and (data.annotations[candidate.text]
      or sentence_reading(candidate.text, data)
      or clean_spelling(candidate.comment)) or ""
    yield(candidate)
  end
end

local lifecycle = require("gannyu_data_lifecycle")
M.init = lifecycle.init
M.fini = lifecycle.fini

return M
