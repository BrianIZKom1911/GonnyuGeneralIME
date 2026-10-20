import os
import shutil
import subprocess
from pathlib import Path

import pytest


SERVICE = Path(__file__).resolve().parents[1] / "platforms/android/app/src/main/java/io/gannyu/input/GannyuInputMethodService.kt"


def test_enter_dispatches_once_and_keeps_composition_in_rime(tmp_path):
    sdk = Path(os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT") or Path.home() / "Library/Android/sdk")
    platforms = sorted((sdk / "platforms").glob("android-*/android.jar"))
    java = shutil.which("java")
    if os.environ.get("JAVA_HOME"):
        java = str(Path(os.environ["JAVA_HOME"]) / "bin/java")
    compiler = shutil.which("kotlinc")
    gradle = shutil.which("gradle")
    if not java or not platforms:
        pytest.skip("requires Java and an Android SDK platform")
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
    start = source.index("    private fun handleEnter()")
    end = source.index("    private fun processEngineEnter()", start)
    method = source[start:end].replace("private fun handleEnter()", "fun handleEnter()")
    harness = r'''
import android.text.InputType
import android.view.KeyEvent
import android.view.inputmethod.EditorInfo

data class Info(
    val inputType: Int = InputType.TYPE_CLASS_TEXT,
    val imeOptions: Int = EditorInfo.IME_ACTION_SEARCH,
    val actionLabel: String? = null,
    val actionId: Int = 0,
)
class Connection {
    val actions = mutableListOf<Int>()
    var result = true
    fun performEditorAction(action: Int): Boolean { actions += action; return result }
}
data class Snapshot(val rawInput: String = "")
class Harness {
    var lastSnapshot = Snapshot()
    var currentInputConnection: Connection? = Connection()
    var currentInputEditorInfo: Info? = Info()
    val keys = mutableListOf<Int>()
    var engineCalls = 0
    var applies = 0
    fun processEngineEnter(): Snapshot? { engineCalls++; return null }
    fun applyEngineSnapshot(snapshot: Snapshot?) { applies++ }
    fun sendDownUpKeyEvents(key: Int) { keys += key }
    METHOD
}

fun main() {
    var cases = 0
    fun verify(info: Info?, action: Int?) {
        val h = Harness()
        h.currentInputEditorInfo = info
        h.handleEnter()
        check(h.engineCalls == 0 && h.applies == 0)
        check(h.currentInputConnection!!.actions == if (action == null) emptyList<Int>() else listOf(action))
        check(h.keys == if (action == null) listOf(KeyEvent.KEYCODE_ENTER) else emptyList<Int>())
        cases++
    }
    val actions = listOf(
        EditorInfo.IME_ACTION_SEARCH, EditorInfo.IME_ACTION_SEND,
        EditorInfo.IME_ACTION_GO, EditorInfo.IME_ACTION_DONE,
        EditorInfo.IME_ACTION_NEXT, EditorInfo.IME_ACTION_PREVIOUS,
    )
    for (action in actions) {
        verify(Info(imeOptions = action), action)
        verify(Info(imeOptions = action or EditorInfo.IME_FLAG_NO_EXTRACT_UI), action)
        verify(Info(imeOptions = action or EditorInfo.IME_FLAG_NO_ENTER_ACTION), null)
        verify(Info(inputType = InputType.TYPE_NULL, imeOptions = action), null)
        verify(Info(imeOptions = action, actionLabel = "custom", actionId = 1234), 1234)
        verify(Info(imeOptions = action, actionLabel = "custom", actionId = 0), action)
        verify(Info(imeOptions = action, actionLabel = "", actionId = 1234), action)
    }
    verify(null, null)
    verify(Info(imeOptions = EditorInfo.IME_ACTION_NONE), null)
    verify(Info(imeOptions = EditorInfo.IME_ACTION_UNSPECIFIED), null)
    verify(Info(imeOptions = EditorInfo.IME_ACTION_NONE, actionLabel = "custom", actionId = 1234), 1234)
    verify(Info(imeOptions = EditorInfo.IME_ACTION_SEARCH or EditorInfo.IME_FLAG_NO_ENTER_ACTION,
                actionLabel = "custom", actionId = 1234), null)
    verify(Info(inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_MULTI_LINE,
                imeOptions = EditorInfo.IME_ACTION_NONE), null)
    verify(Info(inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_MULTI_LINE,
                imeOptions = EditorInfo.IME_ACTION_SEND), EditorInfo.IME_ACTION_SEND)
    for (connected in listOf(true, false)) {
        val h = Harness()
        h.lastSnapshot = Snapshot("lancong")
        if (!connected) h.currentInputConnection = null
        h.handleEnter()
        check(h.engineCalls == 1 && h.applies == 1)
        check(h.keys.isEmpty() && h.currentInputConnection?.actions.orEmpty().isEmpty())
        cases++
    }
    val disconnected = Harness()
    disconnected.currentInputConnection = null
    disconnected.handleEnter()
    check(disconnected.keys.isEmpty() && disconnected.engineCalls == 0)
    cases++
    val rejected = Harness()
    rejected.currentInputConnection!!.result = false
    rejected.handleEnter()
    check(rejected.currentInputConnection!!.actions == listOf(EditorInfo.IME_ACTION_SEARCH))
    check(rejected.keys.isEmpty() && rejected.engineCalls == 0)
    cases++
    println("$cases enter dispatch cases passed")
}
'''.replace("    METHOD", method)
    main = tmp_path / "Main.kt"
    main.write_text(harness, encoding="utf-8")
    jar = tmp_path / "enter.jar"
    compiled = subprocess.run(
        compile_command + ["-no-stdlib", "-no-reflect", "-jvm-target", "17", "-classpath", os.pathsep.join([str(platforms[-1]), str(stdlib)]), str(main), "-d", str(jar)],
        capture_output=True, text=True, timeout=90,
    )
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run(
        [java, "-cp", os.pathsep.join([str(jar), str(stdlib)]), "MainKt"],
        capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "53 enter dispatch cases passed" in result.stdout
