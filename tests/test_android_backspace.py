import os
import shutil
import subprocess
from pathlib import Path

import pytest


SERVICE = Path(__file__).resolve().parents[1] / "platforms/android/app/src/main/java/io/gannyu/input/GannyuInputMethodService.kt"


def declaration(source, signature):
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end].replace("private fun", "fun").replace("android.view.inputmethod.EditorInfo", "Info")


def test_backspace_deletes_selection_without_deleting_its_neighbor(tmp_path):
    java = shutil.which("java")
    if os.environ.get("JAVA_HOME"):
        java = str(Path(os.environ["JAVA_HOME"]) / "bin/java")
    compiler = shutil.which("kotlinc")
    gradle = shutil.which("gradle")
    if not java:
        pytest.skip("requires Java")
    if compiler:
        compile_command = [compiler]
        kotlin_lib = Path(compiler).resolve().parent.parent / "lib"
    elif gradle:
        kotlin_lib = Path(gradle).resolve().parent.parent / "lib"
        if not kotlin_lib.is_dir():
            kotlin_lib = Path(gradle).resolve().parent.parent / "libexec/lib"
        if not list(kotlin_lib.glob("kotlin-compiler-embeddable-*.jar")):
            pytest.skip("requires a Kotlin compiler")
        compile_command = [java, "-cp", str(kotlin_lib / "*"), "org.jetbrains.kotlin.cli.jvm.K2JVMCompiler"]
    else:
        pytest.skip("requires kotlinc or a Gradle distribution containing the Kotlin compiler")
    stdlib = next(kotlin_lib.glob("kotlin-stdlib.jar"), None) or next(kotlin_lib.glob("kotlin-stdlib-[0-9]*.jar"))
    source = SERVICE.read_text(encoding="utf-8")
    methods = "\n".join(declaration(source, signature) for signature in [
        "private fun handleBackspace()",
        "override fun onStartInput(",
        "override fun onUpdateSelection(",
        "override fun onFinishInput()",
    ])
    field = next(line.strip() for line in source.splitlines() if "private var editorSelectionCollapsed" in line)
    harness = r'''
object KeyEvent { const val KEYCODE_DEL = 67 }
data class Info(val initialSelStart: Int, val initialSelEnd: Int)
data class Snapshot(val rawInput: String = "")
open class Base {
    open fun onStartInput(attribute: Info?, restarting: Boolean) {}
    open fun onFinishInput() {}
    open fun onUpdateSelection(oldSelStart: Int, oldSelEnd: Int, newSelStart: Int,
        newSelEnd: Int, candidatesStart: Int, candidatesEnd: Int) {}
}
class Connection(var text: String, var start: Int, var end: Int) {
    var readable = true
    var emptyInsteadOfNull = false
    var acceptCommit = true
    val calls = mutableListOf<String>()
    fun getSelectedText(flags: Int): CharSequence? {
        calls += "query"
        if (!readable) return null
        if (start == end) return if (emptyInsteadOfNull) "" else null
        return text.substring(minOf(start, end), maxOf(start, end))
    }
    fun commitText(value: String, newCursorPosition: Int): Boolean {
        calls += "commit"
        check(value == "" && newCursorPosition == 1)
        if (!acceptCommit) return false
        val left = minOf(start, end)
        text = text.removeRange(left, maxOf(start, end))
        start = left
        end = left
        return true
    }
    fun deleteSurroundingTextInCodePoints(before: Int, after: Int): Boolean {
        calls += "surrounding"
        check(before == 1 && after == 0)
        val left = minOf(start, end)
        if (left > 0) {
            val from = text.offsetByCodePoints(left, -1)
            text = text.removeRange(from, left)
            start -= left - from
            end -= left - from
        }
        return true
    }
    fun editorBackspace() {
        calls += "key"
        if (start != end) {
            val left = minOf(start, end)
            text = text.removeRange(left, maxOf(start, end))
            start = left
            end = left
        } else if (start > 0) {
            val from = text.offsetByCodePoints(start, -1)
            text = text.removeRange(from, start)
            start = from
            end = from
        }
    }
}
class Harness: Base() {
    FIELD
    var englishShift = false
    var lastSnapshot = Snapshot()
    var currentInputConnection: Connection? = null
    var engineCalls = 0
    var applies = 0
    val keys = mutableListOf<Int>()
    fun resetState(clearAccumulated: Boolean) {}
    fun stopBackspaceRepeat() {}
    fun hideKeyPreview() {}
    fun processEngineEvent(event: String): Snapshot? { engineCalls++; return null }
    fun applyEngineSnapshot(snapshot: Snapshot?) { applies++ }
    fun sendDownUpKeyEvents(code: Int) { keys += code; currentInputConnection?.editorBackspace() }
    METHODS
}

fun main() {
    var cases = 0
    fun setup(text: String, start: Int, end: Int, readable: Boolean = true): Pair<Harness, Connection> {
        val h = Harness()
        val c = Connection(text, start, end)
        c.readable = readable
        h.currentInputConnection = c
        h.onStartInput(Info(start, end), false)
        return h to c
    }
    val text = "甲乙丙丁"
    for (start in 0..text.length) for (end in 0..text.length) {
        if (start == end) continue
        for (readable in listOf(true, false)) {
            val (h, c) = setup(text, start, end, readable)
            h.handleBackspace()
            check(c.text == text.removeRange(minOf(start, end), maxOf(start, end)))
            check(c.start == c.end && c.start == minOf(start, end))
            check("surrounding" !in c.calls && h.engineCalls == 0)
            check(c.calls.count { it == "commit" || it == "key" } == 1)
            cases++
        }
    }
    for (position in 0..text.length) for (empty in listOf(true, false)) {
        val (h, c) = setup(text, position, position)
        c.emptyInsteadOfNull = empty
        h.handleBackspace()
        val expected = if (position == 0) text else text.removeRange(position - 1, position)
        check(c.text == expected && c.calls == listOf("query", "surrounding"))
        check(h.keys.isEmpty())
        cases++
    }
    for (value in listOf("甲乙\n丙丁", "甲👍🏽乙", "甲乙")) {
        val (h, c) = setup(value, 1, value.length)
        h.handleBackspace()
        check(c.text == "甲" && c.calls == listOf("query", "commit"))
        cases++
    }
    val (repeat, repeatedDoc) = setup(text, 1, 3)
    repeat.handleBackspace()
    check(repeatedDoc.text == "甲丁")
    repeat.handleBackspace()
    check(repeatedDoc.text == "丁")
    check(repeatedDoc.calls == listOf("query", "commit", "query", "surrounding"))
    cases++
    val (composing, composedDoc) = setup(text, 1, 3)
    composing.lastSnapshot = Snapshot("lancong")
    composing.handleBackspace()
    check(composing.engineCalls == 1 && composing.applies == 1)
    check(composedDoc.text == text && composedDoc.calls.isEmpty() && composing.keys.isEmpty())
    cases++
    val disconnected = Harness()
    disconnected.handleBackspace()
    check(disconnected.keys.isEmpty() && disconnected.engineCalls == 0)
    cases++
    val (rejected, rejectedDoc) = setup(text, 1, 3)
    rejectedDoc.acceptCommit = false
    rejected.handleBackspace()
    check(rejectedDoc.text == text && rejectedDoc.calls == listOf("query", "commit"))
    check(rejected.keys.isEmpty())
    cases++
    val (changed, changedDoc) = setup(text, 0, 0, false)
    changedDoc.start = 3
    changedDoc.end = 1
    changed.onUpdateSelection(0, 0, 3, 1, -1, -1)
    changed.handleBackspace()
    check(changedDoc.text == "甲丁" && changed.keys == listOf(KeyEvent.KEYCODE_DEL))
    changedDoc.calls.clear()
    changed.onUpdateSelection(3, 1, 1, 1, -1, -1)
    changed.handleBackspace()
    check(changedDoc.text == "丁" && changedDoc.calls == listOf("query", "surrounding"))
    cases++
    val (unknown, unknownDoc) = setup(text, 1, 3, false)
    unknown.onUpdateSelection(1, 3, -1, -1, -1, -1)
    unknown.handleBackspace()
    check(unknownDoc.text == "甲丁" && unknown.keys == listOf(KeyEvent.KEYCODE_DEL))
    cases++
    for (info in listOf(null, Info(-1, -1))) {
        val (fresh, freshDoc) = setup(text, 1, 3, false)
        fresh.onStartInput(info, true)
        fresh.handleBackspace()
        check(freshDoc.text == "甲丁" && fresh.keys == listOf(KeyEvent.KEYCODE_DEL))
        cases++
    }
    val (finished, finishedDoc) = setup(text, 0, 0, false)
    finished.onFinishInput()
    finishedDoc.start = 1
    finishedDoc.end = 3
    finished.handleBackspace()
    check(finishedDoc.text == "甲丁" && finished.keys == listOf(KeyEvent.KEYCODE_DEL))
    cases++
    println("$cases backspace cases passed")
}
'''.replace("    FIELD", field).replace("    METHODS", methods)
    main = tmp_path / "Main.kt"
    main.write_text(harness, encoding="utf-8")
    jar = tmp_path / "backspace.jar"
    compiled = subprocess.run(
        compile_command + ["-no-stdlib", "-no-reflect", "-jvm-target", "17", "-classpath", str(stdlib), str(main), "-d", str(jar)],
        capture_output=True, text=True, timeout=90,
    )
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run(
        [java, "-cp", os.pathsep.join([str(jar), str(stdlib)]), "MainKt"],
        capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "62 backspace cases passed" in result.stdout
