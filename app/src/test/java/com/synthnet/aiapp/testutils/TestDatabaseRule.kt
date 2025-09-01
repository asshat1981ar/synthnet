package com.synthnet.aiapp.testutils

import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.synthnet.aiapp.data.database.SynthNetDatabase
import org.junit.rules.TestWatcher
import org.junit.runner.Description
import java.io.IOException

/**
 * JUnit rule that creates an in-memory Room database for testing
 * and properly closes it after each test.
 */
class TestDatabaseRule : TestWatcher() {
    
    lateinit var database: SynthNetDatabase
        private set
    
    override fun starting(description: Description) {
        super.starting(description)
        // Create an in-memory database for testing
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            SynthNetDatabase::class.java
        )
            // Allow main thread queries for testing
            .allowMainThreadQueries()
            // Don't keep query logs in memory
            .setQueryCallback({ _, _ -> }, { it.run() })
            .build()
    }
    
    override fun finished(description: Description) {
        super.finished(description)
        try {
            database.close()
        } catch (e: IOException) {
            // Ignore close errors in tests
        }
    }
    
    /**
     * Clears all data from the database
     */
    fun clearDatabase() {
        database.clearAllTables()
    }
    
    /**
     * Inserts test data using the provided block
     */
    inline fun insertTestData(block: SynthNetDatabase.() -> Unit) {
        database.block()
    }
    
    /**
     * Executes a query and returns the result
     */
    inline fun <T> executeQuery(block: SynthNetDatabase.() -> T): T {
        return database.block()
    }
}