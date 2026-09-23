// Drop these classes into your Android Studio project!

package com.example.emdadiaquran

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import android.graphics.BitmapFactory
import android.widget.Toast
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import java.io.File
import java.io.FileOutputStream

// --- 1. Database Helper to read ayahinfo.db ---
class AyahDatabaseHelper(private val context: Context) : SQLiteOpenHelper(context, DB_NAME, null, 1) {
    companion object {
        private const val DB_NAME = "ayahinfo.db"
    }

    // Copy the database from assets/ to the app's internal storage
    fun copyDatabase() {
        val dbFile = context.getDatabasePath(DB_NAME)
        if (!dbFile.exists()) {
            dbFile.parentFile?.mkdirs()
            context.assets.open(DB_NAME).use { input ->
                FileOutputStream(dbFile).use { output ->
                    input.copyTo(output)
                }
            }
        }
    }

    data class AyahBound(val sura: Int, val ayah: Int, val minX: Int, val maxX: Int, val minY: Int, val maxY: Int)

    fun getAyahBoundsForPage(pageNumber: Int): List<AyahBound> {
        val bounds = mutableListOf<AyahBound>()
        val db = this.readableDatabase
        val cursor = db.rawQuery("SELECT sura_number, ayah_number, min_x, max_x, min_y, max_y FROM glyphs WHERE page_number = ?", arrayOf(pageNumber.toString()))
        while (cursor.moveToNext()) {
            bounds.add(AyahBound(
                cursor.getInt(0), cursor.getInt(1),
                cursor.getInt(2), cursor.getInt(3),
                cursor.getInt(4), cursor.getInt(5)
            ))
        }
        cursor.close()
        return bounds
    }

    override fun onCreate(db: SQLiteDatabase?) {}
    override fun onUpgrade(db: SQLiteDatabase?, oldVersion: Int, newVersion: Int) {}
}

// --- 2. Surah List Screen ---
@Composable
fun SuraListScreen(onSuraClick: (Int) -> Unit) {
    // Hardcoded starting pages for Emdadia (You can update these based on your DB)
    val suraStartPages = listOf(1, 2, 50, 76, 106) // Add all 114 starting pages here
    val suraNames = listOf("Al-Fatiha", "Al-Baqarah", "Al-Imran", "An-Nisa", "Al-Ma'idah")

    LazyColumn {
        itemsIndexed(suraNames) { index, name ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp)
                    .clickable { onSuraClick(suraStartPages[index]) }
            ) {
                Text(text = ". ", modifier = Modifier.padding(16.dp), style = MaterialTheme.typography.titleLarge)
            }
        }
    }
}

// --- 3. Quran Page Screen (Image + Clickable Bounds) ---
@Composable
fun QuranPageScreen(pageNumber: Int) {
    val context = LocalContext.current
    var ayahBounds by remember { mutableStateOf<List<AyahDatabaseHelper.AyahBound>>(emptyList()) }
    var highlightedAyah by remember { mutableStateOf<AyahDatabaseHelper.AyahBound?>(null) }
    var imageSize by remember { mutableStateOf(Size.Zero) }

    // Load Database Bounds
    LaunchedEffect(pageNumber) {
        val dbHelper = AyahDatabaseHelper(context)
        dbHelper.copyDatabase()
        ayahBounds = dbHelper.getAyahBoundsForPage(pageNumber)
    }

    // Load Image from Assets
    val imageName = String.format("page%03d.png", pageNumber)
    val bitmap = remember(pageNumber) {
        context.assets.open(imageName).use { BitmapFactory.decodeStream(it) }?.asImageBitmap()
    }

    if (bitmap != null) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .pointerInput(Unit) {
                    detectTapGestures { tapOffset ->
                        // Calculate scale factors (Screen Size vs Original Image 2999x1859)
                        val scaleX = bitmap.width / imageSize.width
                        val scaleY = bitmap.height / imageSize.height
                        
                        // Map screen click to original image coordinates
                        val mappedX = tapOffset.x * scaleX
                        val mappedY = tapOffset.y * scaleY

                        // Find which Ayah was clicked
                        val clicked = ayahBounds.find {
                            mappedX >= it.minX && mappedX <= it.maxX &&
                            mappedY >= it.minY && mappedY <= it.maxY
                        }

                        if (clicked != null) {
                            highlightedAyah = clicked
                            Toast.makeText(context, "Sura , Ayah ", Toast.LENGTH_SHORT).show()
                        } else {
                            highlightedAyah = null
                        }
                    }
                }
        ) {
            Image(
                bitmap = bitmap,
                contentDescription = "Quran Page ",
                modifier = Modifier.fillMaxSize(),
                onTextLayout = { /* Not used */ }
            )

            // Optional: Draw a highlight over the clicked Ayah
            Canvas(modifier = Modifier.fillMaxSize()) {
                imageSize = size // Capture screen size of the image
                highlightedAyah?.let {
                    val scaleX = size.width / bitmap.width
                    val scaleY = size.height / bitmap.height
                    drawRect(
                        color = Color.Blue.copy(alpha = 0.3f),
                        topLeft = Offset(it.minX * scaleX, it.minY * scaleY),
                        size = Size((it.maxX - it.minX) * scaleX, (it.maxY - it.minY) * scaleY)
                    )
                }
            }
        }
    } else {
        Text("Loading Page ...")
    }
}
