package io.gannyu.input

import android.content.Context
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.View
import android.view.ViewConfiguration
import android.widget.Button
import android.widget.LinearLayout

/**
 * A keyboard row with separate visual and logical key bounds.
 *
 * AOSP LatinIME models a key's visible bounds independently from its hit box, so the visual
 * horizontal/vertical gaps still belong to a key. This row keeps the existing child layout and
 * routes each touch cell to its closest visible Button.
 *
 * Reference: AOSP LatinIME Key.java (mWidth/mHeight versus mHitBox) and KeyDetector.java.
 */
internal class KeyboardRowLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
) : LinearLayout(context, attrs) {
    private val touchSlop = ViewConfiguration.get(context).scaledTouchSlop
    private val pointerKeys = linkedMapOf<Int, Button>()
    private val pointerDownTimes = linkedMapOf<Int, Long>()
    private val blockedPointers = mutableSetOf<Int>()

    override fun dispatchTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                pointerDownTimes.clear()
                blockedPointers.clear()
                pointerKeys.clear()
                assignPointer(event, event.actionIndex)
                if (pointerKeys.isEmpty()) return super.dispatchTouchEvent(event)
                dispatchPointer(event, event.actionIndex, MotionEvent.ACTION_DOWN)
                return true
            }

            MotionEvent.ACTION_POINTER_DOWN -> {
                val index = event.actionIndex
                val id = event.getPointerId(index)
                assignPointer(event, index)
                if (id in pointerKeys) dispatchPointer(event, index, MotionEvent.ACTION_DOWN)
            }

            MotionEvent.ACTION_MOVE -> {
                if (pointerKeys.isEmpty()) return if (blockedPointers.isEmpty()) super.dispatchTouchEvent(event) else true
                pointerKeys.toMap().forEach { (pointerId, target) ->
                    val index = event.findPointerIndex(pointerId)
                    if (index < 0 || event.getY(index) < -touchSlop || event.getY(index) >= height + touchSlop ||
                        nearestKey(event.getX(index).toInt()) !== target
                    ) {
                        dispatchPointer(event, index, MotionEvent.ACTION_CANCEL)
                        pointerKeys.remove(pointerId)
                        pointerDownTimes.remove(pointerId)
                        blockedPointers += pointerId
                    } else {
                        dispatchPointer(event, index, MotionEvent.ACTION_MOVE)
                    }
                }
            }

            MotionEvent.ACTION_CANCEL -> {
                if (pointerKeys.isEmpty()) return super.dispatchTouchEvent(event)
                pointerKeys.keys.toList().forEach { pointerId ->
                    dispatchPointer(event, event.findPointerIndex(pointerId), MotionEvent.ACTION_CANCEL)
                }
                pointerKeys.clear()
                pointerDownTimes.clear()
                blockedPointers.clear()
                return true
            }

            MotionEvent.ACTION_POINTER_UP, MotionEvent.ACTION_UP -> {
                val index = event.actionIndex
                val pointerId = event.getPointerId(index)
                val target = pointerKeys[pointerId]
                if (target != null) {
                    val action = if (event.getY(index) < -touchSlop || event.getY(index) >= height + touchSlop ||
                        nearestKey(event.getX(index).toInt()) !== target
                    ) MotionEvent.ACTION_CANCEL else MotionEvent.ACTION_UP
                    dispatchPointer(event, index, action)
                }
                pointerKeys.remove(pointerId)
                pointerDownTimes.remove(pointerId)
                blockedPointers.remove(pointerId)
                if (event.actionMasked == MotionEvent.ACTION_UP) {
                    pointerKeys.clear()
                    pointerDownTimes.clear()
                    blockedPointers.clear()
                }
                return true
            }

            else -> if (pointerKeys.isEmpty() && blockedPointers.isEmpty()) return super.dispatchTouchEvent(event)
        }
        return true
    }

    private fun assignPointer(event: MotionEvent, pointerIndex: Int) {
        val pointerId = event.getPointerId(pointerIndex)
        val target = nearestKey(event.getX(pointerIndex).toInt()) ?: return
        if (pointerKeys.values.any { it === target }) {
            blockedPointers += pointerId
            return
        }
        pointerKeys[pointerId] = target
        pointerDownTimes[pointerId] = event.downTime
    }

    private fun nearestKey(x: Int): Button? {
        val keys = ArrayList<Button>(childCount)
        for (index in 0 until childCount) {
            val child = getChildAt(index)
            if (child is Button && child.visibility == View.VISIBLE && child.isEnabled) {
                keys += child
            }
        }
        val lefts = IntArray(keys.size) { keys[it].left }
        val rights = IntArray(keys.size) { keys[it].right }
        val nearestIndex = HorizontalKeyHitResolver.nearestKeyIndex(x, lefts, rights)
        if (nearestIndex < 0) return null
        return keys[nearestIndex]
    }

    private fun dispatchPointer(source: MotionEvent, pointerIndex: Int, action: Int) {
        if (pointerIndex < 0) return
        val pointerId = source.getPointerId(pointerIndex)
        val target = pointerKeys[pointerId] ?: return
        val event = MotionEvent.obtain(
            pointerDownTimes[pointerId] ?: source.downTime,
            source.eventTime,
            action,
            source.getX(pointerIndex) - target.left,
            source.getY(pointerIndex) - target.top,
            source.metaState,
        )
        event.source = source.source
        try {
            target.dispatchTouchEvent(event)
        } finally {
            event.recycle()
        }
    }
}
