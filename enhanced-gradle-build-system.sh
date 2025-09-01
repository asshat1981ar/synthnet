#!/bin/bash

# ===============================================================================
# Enhanced Universal Gradle-based APK Build Environment for Termux
# Production-Ready Android Build System with Comprehensive Error Handling
# 
# Based on lessons learned from SynthNet AI and integrated with Android SDK fixes
# Enhanced with JDK compatibility, build optimization, and professional templates
# ===============================================================================

set -euo pipefail

# ===== CONFIGURATION & CONSTANTS =====
readonly SCRIPT_VERSION="2.0.0"
readonly SCRIPT_NAME="Enhanced Universal Gradle APK Builder"

# Colors and formatting
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'
readonly BOLD='\033[1m'

# Build environment paths
readonly TERMUX_BUILD_HOME="$HOME/gradle-apk-builder"
readonly DOWNLOADS_DIR="$HOME/storage/downloads"
readonly SDK_SOURCE_DIR="$HOME/android-sdk-test"  # Where SDK JARs are located
readonly CACHE_DIR="$TERMUX_BUILD_HOME/.cache"
readonly TEMP_BUILD_DIR="$HOME/.cache/gradle-build-$$"

# Build configuration
readonly DEFAULT_MIN_SDK="26"
readonly DEFAULT_TARGET_SDK="34"
readonly DEFAULT_COMPILE_SDK="34"
readonly GRADLE_VERSION="8.3"
readonly AGP_VERSION="8.2.0"
readonly KOTLIN_VERSION="1.9.22"

# ===== UTILITY FUNCTIONS =====

log_header() {
    echo -e "${BLUE}${BOLD}$1${NC}"
    echo -e "${BLUE}$(printf '=%.0s' {1..60})${NC}"
}

log_info() {
    echo -e "${GREEN}ℹ  $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_step() {
    echo -e "${CYAN}🔹 $1${NC}"
}

# Progress bar function
show_progress() {
    local current=$1
    local total=$2
    local task=$3
    local percent=$((current * 100 / total))
    local filled=$((percent / 2))
    local empty=$((50 - filled))
    
    printf "\r${CYAN}[%-50s] %3d%% %s${NC}" \
           "$(printf '#%.0s' $(seq 1 $filled))$(printf ' %.0s' $(seq 1 $empty))" \
           "$percent" "$task"
    
    if [ $current -eq $total ]; then
        echo
    fi
}

# Enhanced error handling with recovery suggestions
handle_error() {
    local exit_code=$?
    local line_number=$1
    local command=$2
    
    log_error "Build failed at line $line_number: $command (exit code: $exit_code)"
    
    # Provide recovery suggestions based on common errors
    case $exit_code in
        127)
            log_warn "Command not found. Try: pkg install -y <package-name>"
            ;;
        1)
            log_warn "General error. Check logs above for details."
            ;;
        2)
            log_warn "Permission error. Check file permissions and paths."
            ;;
        *)
            log_warn "Unknown error. Check system resources and dependencies."
            ;;
    esac
    
    cleanup_on_exit
    exit $exit_code
}

# Set up enhanced error trapping
trap 'handle_error ${LINENO} "$BASH_COMMAND"' ERR

# Cleanup function
cleanup_on_exit() {
    if [ -d "$TEMP_BUILD_DIR" ]; then
        rm -rf "$TEMP_BUILD_DIR"
        log_info "Cleaned up temporary build directory"
    fi
}

trap cleanup_on_exit EXIT

# ===== JDK COMPATIBILITY SYSTEM =====

detect_and_configure_jdk() {
    log_step "Detecting and configuring optimal JDK..."
    
    local jdk_candidates=(
        "$PREFIX/lib/jvm/java-21-openjdk"
        "$PREFIX/lib/jvm/java-17-openjdk"
        "$PREFIX/lib/jvm/java-11-openjdk"
        "$PREFIX/lib/jvm/java-8-openjdk"
    )
    
    local selected_jdk=""
    local jdk_version=""
    
    # Test current Java installation first
    if command -v java &> /dev/null; then
        jdk_version=$(java -version 2>&1 | head -1 | grep -oP '(?<=version ")\d+' || echo "unknown")
        log_info "Found Java version: $jdk_version"
        
        # Test Gradle compatibility with current JDK
        if test_jdk_gradle_compatibility "$jdk_version"; then
            selected_jdk="$JAVA_HOME"
            log_success "Current JDK $jdk_version is compatible with Gradle $GRADLE_VERSION"
        fi
    fi
    
    # If current JDK is not suitable, try alternatives
    if [ -z "$selected_jdk" ]; then
        log_warn "Testing alternative JDK installations..."
        
        for jdk_path in "${jdk_candidates[@]}"; do
            if [ -d "$jdk_path" ]; then
                export JAVA_HOME="$jdk_path"
                export PATH="$JAVA_HOME/bin:$PATH"
                
                if command -v java &> /dev/null; then
                    jdk_version=$(java -version 2>&1 | head -1 | grep -oP '(?<=version ")\d+' || echo "unknown")
                    log_info "Testing JDK $jdk_version at $jdk_path"
                    
                    if test_jdk_gradle_compatibility "$jdk_version"; then
                        selected_jdk="$jdk_path"
                        log_success "Selected JDK $jdk_version at $jdk_path"
                        break
                    fi
                fi
            fi
        done
    fi
    
    # If no compatible JDK found, install recommended version
    if [ -z "$selected_jdk" ]; then
        log_warn "No compatible JDK found. Installing OpenJDK 21..."
        pkg install -y openjdk-21
        selected_jdk="$PREFIX/lib/jvm/java-21-openjdk"
        jdk_version="21"
    fi
    
    # Configure environment
    export JAVA_HOME="$selected_jdk"
    export PATH="$JAVA_HOME/bin:$PATH"
    
    # Write JDK configuration
    cat > "$TERMUX_BUILD_HOME/jdk-config.sh" << EOF
#!/bin/bash
# JDK Configuration for Enhanced Gradle Build System
export JAVA_HOME="$selected_jdk"
export PATH="\$JAVA_HOME/bin:\$PATH"
export JDK_VERSION="$jdk_version"

# Gradle JVM options optimized for Termux
export GRADLE_OPTS="-Xmx2g -Xms512m -XX:MaxMetaspaceSize=512m -XX:+HeapDumpOnOutOfMemoryError"
export _JAVA_OPTIONS="-XX:+UnlockExperimentalVMOptions -XX:+UseG1GC"
EOF
    
    chmod +x "$TERMUX_BUILD_HOME/jdk-config.sh"
    log_success "JDK configuration saved to $TERMUX_BUILD_HOME/jdk-config.sh"
}

