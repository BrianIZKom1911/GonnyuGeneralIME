import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from test_android_backspace import SERVICE, declaration


def test_emoji_navigation_clears_composition_and_preserves_ime_entry(tmp_path):
    java = str(Path(os.environ["JAVA_HOME"]) / "bin/java") if os.environ.get("JAVA_HOME") else shutil.which("java")
    gradle = shutil.which("gradle")
    if not java or not gradle:
        pytest.skip("requires Java and Gradle's Kotlin compiler")
    lib = Path(gradle).resolve().parent.parent / "lib"
    if not lib.is_dir():
        lib = Path(gradle).resolve().parent.parent / "libexec/lib"
    stdlib = next(lib.glob("kotlin-stdlib-[0-9]*.jar"))
    source = SERVICE.read_text()
    methods = "\n".join(declaration(source, signature) for signature in [
        "private fun onKey(", "private fun bottomRowLabels(",
    ])
    pages = re.search(r'private val EMOJI_PAGES = listOf\((.*?)\n        \)', source, re.S).group(0).replace("private ", "")
    harness = r'''
data class KeySpec(val label: String, val isLetter: Boolean = false)
data class Snapshot(val rawInput: String = "pending")
class Connection {
    val texts = mutableListOf<String>()
    fun commitText(text: String, cursor: Int) { texts += text }
}
class Harness {
    enum class KeyboardPage { LETTERS, NUMBERS, SYMBOLS, SYMBOLS_MORE, EMOJI }
    var keyboardPage = KeyboardPage.LETTERS
    var emojiPageIndex = 0
    var englishMode = true
    var englishShift = true
    var clears = 0
    var lastSnapshot = Snapshot()
    val currentInputConnection: Connection? = Connection()
    val PUNCT_AFTER_COMPOSE = setOf(",", ".")
    val IME_SWITCH_KEY = "🌐"
    PAGES
    fun resetState(clearAccumulated: Boolean) { check(clearAccumulated); clears++; lastSnapshot = Snapshot("") }
    fun renderKeyboard() {}
    fun handleBackspace() {}
    fun handleEnter() {}
    fun handleSpace() {}
    fun appendInput(value: Char) { error("emoji must not enter the pinyin path") }
    fun processEngineText(value: String): Snapshot { error("composition must be cleared before emoji input") }
    fun applyEngineSnapshot(value: Snapshot) {}
    METHODS
    fun press(label: String) { onKey(KeySpec(label)) }
}
fun main() {
    val h = Harness()
    check(h.EMOJI_PAGES.size == 8 && h.EMOJI_PAGES.all { it.size == 30 })
    val all = h.EMOJI_PAGES.flatten()
    check(all.toSet().size == all.size)
    check(all.all { it.codePointCount(0, it.length) == 1 })
    for (page in Harness.KeyboardPage.entries) {
        h.keyboardPage = page
        for (switcher in listOf(false, true)) {
            val keys = h.bottomRowLabels(switcher)
            check(("🌐" in keys) == switcher)
            if (switcher) check(keys.first() == "🌐")
            if (page != Harness.KeyboardPage.EMOJI) check(keys[keys.indexOf("空格") - 1] == "表情")
            for (width in listOf(308, 320, 363, 760, 1012)) {
                val gap = if (width <= 315) 4 else if (width <= 350) 5 else 6
                val keyWidth = (width - gap * 9) / 10
                val fixed = keys.filter { it != "空格" }.sumOf {
                    when (it) { "中", "英", "123", "ABC", "符号", "🌐" -> (keyWidth * 1.12f).toInt()
                        "↵" -> (keyWidth * 1.6f).toInt(); "赣拼" -> (keyWidth * 1.5f).toInt(); else -> keyWidth }
                }
                check(width - fixed - gap * (keys.size - 1) >= 44)
            }
        }
    }
    h.press("表情")
    check(h.clears == 1 && h.lastSnapshot.rawInput.isEmpty() && h.emojiPageIndex == 0)
    check(h.keyboardPage == Harness.KeyboardPage.EMOJI)
    h.press("上一页"); check(h.emojiPageIndex == 7)
    h.press("下一页"); check(h.emojiPageIndex == 0)
    for (page in h.EMOJI_PAGES) {
        page.forEach { h.press(it) }
        h.press("下一页")
    }
    check(h.currentInputConnection!!.texts == all)
    check(h.keyboardPage == Harness.KeyboardPage.EMOJI && h.clears == 1)
    h.press("赣拼")
    check(h.keyboardPage == Harness.KeyboardPage.LETTERS && !h.englishMode && !h.englishShift)
    check(h.clears == 1)
}
'''.replace("PAGES", pages, 1).replace("METHODS", methods)
    path = tmp_path / "Emoji.kt"
    path.write_text(harness)
    output = tmp_path / "classes"
    subprocess.run([java, "-cp", str(lib / "*"), "org.jetbrains.kotlin.cli.jvm.K2JVMCompiler",
                    "-no-stdlib", "-no-reflect", "-classpath", str(stdlib), "-d", str(output), str(path)],
                   check=True, capture_output=True, text=True)
    subprocess.run([java, "-cp", f"{output}{os.pathsep}{stdlib}", "EmojiKt"], check=True, capture_output=True, text=True)
