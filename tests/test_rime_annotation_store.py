import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import zlib

import pytest

from platforms.rime.build import (
    PLATFORM_DIR,
    active_regions,
    build,
    build_metadata,
    build_preferred_readings,
    build_single_character_frequencies,
    load_entries,
    write_lua_data,
)


@pytest.fixture
def lua():
    binary = os.environ.get("GANNYU_LUA_BIN") or next(
        (path for name in ("lua5.4", "lua54", "lua5.3", "lua") if (path := shutil.which(name))),
        None,
    )
    if binary is None:
        pytest.skip("set GANNYU_LUA_BIN to run the annotation reader")
    return binary


def literal(value):
    if isinstance(value, str):
        value = value.replace("\\", "\\\\").replace('"', '\\"')
        value = re.sub(r"[\x00-\x1f]", lambda match: f"\\{ord(match[0]):03d}", value)
        return '"' + value + '"'
    if isinstance(value, dict):
        return "{" + ",\n".join(f"[{literal(key)}]={literal(item)}" for key, item in value.items()) + "}"
    if isinstance(value, list):
        return "{" + ",".join(map(literal, value)) + "}"
    return str(value)


def reference(path, annotations, readings, before, after, frequencies):
    path.write_text("return " + literal({
        "annotations": annotations, "readings": readings, "before": before,
        "after": after, "single_character_frequencies": frequencies,
    }), encoding="utf-8")


def check(lua, directory, expected, name):
    result = subprocess.run(
        [lua, str(Path(__file__).parent / "lua/rime_annotation_store.lua"), str(directory), str(expected), name],
        check=True, capture_output=True, text=True, timeout=120,
    )
    print(result.stdout.strip())


def fixture_store(directory, annotations):
    data = directory / "lua"
    data.mkdir(parents=True)
    for name in ("gannyu_annotation_store", "gannyu_data_lifecycle", "gannyu_annotation_filter", "gannyu_single_char_filter", "gannyu_relation_filter"):
        shutil.copyfile(PLATFORM_DIR / f"{name}.lua", data / f"{name}.lua")
    readings = {"我": "ngo3", "们": "men4", "嗰": "go0"}
    before = {"蔬菜": ["青菜"]}
    after = {"青菜": ["蔬菜"]}
    frequencies = {"青": 300000}
    write_lua_data(data / "gannyu_test_data.lua", annotations, readings, before, after, frequencies)
    expected = directory / "reference.lua"
    reference(expected, annotations, readings, before, after, frequencies)
    return expected


@pytest.mark.parametrize("region", active_regions())
def test_all_canonical_annotations_and_filters_match(lua, tmp_path, region):
    build(region, tmp_path)
    _, entries = load_entries(region)
    annotations, before, after = build_metadata(entries)
    expected = tmp_path / "reference.lua"
    reference(expected, annotations, build_preferred_readings(entries), before, after, build_single_character_frequencies(entries))
    check(lua, tmp_path, expected, "gannyu_" + region)


@pytest.mark.parametrize("annotations", [{}, {
    "": "empty key", "empty": "", "青菜": "qiang1 cai3 [官]蔬菜",
    "蔬菜": "[官话词] su1 cai3 [赣]青菜（qiang1 cai3）",
    "引号\"\\换行": "\x00\r\n\t\"\\😀𠮷", "长标注": "赣语/拼音\n" * 10000,
}])
def test_empty_unicode_long_and_escaped_annotations(lua, tmp_path, annotations):
    directory = tmp_path / "方案 directory"
    expected = fixture_store(directory, annotations)
    check(lua, directory, expected, "gannyu_test")