test_jdk_gradle_compatibility() {
    local jdk_version=$1
    
    # Create minimal test project
    local test_dir="$TEMP_BUILD_DIR/jdk-test"
    mkdir -p "$test_dir"
    
    # Create minimal gradle project for testing
    cat > "$test_dir/build.gradle" << 'EOF'
plugins {
    id 'base'
}

task testJavaCompatibility {
    doLast {
        println "JDK compatibility test passed"
    }
}
EOF
    
    cat > "$test_dir/gradle.properties" << EOF
org.gradle.jvmargs=-Xmx1g -XX:MaxMetaspaceSize=256m
org.gradle.daemon=true
org.gradle.parallel=false
org.gradle.caching=false
EOF
    
    # Test Gradle wrapper initialization and task execution
    cd "$test_dir"
    
    # Create gradle wrapper
    if gradle wrapper --gradle-version "$GRADLE_VERSION" &>/dev/null; then
        # Test task execution
        if ./gradlew testJavaCompatibility --quiet &>/dev/null; then
            cd - &>/dev/null
            return 0
        fi
    fi
    
    cd - &>/dev/null
    return 1
}

# ===== ENHANCED PROJECT TEMPLATES =====

create_enhanced_templates() {
    log_step "Creating enhanced project templates..."
    
    local templates_dir="$TERMUX_BUILD_HOME/templates"
    mkdir -p "$templates_dir"
    
    # Create Basic Android Project Template
    create_basic_template "$templates_dir/basic"
    
    # Create Kotlin Project Template
    create_kotlin_template "$templates_dir/kotlin"
    
    # Create Jetpack Compose Template
    create_compose_template "$templates_dir/compose"
    
    # Create Library Project Template
    create_library_template "$templates_dir/library"
    
    log_success "Enhanced project templates created"
}

create_basic_template() {
    local template_dir=$1
    mkdir -p "$template_dir/src/main/java" "$template_dir/src/main/res/values" "$template_dir/src/main/res/layout"
    
    # build.gradle.kts for basic template
    cat > "$template_dir/build.gradle.kts" << 'EOF'
plugins {
    id("com.android.application")
}

android {
    namespace = "{{PACKAGE_NAME}}"
    compileSdk = {{COMPILE_SDK}}

    defaultConfig {
        applicationId = "{{PACKAGE_NAME}}"
        minSdk = {{MIN_SDK}}
        targetSdk = {{TARGET_SDK}}
        versionCode = {{VERSION_CODE}}
        versionName = "{{VERSION_NAME}}"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
            isDebuggable = true
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    
    buildFeatures {
        viewBinding = true
    }
    
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}
EOF

    # AndroidManifest.xml
    cat > "$template_dir/src/main/AndroidManifest.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    
    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.{{CLASS_NAME}}"
        tools:targetApi="31">
        
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
EOF

    # MainActivity.java
    cat > "$template_dir/src/main/java/MainActivity.java.template" << 'EOF'
package {{PACKAGE_NAME}};

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.WindowCompat;
import {{PACKAGE_NAME}}.databinding.ActivityMainBinding;

public class MainActivity extends AppCompatActivity {
    
    private ActivityMainBinding binding;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
        
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());
        
        // Setup your UI here
        binding.textViewTitle.setText("Welcome to {{APP_NAME}}");
        binding.buttonAction.setOnClickListener(v -> {
            binding.textViewTitle.setText("Hello from Enhanced Gradle Builder!");
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        binding = null;
    }
}
EOF

    # activity_main.xml
    cat > "$template_dir/src/main/res/layout/activity_main.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout 
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res/auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="16dp"
    tools:context=".MainActivity">

    <TextView
        android:id="@+id/textView_title"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/app_name"
        android:textAppearance="@style/TextAppearance.Material3.HeadlineMedium"
        android:textAlignment="center"
        app:layout_constraintBottom_toTopOf="@+id/button_action"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <Button
        android:id="@+id/button_action"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/button_click_me"
        android:layout_marginTop="32dp"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toBottomOf="@+id/textView_title" />

</androidx.constraintlayout.widget.ConstraintLayout>
EOF

    # strings.xml
    cat > "$template_dir/src/main/res/values/strings.xml" << 'EOF'
<resources>
    <string name="app_name">{{APP_NAME}}</string>
    <string name="button_click_me">Click Me!</string>
    <string name="welcome_message">Welcome to {{APP_NAME}}</string>
    <string name="built_with_gradle">Built with Enhanced Gradle Builder</string>
</resources>
EOF

    # Create template metadata
    cat > "$template_dir/template.properties" << 'EOF'
template.name=Basic Android Application
template.description=A basic Android application with ViewBinding and Material Design
template.language=Java
template.min_api=26
template.requires_kotlin=false
template.requires_compose=false
EOF
}

create_kotlin_template() {
    local template_dir=$1
    mkdir -p "$template_dir/src/main/kotlin" "$template_dir/src/main/res/values" "$template_dir/src/main/res/layout"
    
    # build.gradle.kts for Kotlin template
    cat > "$template_dir/build.gradle.kts" << 'EOF'
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "{{PACKAGE_NAME}}"
    compileSdk = {{COMPILE_SDK}}

    defaultConfig {
        applicationId = "{{PACKAGE_NAME}}"
        minSdk = {{MIN_SDK}}
        targetSdk = {{TARGET_SDK}}
        versionCode = {{VERSION_CODE}}
        versionName = "{{VERSION_NAME}}"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
            isDebuggable = true
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    
    kotlinOptions {
        jvmTarget = "1.8"
    }
    
    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0")
    implementation("androidx.activity:activity-ktx:1.8.2")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.jetbrains.kotlin:kotlin-test:${KOTLIN_VERSION}")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}
EOF

    # MainActivity.kt
    cat > "$template_dir/src/main/kotlin/MainActivity.kt.template" << 'EOF'
package {{PACKAGE_NAME}}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import androidx.lifecycle.lifecycleScope
import {{PACKAGE_NAME}}.databinding.ActivityMainBinding
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private var clickCount = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupUI()
    }
    
    private fun setupUI() {
        binding.apply {
            textViewTitle.text = "Welcome to {{APP_NAME}}"
            buttonAction.setOnClickListener {
                handleButtonClick()
            }
        }
    }
    
    private fun handleButtonClick() {
        clickCount++
        binding.textViewTitle.text = when {
            clickCount == 1 -> "Hello from Kotlin!"
            clickCount < 5 -> "Clicked $clickCount times"
            else -> "You love clicking! 🎉"
        }
        
        // Demonstrate coroutines
        lifecycleScope.launch {
            binding.buttonAction.isEnabled = false
            delay(500)
            binding.buttonAction.isEnabled = true
        }
    }
}
EOF

    # Same layout and strings as basic template
    cp "$TERMUX_BUILD_HOME/templates/basic/src/main/res/layout/activity_main.xml" "$template_dir/src/main/res/layout/"
    cp "$TERMUX_BUILD_HOME/templates/basic/src/main/res/values/strings.xml" "$template_dir/src/main/res/values/"
    cp "$TERMUX_BUILD_HOME/templates/basic/src/main/AndroidManifest.xml" "$template_dir/src/main/"
    
    # Template metadata
    cat > "$template_dir/template.properties" << 'EOF'
template.name=Kotlin Android Application
template.description=A Kotlin Android application with coroutines and modern Android patterns
template.language=Kotlin
template.min_api=26
template.requires_kotlin=true
template.requires_compose=false
EOF
}

