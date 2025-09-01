# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.kts.

# Keep all model classes for serialization
-keep class com.synthnet.aiapp.domain.models.** { *; }
-keep class com.synthnet.aiapp.data.entities.** { *; }

# Keep Room entities and DAOs
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *
-keep @androidx.room.Dao class *

# Keep Hilt generated classes
-keep class dagger.hilt.** { *; }
-keep class * extends dagger.hilt.android.HiltAndroidApp
-keep @dagger.hilt.android.lifecycle.HiltViewModel class * { *; }

# Keep WebSocket classes
-keep class org.java_websocket.** { *; }

# Keep Gson classes for JSON serialization
-keepclassmembers,allowobfuscation class * {
  @com.google.gson.annotations.SerializedName <fields>;
}
-keep,allowobfuscation,allowshrinking class com.google.gson.reflect.TypeToken
-keep,allowobfuscation,allowshrinking class * extends com.google.gson.reflect.TypeToken

# Keep Retrofit and OkHttp classes
-keep class retrofit2.** { *; }
-keep class okhttp3.** { *; }

# Keep Kotlin coroutines
-keep class kotlinx.coroutines.** { *; }

# General Android rules
-keepattributes Signature
-keepattributes *Annotation*
-keep class * extends java.lang.Enum { *; }