@pytest.mark.parametrize("damage", ["missing", "empty", "short_header", "truncated", "format", "checksum", "region", "offset", "order"])
def test_invalid_store_fails_explicitly(lua, tmp_path, damage):
    fixture_store(tmp_path, {"a": "first", "b": "second"})
    path = tmp_path / "lua/gannyu_test_annotations.bin"
    data = bytearray(path.read_bytes())
    if damage == "missing":
        path.unlink()
    else:
        if damage == "empty":
            data.clear()
        elif damage == "short_header":
            del data[23:]
        elif damage == "truncated":
            del data[-1:]
        elif damage == "format":
            data[7] = ord("2")
        elif damage == "checksum":
            data[-1] ^= 1
        else:
            name_size = struct.unpack_from("<I", data, 16)[0]
            index = 24 + name_size
            if damage == "region":
                data[24] = ord("x")
            elif damage == "offset":
                struct.pack_into("<I", data, index, 0xFFFFFFFF)
            elif damage == "order":
                blob = index + 32
                data[blob] = ord("z")
            struct.pack_into("<I", data, 20, zlib.adler32(data[24:]))
        path.write_bytes(data)
    script = tmp_path / "failure.lua"
    script.write_text(
        "package.path = " + literal(str(tmp_path / "lua/?.lua")) + ";" +
        'local ok, failure = pcall(require, "gannyu_test_data"); assert(not ok, "corruption accepted"); assert(type(failure) == "string"); print(failure)',
        encoding="utf-8",
    )
    subprocess.run([lua, str(script)], check=True, capture_output=True, text=True, timeout=10)


@pytest.mark.parametrize("fault", [
    "none", "seek_end", "seek_set", "read_failure", "read_throw",
    "short_read", "trailing_failure", "trailing_data", "close_failure",
])
def test_exact_read_closes_file_on_success_and_failure(lua, tmp_path, fault):
    fixture_store(tmp_path, {"a": "first", "b": "second"})
    script = tmp_path / "io_failure.lua"
    script.write_text(
        "package.path = " + literal(str(tmp_path / "lua/?.lua")) + ";\n"
        "local target = " + literal(str(tmp_path / "lua/gannyu_test_annotations.bin")) + "\n"
        "local fault = " + literal(fault) + "\n" + r'''
local open = io.open
local closes, reads = 0, 0
io.open = function(path, mode)
  local file, failure = open(path, mode)
  if path ~= target or not file then return file, failure end
  return {
    seek = function(_, whence, position)
      if fault == "seek_end" and whence == "end" then return nil, "injected seek failure" end
      if fault == "seek_set" and whence == "set" then return nil, "injected rewind failure" end
      return file:seek(whence, position)
    end,
    read = function(_, amount)
      assert(type(amount) == "number", "unbounded annotation read")
      reads = reads + 1
      if reads == 1 then
        if fault == "read_failure" then return nil, "injected read failure" end
        if fault == "read_throw" then error("injected read exception") end
        local data = file:read(amount)
        if fault == "short_read" then return data:sub(1, -2) end
        return data
      end
      if fault == "trailing_failure" then return nil, "injected trailing read failure" end
      if fault == "trailing_data" then return "x" end
      return file:read(amount)
    end,
    close = function()
      closes = closes + 1
      local closed, failure = file:close()
      if fault == "close_failure" then return nil, "injected close failure" end
      return closed, failure
    end,
  }
end
local ok, result = pcall(require, "gannyu_test_data")
assert(closes == 1, "annotation file not closed exactly once")
if fault == "none" then
  assert(ok, result)
  assert(result.annotations.a == "first" and result.annotations.b == "second")
  assert(reads == 2, "missing end-of-file validation")
else
  assert(not ok, "I/O failure accepted: " .. fault)
  assert(type(result) == "string", "missing I/O failure reason")
  local reasons = {
    seek_end = "injected seek failure", seek_set = "injected rewind failure",
    read_failure = "injected read failure", read_throw = "injected read exception",
    short_read = "truncated annotation data", trailing_failure = "injected trailing read failure",
    trailing_data = "annotation size changed during read", close_failure = "injected close failure",
  }
  assert(result:find(reasons[fault], 1, true), "incorrect I/O failure reason: " .. result)
end
''',
        encoding="utf-8",
    )
    subprocess.run([lua, str(script)], check=True, capture_output=True, text=True, timeout=10)
