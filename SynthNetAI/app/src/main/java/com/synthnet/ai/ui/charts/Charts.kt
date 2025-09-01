package com.synthnet.ai.ui.charts

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.unit.dp

@Composable
fun LineChart(
    dataPoints: List<Float>,
    modifier: Modifier = Modifier,
    lineColor: Color = MaterialTheme.colorScheme.primary
) {
    Canvas(modifier = modifier.fillMaxSize()) {
        drawLineChart(dataPoints, lineColor)
    }
}

@Composable
fun BarChart(
    dataPoints: List<Float>,
    labels: List<String>,
    modifier: Modifier = Modifier,
    barColor: Color = MaterialTheme.colorScheme.secondary
) {
    Canvas(modifier = modifier.fillMaxSize()) {
        drawBarChart(dataPoints, barColor)
    }
}

@Composable
fun PieChart(
    slices: List<PieSlice>,
    modifier: Modifier = Modifier
) {
    Canvas(modifier = modifier.fillMaxSize()) {
        drawPieChart(slices)
    }
}

private fun DrawScope.drawLineChart(dataPoints: List<Float>, color: Color) {
    if (dataPoints.size < 2) return
    
    val maxValue = dataPoints.maxOrNull() ?: 0f
    val minValue = dataPoints.minOrNull() ?: 0f
    val range = maxValue - minValue
    
    val stepX = size.width / (dataPoints.size - 1)
    val points = dataPoints.mapIndexed { index, value ->
        val x = index * stepX
        val y = size.height - ((value - minValue) / range) * size.height
        Offset(x, y)
    }
    
    for (i in 0 until points.size - 1) {
        drawLine(
            color = color,
            start = points[i],
            end = points[i + 1],
            strokeWidth = 3.dp.toPx()
        )
    }
}

private fun DrawScope.drawBarChart(dataPoints: List<Float>, color: Color) {
    val maxValue = dataPoints.maxOrNull() ?: 0f
    val barWidth = size.width / dataPoints.size
    
    dataPoints.forEachIndexed { index, value ->
        val barHeight = (value / maxValue) * size.height
        val left = index * barWidth
        val top = size.height - barHeight
        
        drawRect(
            color = color,
            topLeft = Offset(left, top),
            size = androidx.compose.ui.geometry.Size(barWidth * 0.8f, barHeight)
        )
    }
}

private fun DrawScope.drawPieChart(slices: List<PieSlice>) {
    var startAngle = 0f
    val centerX = size.width / 2
    val centerY = size.height / 2
    val radius = minOf(centerX, centerY) * 0.8f
    
    slices.forEach { slice ->
        val sweepAngle = (slice.value / slices.sumOf { it.value.toDouble() }) * 360f
        
        drawArc(
            color = slice.color,
            startAngle = startAngle,
            sweepAngle = sweepAngle.toFloat(),
            useCenter = true,
            topLeft = Offset(centerX - radius, centerY - radius),
            size = androidx.compose.ui.geometry.Size(radius * 2, radius * 2)
        )
        
        startAngle += sweepAngle.toFloat()
    }
}

data class PieSlice(
    val value: Float,
    val color: Color,
    val label: String
)