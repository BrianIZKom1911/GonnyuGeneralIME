import os
import shutil
import subprocess
from pathlib import Path

import pytest

from test_android_backspace import SERVICE, declaration


def test_candidate_batches_and_vertical_drag(tmp_path):
    java = str(Path(os.environ["JAVA_HOME"]) / "bin/java") if os.environ.get("JAVA_HOME") else shutil.which("java")
    gradle = shutil.which("gradle")
    if not java or not gradle:
        pytest.skip("requires Java and Gradle's Kotlin compiler")
    lib = Path(gradle).resolve().parent.parent / "lib"
    if not lib.is_dir():
        lib = Path(gradle).resolve().parent.parent / "libexec/lib"
    if not list(lib.glob("kotlin-compiler-embeddable-*.jar")):
        pytest.skip("requires Gradle's Kotlin compiler")
    stdlib = next(lib.glob("kotlin-stdlib-[0-9]*.jar"))
    source = SERVICE.read_text()
    methods = "\n".join(declaration(source, signature) for signature in [
        "private fun loadMoreCandidates()",
        "private fun toggleCandidateExpansion()",
        "private fun collapseCandidateExpansion()",
    ])
    touch = declaration(source, "override fun onTouchEvent(event: MotionEvent)")
    fields = "\n".join(line.strip().replace("private ", "") for line in source.splitlines() if any(
        f"private var {name} " in line for name in [
            "candidateLoadGeneration", "candidateNextOffset", "candidateHasMore", "candidateLoading", "candidateLoadFailed",
        ]
    ))
    harness = r'''
import java.util.ArrayDeque
data class Candidate(val globalIndex: Int)
data class Snapshot(val rawInput: String = "abc", val schemaId: String = "schema",
    val candidates: List<Candidate> = (0..<9).map { Candidate(it) })
class Tasks {
    val queue = ArrayDeque<() -> Unit>()
    fun execute(block: () -> Unit) { queue.add(block) }
    fun post(block: () -> Unit) { queue.add(block) }
    fun drain() { while (queue.isNotEmpty()) queue.removeFirst()() }
}
data class Batch(val offset: Int, val candidates: List<Candidate>, val hasMore: Boolean,
    val rawInput: String = "abc", val schemaId: String = "schema")
val batches = mutableMapOf<String, Batch>()
class JSONObject(val key: String) {
    val value get() = batches.getValue(key)
    fun optInt(name: String, fallback: Int) = value.offset
    fun optString(name: String) = if (name == "rawInput") value.rawInput else value.schemaId
    fun optBoolean(name: String) = value.hasMore
    override fun toString() = key
}
class Bridge {
    val requests = mutableListOf<Int>()
    var fail = false
    var wrongIndex = false
    fun nativeCandidates(handle: Long, offset: Int, limit: Int): String? {
        requests += offset
        if (fail) return null
        val end = minOf(205, offset + limit)
        val key = "batch-${batches.size}"
        batches[key] = Batch(offset, (offset..<end).map { Candidate(it + if (wrongIndex) 1 else 0) }, end < 205)
        return key
    }
}
class Harness {
    FIELDS
    var candidateExpanded = false
    var pipelineReady = true
    var pipelineHandle = 1L
    var lastSnapshot = Snapshot()
    val expandedCandidates = mutableListOf<Candidate>()
    val candidateLoadExecutor = Tasks()
    val candidateLoadHandler = Tasks()
    val nativeBridge = Bridge()
    fun renderExpandedCandidates() {}
    fun renderState() {}
    fun parseSnapshot(key: String) = Snapshot(candidates = batches.getValue(key).candidates)
    fun drain() { candidateLoadExecutor.drain(); candidateLoadHandler.drain() }
    METHODS
}
class MotionEvent(val action: Int, val x: Float, val y: Float) {
    companion object { const val ACTION_DOWN = 0; const val ACTION_UP = 1; const val ACTION_MOVE = 2; const val ACTION_CANCEL = 3 }
}
class Parent { var blocked = false; fun requestDisallowInterceptTouchEvent(value: Boolean) { blocked = value } }
open class Base { open fun onTouchEvent(event: MotionEvent): Boolean = false }
class TouchHarness: Base() {
    var downX = 0f
    var downY = 0f
    var moved = false
    val candidate = Candidate(0)
    val parent = Parent()
    var commits = 0
    fun dp(value: Int) = value
    fun commitCandidate(value: Candidate) { commits++ }
    TOUCH
}
fun main() {
    val h = Harness()
    h.toggleCandidateExpansion()
    h.loadMoreCandidates()
    check(h.candidateLoading && h.expandedCandidates.size == 9 && h.candidateLoadExecutor.queue.size == 1)
    h.drain()
    check(h.expandedCandidates.map { it.globalIndex } == (0..<100).toList())
    h.loadMoreCandidates(); h.drain()
    check(h.expandedCandidates.map { it.globalIndex } == (0..<200).toList())
    h.loadMoreCandidates(); h.drain()
    check(h.expandedCandidates.map { it.globalIndex } == (0..<205).toList() && !h.candidateHasMore)
    h.loadMoreCandidates(); h.drain()
    check(h.nativeBridge.requests == listOf(0, 100, 200))
    val retry = Harness()
    retry.nativeBridge.fail = true
    retry.toggleCandidateExpansion(); retry.drain()
    check(retry.candidateLoadFailed && !retry.candidateLoading && retry.expandedCandidates.size == 9)
    retry.nativeBridge.fail = false
    retry.loadMoreCandidates(); retry.drain()
    check(retry.nativeBridge.requests == listOf(0, 0) && retry.expandedCandidates.size == 100)
    retry.nativeBridge.wrongIndex = true
    retry.loadMoreCandidates(); retry.drain()
    check(retry.candidateLoadFailed && retry.candidateNextOffset == 100 && retry.expandedCandidates.size == 100)
    val reopened = Harness()
    reopened.toggleCandidateExpansion()
    reopened.collapseCandidateExpansion()
    reopened.toggleCandidateExpansion()
    reopened.drain()
    check(reopened.nativeBridge.requests == listOf(0, 0) && reopened.expandedCandidates.size == 100)
    for (invalidation in 0..3) {
        val stale = Harness()
        stale.toggleCandidateExpansion()
        when (invalidation) {
            0 -> stale.candidateLoadGeneration++
            1 -> stale.pipelineHandle++
            2 -> stale.lastSnapshot = Snapshot(rawInput = "new")
            3 -> stale.lastSnapshot = Snapshot(schemaId = "other")
        }
        stale.drain()
        check(stale.expandedCandidates.size == 9)
    }
    for (dx in listOf(0f, 50f)) {
        val t = TouchHarness()
        t.onTouchEvent(MotionEvent(0, 20f, 20f))
        t.onTouchEvent(MotionEvent(2, 20f + dx, 70f))
        check(!t.parent.blocked)
        t.onTouchEvent(MotionEvent(1, 20f + dx, 70f))
        check(t.commits == 0)
    }
    val upOnly = TouchHarness()
    upOnly.onTouchEvent(MotionEvent(0, 20f, 20f))
    upOnly.onTouchEvent(MotionEvent(1, 20f, 70f))
    check(upOnly.commits == 0)
    val tap = TouchHarness()
    tap.onTouchEvent(MotionEvent(0, 20f, 20f))
    tap.onTouchEvent(MotionEvent(1, 21f, 21f))
    check(tap.commits == 1)
    println("candidate paging and drag regressions passed")
}
'''.replace("    FIELDS", fields).replace("    METHODS", methods).replace("    TOUCH", touch)
    main = tmp_path / "Main.kt"
    main.write_text(harness)
    jar = tmp_path / "paging.jar"
    compiled = subprocess.run(
        [java, "-cp", str(lib / "*"), "org.jetbrains.kotlin.cli.jvm.K2JVMCompiler", "-no-stdlib", "-no-reflect", "-classpath", str(stdlib), str(main), "-d", str(jar)],
        capture_output=True, text=True, timeout=90,
    )
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([java, "-cp", os.pathsep.join([str(jar), str(stdlib)]), "MainKt"], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "candidate paging and drag regressions passed" in result.stdout