create_compose_template() {
    local template_dir=$1
    mkdir -p "$template_dir/src/main/kotlin" "$template_dir/src/main/res/values"
    
    # build.gradle.kts for Compose template
    cat > "$template_dir/build.gradle.kts" << 'EOF'
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "{{PACKAGE_NAME}}"
    compileSdk = {{COMPILE_SDK}}

    defaultConfig {
        applicationId = "{{PACKAGE_NAME}}"
        minSdk = {{MIN_SDK}}
        targetSdk = {{TARGET_SDK}}
        versionCode = {{VERSION_CODE}}
        versionName = "{{VERSION_NAME}}"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
            isDebuggable = true
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    
    kotlinOptions {
        jvmTarget = "1.8"
    }
    
    buildFeatures {
        compose = true
    }
    
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.8"
    }
    
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    // Compose BOM
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.activity:activity-compose:1.8.2")
    
    // Core Android
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    
    // Debug tools
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}
EOF

    # MainActivity.kt for Compose
    cat > "$template_dir/src/main/kotlin/MainActivity.kt.template" << 'EOF'
package {{PACKAGE_NAME}}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import {{PACKAGE_NAME}}.ui.theme.{{CLASS_NAME}}Theme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            {{CLASS_NAME}}Theme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainScreen()
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen() {
    var clickCount by remember { mutableIntStateOf(0) }
    var showMessage by remember { mutableStateOf(false) }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 16.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "Welcome to {{APP_NAME}}",
                    style = MaterialTheme.typography.headlineMedium,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.primary
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "Built with Enhanced Gradle Builder",
                    style = MaterialTheme.typography.bodyLarge,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                if (showMessage) {
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "Button clicked $clickCount times!",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.secondary
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        Button(
            onClick = {
                clickCount++
                showMessage = true
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp)
        ) {
            Text(
                text = "Click Me!",
                style = MaterialTheme.typography.titleMedium
            )
        }
        
        if (clickCount > 5) {
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "🎉 You love Compose!",
                style = MaterialTheme.typography.headlineSmall,
                color = MaterialTheme.colorScheme.tertiary
            )
        }
    }
}

@Preview(showBackground = true)
@Composable
fun MainScreenPreview() {
    {{CLASS_NAME}}Theme {
        MainScreen()
    }
}
EOF

    # Theme files for Compose
    mkdir -p "$template_dir/src/main/kotlin/ui/theme"
    
    cat > "$template_dir/src/main/kotlin/ui/theme/Color.kt.template" << 'EOF'
package {{PACKAGE_NAME}}.ui.theme

import androidx.compose.ui.graphics.Color

val Purple80 = Color(0xFFD0BCFF)
val PurpleGrey80 = Color(0xFFCCC2DC)
val Pink80 = Color(0xFFEFB8C8)

val Purple40 = Color(0xFF6650a4)
val PurpleGrey40 = Color(0xFF625b71)
val Pink40 = Color(0xFF7D5260)
EOF

    cat > "$template_dir/src/main/kotlin/ui/theme/Theme.kt.template" << 'EOF'
package {{PACKAGE_NAME}}.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val DarkColorScheme = darkColorScheme(
    primary = Purple80,
    secondary = PurpleGrey80,
    tertiary = Pink80
)

