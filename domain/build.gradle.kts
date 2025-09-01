
plugins {
    id("org.jetbrains.kotlin.jvm")
    id("kotlin-kapt")
}

java {
    sourceCompatibility = JavaVersion.VERSION_1_8
    targetCompatibility = JavaVersion.VERSION_1_8
}

dependencies {
    implementation(project(":data"))
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    
    // Hilt
    implementation("com.google.dagger:hilt-core:2.48")
    kapt("com.google.dagger:hilt-compiler:2.48")
    
    // Serialization
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")
    
    // DateTime
    implementation("org.jetbrains.kotlinx:kotlinx-datetime:0.5.0")
}