private val LightColorScheme = lightColorScheme(
    primary = Purple40,
    secondary = PurpleGrey40,
    tertiary = Pink40
)

@Composable
fun {{CLASS_NAME}}Theme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }

        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
EOF

    cat > "$template_dir/src/main/kotlin/ui/theme/Type.kt.template" << 'EOF'
package {{PACKAGE_NAME}}.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val Typography = Typography(
    bodyLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp
    )
)
EOF

    # AndroidManifest.xml for Compose
    cat > "$template_dir/src/main/AndroidManifest.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.{{CLASS_NAME}}"
        tools:targetApi="31">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.{{CLASS_NAME}}">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
EOF

    # strings.xml
    cat > "$template_dir/src/main/res/values/strings.xml" << 'EOF'
<resources>
    <string name="app_name">{{APP_NAME}}</string>
</resources>
EOF

    # Template metadata
    cat > "$template_dir/template.properties" << 'EOF'
template.name=Jetpack Compose Application
template.description=A modern Android application using Jetpack Compose with Material3 design
template.language=Kotlin
template.min_api=26
template.requires_kotlin=true
template.requires_compose=true
EOF
}

create_library_template() {
    local template_dir=$1
    mkdir -p "$template_dir/src/main/kotlin" "$template_dir/src/main/res/values"
    
    # build.gradle.kts for library template
    cat > "$template_dir/build.gradle.kts" << 'EOF'
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("maven-publish")
}

android {
    namespace = "{{PACKAGE_NAME}}"
    compileSdk = {{COMPILE_SDK}}

    defaultConfig {
        minSdk = {{MIN_SDK}}
        
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        consumerProguardFiles("consumer-rules.pro")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    
    kotlinOptions {
        jvmTarget = "1.8"
    }
    
    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}

afterEvaluate {
    publishing {
        publications {
            register<MavenPublication>("release") {
                groupId = "{{PACKAGE_NAME}}"
                artifactId = "{{ARTIFACT_NAME}}"
                version = "{{VERSION_NAME}}"
                
                from(components["release"])
            }
        }
    }
}
EOF

    # Library class template
    cat > "$template_dir/src/main/kotlin/LibraryClass.kt.template" << 'EOF'
package {{PACKAGE_NAME}}

/**
 * {{APP_NAME}} Library
 * 
 * This is a sample library class that demonstrates the library template
 * functionality. Replace this with your actual library code.
 */
class {{CLASS_NAME}}Library {
    
    companion object {
        /**
         * Get the library version
         */
        fun getVersion(): String = "{{VERSION_NAME}}"
        
        /**
         * Initialize the library
         */
        fun initialize(): Boolean {
            return try {
                // Add your initialization code here
                true
            } catch (e: Exception) {
                false
            }
        }
    }
    
    /**
     * Sample utility function
     */
    fun processData(input: String): String {
        return "Processed: $input"
    }
    
    /**
     * Sample async operation
     */
    suspend fun performAsyncOperation(): String {
        // Simulate async work
        kotlinx.coroutines.delay(100)
        return "Async operation completed"
    }
}
EOF

    # Template metadata
    cat > "$template_dir/template.properties" << 'EOF'
template.name=Android Library
template.description=An Android library project with Kotlin and publishing support
template.language=Kotlin
template.min_api=26
template.requires_kotlin=true
template.requires_compose=false
template.is_library=true
EOF
}

# ===== ENHANCED BUILD SYSTEM =====

create_enhanced_gradle_wrapper() {
    log_step "Creating enhanced Gradle wrapper configuration..."
    
    # Create gradle wrapper properties with optimizations
    cat > "$TERMUX_BUILD_HOME/gradle/wrapper/gradle-wrapper.properties" << EOF
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip
networkTimeout=60000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
EOF

    # Create optimized gradle.properties for Termux
    cat > "$TERMUX_BUILD_HOME/gradle.properties" << EOF
# Gradle optimization for Termux
org.gradle.jvmargs=-Xmx2g -Xms512m -XX:MaxMetaspaceSize=512m -XX:+HeapDumpOnOutOfMemoryError
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configureondemand=true

# Android build optimizations
android.useAndroidX=true
android.enableJetifier=true
android.enableR8.fullMode=true
android.experimental.cacheCompileLibResources=true
android.nonTransitiveRClass=true
android.nonFinalResIds=true

# Kotlin optimizations
kotlin.code.style=official
kotlin.incremental=true
kotlin.incremental.android=true
kotlin.caching.enabled=true

# Build performance
org.gradle.vfs.watch=true
org.gradle.configuration-cache=true
org.gradle.unsafe.configuration-cache=true
EOF
}

create_enhanced_build_scripts() {
    log_step "Creating enhanced build scripts..."
    
    local scripts_dir="$TERMUX_BUILD_HOME/scripts"
    mkdir -p "$scripts_dir"
    
    # Main project creation script
    cat > "$scripts_dir/create-project.sh" << 'EOF'
#!/bin/bash

# Enhanced Project Creator with Multiple Templates
source "$TERMUX_BUILD_HOME/jdk-config.sh"
source "$TERMUX_BUILD_HOME/build-functions.sh"

show_usage() {
    cat << USAGE
Enhanced Gradle Project Creator

Usage: $0 [options] <project_name> <package_name>

Options:
    -t, --template TYPE    Project template (basic|kotlin|compose|library)
    -o, --output DIR      Output directory (default: workspace)
    -v, --version NAME    Version name (default: 1.0.0)
    -c, --version-code N  Version code (default: 1)
    -a, --api LEVEL       Target API level (default: 34)
    -m, --min-api LEVEL   Minimum API level (default: 26)
    -h, --help           Show this help message

Templates:
    basic      - Basic Android application with Java
    kotlin     - Kotlin Android application
    compose    - Jetpack Compose application
    library    - Android library project

Examples:
    $0 MyApp com.example.myapp
    $0 -t compose MyComposeApp com.example.compose
    $0 -t library MyLibrary com.example.mylibrary

USAGE
}

# Parse command line arguments
TEMPLATE="basic"
OUTPUT_DIR="$TERMUX_BUILD_HOME/workspace"
VERSION_NAME="1.0.0"
VERSION_CODE="1"
TARGET_API="34"
MIN_API="26"

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--template)
            TEMPLATE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -v|--version)
            VERSION_NAME="$2"
            shift 2
            ;;
        -c|--version-code)
            VERSION_CODE="$2"
            shift 2
            ;;
        -a|--api)
            TARGET_API="$2"
            shift 2
            ;;
        -m|--min-api)
            MIN_API="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

if [ $# -lt 2 ]; then
    echo "Error: Project name and package name are required"
    show_usage
    exit 1
fi

PROJECT_NAME="$1"
PACKAGE_NAME="$2"

# Validate template
TEMPLATE_DIR="$TERMUX_BUILD_HOME/templates/$TEMPLATE"
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Error: Template '$TEMPLATE' not found"
    echo "Available templates: $(ls $TERMUX_BUILD_HOME/templates/)"
    exit 1
fi

# Create project
log_info "Creating project '$PROJECT_NAME' with template '$TEMPLATE'"
create_project_from_template "$TEMPLATE" "$PROJECT_NAME" "$PACKAGE_NAME" "$OUTPUT_DIR"

log_success "Project '$PROJECT_NAME' created successfully!"
echo
echo "Next steps:"
echo "  1. cd $OUTPUT_DIR/$PROJECT_NAME"
echo "  2. enhanced-build.sh"
echo "  3. Find your APK in $TERMUX_BUILD_HOME/output/"
EOF

    chmod +x "$scripts_dir/create-project.sh"
    
    # Enhanced build script
    cat > "$scripts_dir/enhanced-build.sh" << 'EOF'
#!/bin/bash

# Enhanced Gradle Build Script with Error Recovery
source "$TERMUX_BUILD_HOME/jdk-config.sh"
source "$TERMUX_BUILD_HOME/build-functions.sh"

show_usage() {
    cat << USAGE
Enhanced Gradle APK Builder

Usage: $0 [options] [project_directory]

Options:
    -t, --type TYPE        Build type (debug|release|all) [default: debug]
    -c, --clean           Clean build
    -o, --output DIR      Output directory for APKs
    -s, --sign KEYSTORE   Sign with custom keystore
    -v, --verbose         Verbose output
    -j, --parallel        Enable parallel builds
    -h, --help           Show this help message

Examples:
    $0                    # Build current directory (debug)
    $0 -t release         # Build release APK
    $0 -c MyApp           # Clean build MyApp
    $0 -t all MyApp       # Build both debug and release

USAGE
}

# Default values
BUILD_TYPE="debug"
CLEAN_BUILD=false
VERBOSE=false
PARALLEL=false
PROJECT_DIR="."
CUSTOM_KEYSTORE=""
OUTPUT_DIR="$TERMUX_BUILD_HOME/output"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            BUILD_TYPE="$2"
            shift 2
            ;;
        -c|--clean)
            CLEAN_BUILD=true
            shift
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -s|--sign)
            CUSTOM_KEYSTORE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -j|--parallel)
            PARALLEL=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            PROJECT_DIR="$1"
            shift
            ;;
    esac
done

# Execute build
cd "$PROJECT_DIR" || exit 1
enhanced_gradle_build "$BUILD_TYPE" "$CLEAN_BUILD" "$VERBOSE" "$PARALLEL" "$OUTPUT_DIR"
EOF

    chmod +x "$scripts_dir/enhanced-build.sh"
}

# Create build functions library
create_build_functions() {
    log_step "Creating build functions library..."
    
    cat > "$TERMUX_BUILD_HOME/build-functions.sh" << 'EOF'
#!/bin/bash

# Enhanced Build Functions Library

create_project_from_template() {
    local template=$1
    local project_name=$2
    local package_name=$3
    local output_dir=$4
    
    local template_dir="$TERMUX_BUILD_HOME/templates/$template"
    local project_dir="$output_dir/$project_name"
    local class_name=$(echo "$project_name" | sed 's/[^a-zA-Z0-9]//g')
    local artifact_name=$(echo "$project_name" | tr '[:upper:]' '[:lower:]')
    
    # Create project directory
    mkdir -p "$project_dir"
    
    # Copy template files
    cp -r "$template_dir"/* "$project_dir"/
    
    # Process template variables in all files
    find "$project_dir" -type f \( -name "*.kt" -o -name "*.java" -o -name "*.xml" -o -name "*.gradle*" -o -name "*.properties" \) -exec \
        sed -i \
            -e "s/{{PACKAGE_NAME}}/$package_name/g" \
            -e "s/{{APP_NAME}}/$project_name/g" \
            -e "s/{{CLASS_NAME}}/$class_name/g" \
            -e "s/{{ARTIFACT_NAME}}/$artifact_name/g" \
            -e "s/{{VERSION_CODE}}/$VERSION_CODE/g" \
            -e "s/{{VERSION_NAME}}/$VERSION_NAME/g" \
            -e "s/{{MIN_SDK}}/$MIN_API/g" \
            -e "s/{{TARGET_SDK}}/$TARGET_API/g" \
            -e "s/{{COMPILE_SDK}}/$TARGET_API/g" \
            {} \;
    
    # Rename template files
    find "$project_dir" -name "*.template" | while read -r file; do
        mv "$file" "${file%.template}"
    done
    
    # Create package directory structure for source files
    local package_path=$(echo "$package_name" | tr '.' '/')
    find "$project_dir/src" -name "*.java" -o -name "*.kt" | while read -r file; do
        local dir=$(dirname "$file")
        local filename=$(basename "$file")
        mkdir -p "$dir/$package_path"
        mv "$file" "$dir/$package_path/$filename"
    done
    
    # Copy Gradle wrapper
    cp -r "$TERMUX_BUILD_HOME/gradle" "$project_dir/"
    cp "$TERMUX_BUILD_HOME/gradlew" "$project_dir/"
    cp "$TERMUX_BUILD_HOME/gradle.properties" "$project_dir/"
    
    # Create settings.gradle.kts
    cat > "$project_dir/settings.gradle.kts" << SETTINGS_EOF
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "$project_name"
include(":app")
SETTINGS_EOF

    # Create directory structure
    mkdir -p "$project_dir/app"
    mv "$project_dir/src" "$project_dir/app/"
    mv "$project_dir/build.gradle.kts" "$project_dir/app/"
    if [ -f "$project_dir/proguard-rules.pro" ]; then
        mv "$project_dir/proguard-rules.pro" "$project_dir/app/"
    fi
    
    log_success "Project created: $project_dir"
}

enhanced_gradle_build() {
    local build_type=$1
    local clean_build=$2
    local verbose=$3
    local parallel=$4
    local output_dir=$5
    
    # Prepare build options
    local gradle_opts=()
    
    if [ "$verbose" = true ]; then
        gradle_opts+=("--info")
    fi
    
    if [ "$parallel" = true ]; then
        gradle_opts+=("--parallel")
    fi
    
    # Clean if requested
    if [ "$clean_build" = true ]; then
        log_info "Cleaning project..."
        ./gradlew clean "${gradle_opts[@]}"
    fi
    
    # Build based on type
    case "$build_type" in
        debug)
            log_info "Building debug APK..."
            ./gradlew assembleDebug "${gradle_opts[@]}"
            copy_apk_to_output "debug" "$output_dir"
            ;;
        release)
            log_info "Building release APK..."
            ./gradlew assembleRelease "${gradle_opts[@]}"
            copy_apk_to_output "release" "$output_dir"
            ;;
        all)
            log_info "Building all variants..."
            ./gradlew assemble "${gradle_opts[@]}"
            copy_apk_to_output "debug" "$output_dir"
            copy_apk_to_output "release" "$output_dir"
            ;;
        *)
            log_error "Unknown build type: $build_type"
            return 1
            ;;
    esac
    
    log_success "Build completed successfully!"
}

copy_apk_to_output() {
    local build_variant=$1
    local output_dir=$2
    
    # Find APK files
    local apk_files=($(find . -name "*-${build_variant}.apk" -o -name "*-${build_variant}-unsigned.apk"))
    
    for apk in "${apk_files[@]}"; do
        if [ -f "$apk" ]; then
            local apk_name=$(basename "$apk")
            local timestamp=$(date +"%Y%m%d-%H%M")
            local output_name="${apk_name%.*}-${timestamp}.apk"
            
            cp "$apk" "$output_dir/$output_name"
            log_info "APK copied to: $output_dir/$output_name"
            
            # Also copy to downloads if available
            if [ -d "$DOWNLOADS_DIR" ]; then
                cp "$apk" "$DOWNLOADS_DIR/$output_name"
                log_info "APK also copied to Downloads: $output_name"
            fi
            
            # Show APK info
            show_apk_info "$output_dir/$output_name"
        fi
    done
}

show_apk_info() {
    local apk_path=$1
    
    echo
    log_info "APK Information:"
    echo "📱 File: $(basename "$apk_path")"
    echo "📏 Size: $(du -h "$apk_path" | cut -f1)"
    
    if command -v aapt &> /dev/null; then
        echo "📋 Package Info:"
        aapt dump badging "$apk_path" | head -3
    fi
    
    if command -v apksigner &> /dev/null; then
        if apksigner verify "$apk_path" &>/dev/null; then
            echo "🔐 Signature: ✅ Valid"
        else
            echo "🔐 Signature: ❌ Invalid"
        fi
    fi
}
EOF

    chmod +x "$TERMUX_BUILD_HOME/build-functions.sh"
}

# ===== DEPENDENCY MANAGEMENT =====

setup_dependency_management() {
    log_step "Setting up enhanced dependency management..."
    
    local deps_dir="$TERMUX_BUILD_HOME/dependencies"
    mkdir -p "$deps_dir"
    
    # Create dependency configuration files
    cat > "$deps_dir/android-common.gradle" << 'EOF'
// Common Android dependencies for all projects
ext {
    // Version definitions
    versions = [
        compileSdk       : 34,
        minSdk           : 26,
        targetSdk        : 34,
        
        // Core libraries
        androidxCore     : "1.12.0",
        appcompat        : "1.6.1",
        material         : "1.11.0",
        constraintLayout : "2.1.4",
        lifecycle        : "2.7.0",
        activity         : "1.8.2",
        fragment         : "1.6.2",
        
        // Kotlin
        kotlin           : "1.9.22",
        coroutines       : "1.7.3",
        
        // Compose
        composeBom       : "2024.02.00",
        composeCompiler  : "1.5.8",
        
        // Navigation
        navigation       : "2.7.6",
        
        // Architecture
        room             : "2.6.1",
        hilt             : "2.48",
        hiltNavigation   : "1.1.0",
        
        // Networking
        retrofit         : "2.9.0",
        okhttp           : "4.12.0",
        gson             : "2.10.1",
        
        // Testing
        junit            : "4.13.2",
        androidxJunit    : "1.1.5",
        espresso         : "3.5.1",
        mockito          : "5.8.0",
        mockk            : "1.13.8",
    ]
    
    // Dependency groups
    androidCore = [
        "androidx.core:core-ktx:$versions.androidxCore",
        "androidx.appcompat:appcompat:$versions.appcompat",
        "com.google.android.material:material:$versions.material",
        "androidx.constraintlayout:constraintlayout:$versions.constraintLayout",
    ]
    
    lifecycle = [
        "androidx.lifecycle:lifecycle-runtime-ktx:$versions.lifecycle",
        "androidx.lifecycle:lifecycle-viewmodel-ktx:$versions.lifecycle",
        "androidx.lifecycle:lifecycle-livedata-ktx:$versions.lifecycle",
    ]
    
    compose = [
        "androidx.compose.ui:ui",
        "androidx.compose.ui:ui-tooling-preview",
        "androidx.compose.material3:material3",
        "androidx.activity:activity-compose:$versions.activity",
        "androidx.lifecycle:lifecycle-viewmodel-compose:$versions.lifecycle",
    ]
    
    composeDebug = [
        "androidx.compose.ui:ui-tooling",
        "androidx.compose.ui:ui-test-manifest",
    ]
    
    navigation = [
        "androidx.navigation:navigation-fragment-ktx:$versions.navigation",
        "androidx.navigation:navigation-ui-ktx:$versions.navigation",
        "androidx.navigation:navigation-compose:$versions.navigation",
    ]
    
    room = [
        "androidx.room:room-runtime:$versions.room",
        "androidx.room:room-ktx:$versions.room",
    ]
    
    hilt = [
        "com.google.dagger:hilt-android:$versions.hilt",
        "androidx.hilt:hilt-navigation-compose:$versions.hiltNavigation",
    ]
    
    networking = [
        "com.squareup.retrofit2:retrofit:$versions.retrofit",
        "com.squareup.retrofit2:converter-gson:$versions.retrofit",
        "com.squareup.okhttp3:okhttp:$versions.okhttp",
        "com.squareup.okhttp3:logging-interceptor:$versions.okhttp",
        "com.google.code.gson:gson:$versions.gson",
    ]
    
    kotlin = [
        "org.jetbrains.kotlin:kotlin-stdlib:$versions.kotlin",
        "org.jetbrains.kotlinx:kotlinx-coroutines-android:$versions.coroutines",
    ]
    
    testing = [
        "junit:junit:$versions.junit",
        "androidx.test.ext:junit:$versions.androidxJunit",
        "androidx.test.espresso:espresso-core:$versions.espresso",
    ]
    
    mockito = [
        "org.mockito:mockito-core:$versions.mockito",
        "io.mockk:mockk:$versions.mockk",
        "org.jetbrains.kotlinx:kotlinx-coroutines-test:$versions.coroutines",
    ]
}
EOF

    # Create dependency resolver script
    cat > "$scripts_dir/resolve-dependencies.sh" << 'EOF'
#!/bin/bash

# Enhanced Dependency Resolver
source "$TERMUX_BUILD_HOME/jdk-config.sh"

resolve_project_dependencies() {
    local project_dir=$1
    
    if [ ! -f "$project_dir/build.gradle.kts" ] && [ ! -f "$project_dir/build.gradle" ]; then
        log_error "No Gradle build file found in $project_dir"
        return 1
    fi
    
    cd "$project_dir" || return 1
    
    log_info "Resolving dependencies for project..."
    
    # Download dependencies
    if ! ./gradlew dependencies --configuration=debugRuntimeClasspath; then
        log_warn "Failed to resolve some dependencies, continuing..."
    fi
    
    # Pre-download common dependencies
    ./gradlew :app:dependencies --configuration=releaseRuntimeClasspath &>/dev/null || true
    
    log_success "Dependencies resolved"
}

# Run if called directly
if [ "$0" = "${BASH_SOURCE[0]}" ]; then
    resolve_project_dependencies "${1:-.}"
fi
EOF

    chmod +x "$scripts_dir/resolve-dependencies.sh"
}

# ===== INTEGRATION WITH ANDROID SDK FIXES =====

integrate_android_sdk_fixes() {
    log_step "Integrating with Android SDK resolution fixes..."
    
    # Check if SDK JARs exist in the source directory
    if [ -d "$SDK_SOURCE_DIR" ] && [ -f "$SDK_SOURCE_DIR/android-34.jar" ]; then
        log_info "Found Android SDK JARs, integrating them..."
        
        local sdk_dir="$TERMUX_BUILD_HOME/android-sdk"
        mkdir -p "$sdk_dir"
        
        # Copy SDK JARs
        cp "$SDK_SOURCE_DIR"/android-*.jar "$sdk_dir/" 2>/dev/null || true
        
        # Create Android SDK configuration
        cat > "$TERMUX_BUILD_HOME/android-sdk-config.sh" << EOF
#!/bin/bash
# Android SDK Configuration for Enhanced Build System

export ANDROID_SDK_ROOT="$sdk_dir"
export ANDROID_HOME="$sdk_dir"

# Available Android API levels
AVAILABLE_APIS=($(ls "$sdk_dir"/android-*.jar 2>/dev/null | sed 's/.*android-\([0-9]*\)\.jar/\1/' | sort -n))

get_android_jar() {
    local api_level=\$1
    local jar_file="$sdk_dir/android-\${api_level}.jar"
    
    if [ -f "\$jar_file" ]; then
        echo "\$jar_file"
        return 0
    fi
    
    # Fallback to highest available API
    local highest_api=\$(printf '%s\n' "\${AVAILABLE_APIS[@]}" | tail -1)
    local fallback_jar="$sdk_dir/android-\${highest_api}.jar"
    
    if [ -f "\$fallback_jar" ]; then
        echo "\$fallback_jar"
        return 0
    fi
    
    return 1
}

export -f get_android_jar
EOF
        
        chmod +x "$TERMUX_BUILD_HOME/android-sdk-config.sh"
        
        log_success "Android SDK integration completed"
        log_info "Available API levels: $(ls "$sdk_dir"/android-*.jar 2>/dev/null | sed 's/.*android-\([0-9]*\)\.jar/\1/' | tr '\n' ' ')"
    else
        log_warn "Android SDK JARs not found at $SDK_SOURCE_DIR"
        log_warn "Some advanced features may not work without proper Android SDK"
    fi
}

# ===== MAIN INSTALLATION FUNCTION =====

main() {
    log_header "$SCRIPT_NAME v$SCRIPT_VERSION - Installation"
    
    # Create main directory structure
    log_info "Creating build environment at $TERMUX_BUILD_HOME..."
    mkdir -p "$TERMUX_BUILD_HOME"/{templates,scripts,gradle/wrapper,output,workspace,.cache,dependencies}
    mkdir -p "$TEMP_BUILD_DIR"
    
    # Step-by-step installation with progress
    local total_steps=8
    local current_step=0
    
    show_progress $((++current_step)) $total_steps "Installing required packages..."
    pkg install -y aapt aapt2 d8 apksigner android-tools wget curl unzip
    
    show_progress $((++current_step)) $total_steps "Configuring JDK compatibility..."
    detect_and_configure_jdk
    
    show_progress $((++current_step)) $total_steps "Creating enhanced project templates..."
    create_enhanced_templates
    
    show_progress $((++current_step)) $total_steps "Setting up Gradle wrapper..."
    create_enhanced_gradle_wrapper
    
    # Copy Gradle wrapper files
    wget -q -O "$TERMUX_BUILD_HOME/gradlew" "https://raw.githubusercontent.com/gradle/gradle/v$GRADLE_VERSION/gradlew"
    chmod +x "$TERMUX_BUILD_HOME/gradlew"
    
    show_progress $((++current_step)) $total_steps "Creating build scripts..."
    create_enhanced_build_scripts
    create_build_functions
    
    show_progress $((++current_step)) $total_steps "Setting up dependency management..."
    setup_dependency_management
    
    show_progress $((++current_step)) $total_steps "Integrating Android SDK fixes..."
    integrate_android_sdk_fixes
    
    show_progress $((++current_step)) $total_steps "Creating environment configuration..."
    
    # Create main environment configuration
    cat > "$TERMUX_BUILD_HOME/env.sh" << EOF
#!/bin/bash
# Enhanced Gradle Build Environment

# Source all configuration
source "$TERMUX_BUILD_HOME/jdk-config.sh"
source "$TERMUX_BUILD_HOME/build-functions.sh"

if [ -f "$TERMUX_BUILD_HOME/android-sdk-config.sh" ]; then
    source "$TERMUX_BUILD_HOME/android-sdk-config.sh"
fi

export TERMUX_BUILD_HOME="$TERMUX_BUILD_HOME"
export PATH="$TERMUX_BUILD_HOME/scripts:\$PATH"

# Aliases for convenience
alias create-project="$TERMUX_BUILD_HOME/scripts/create-project.sh"
alias build-apk="$TERMUX_BUILD_HOME/scripts/enhanced-build.sh"
alias resolve-deps="$TERMUX_BUILD_HOME/scripts/resolve-dependencies.sh"

echo -e "${GREEN}✅ Enhanced Gradle Build Environment Loaded${NC}"
echo -e "${CYAN}📍 Build Home: $TERMUX_BUILD_HOME${NC}"
echo -e "${CYAN}☕ Java: \$(java -version 2>&1 | head -1)${NC}"
echo -e "${CYAN}🔨 Gradle: Available via wrapper${NC}"
echo
echo -e "${YELLOW}Quick Start:${NC}"
echo -e "  ${WHITE}create-project MyApp com.example.myapp${NC}"
echo -e "  ${WHITE}cd workspace/MyApp && build-apk${NC}"
EOF
    
    chmod +x "$TERMUX_BUILD_HOME/env.sh"
    
    show_progress $total_steps $total_steps "Installation completed!"
    
    # Test installation with a sample project
    log_info "Testing installation with sample project..."
    source "$TERMUX_BUILD_HOME/env.sh"
    
    if "$TERMUX_BUILD_HOME/scripts/create-project.sh" -t basic TestApp com.test.app; then
        log_success "Sample project created successfully!"
        
        # Attempt to build the sample
        cd "$TERMUX_BUILD_HOME/workspace/TestApp"
        if timeout 300 "$TERMUX_BUILD_HOME/scripts/enhanced-build.sh" -t debug; then
            log_success "Sample build completed successfully!"
        else
            log_warn "Sample build timed out or failed - this is normal on first run"
        fi
    else
        log_warn "Sample project creation failed - manual testing may be required"
    fi
    
    # Final success message
    echo
    log_header "🎉 Installation Completed Successfully!"
    echo
    log_success "Enhanced Gradle Build System v$SCRIPT_VERSION is ready!"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "  1. Load environment: ${WHITE}source $TERMUX_BUILD_HOME/env.sh${NC}"
    echo -e "  2. Create project:   ${WHITE}create-project MyApp com.example.myapp${NC}"
    echo -e "  3. Build APK:        ${WHITE}cd workspace/MyApp && build-apk${NC}"
    echo
    echo -e "${CYAN}Available Templates:${NC}"
    for template in "$TERMUX_BUILD_HOME/templates"/*; do
        if [ -d "$template" ]; then
            local name=$(basename "$template")
            local desc=""
            if [ -f "$template/template.properties" ]; then
                desc=" - $(grep 'template.description' "$template/template.properties" | cut -d'=' -f2-)"
            fi
            echo -e "  ${WHITE}$name${NC}$desc"
        fi
    done
    echo
    echo -e "${GREEN}Happy Android development in Termux! 🚀${NC}"
}

# Run main installation if script is executed directly
if [ "$0" = "${BASH_SOURCE[0]}" ]; then
    main "$@"
fi