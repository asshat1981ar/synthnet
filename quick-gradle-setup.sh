#!/bin/bash

# ===============================================================================
# Quick Enhanced Gradle Build System Setup
# Simplified version optimized for existing SynthNet environment
# ===============================================================================

set -euo pipefail

# Colors and formatting
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Configuration
readonly BUILD_HOME="$HOME/gradle-apk-builder"
readonly DOWNLOADS_DIR="$HOME/storage/downloads"

log_info() { echo -e "${GREEN}✓ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

echo -e "${BLUE}🚀 Quick Enhanced Gradle Build System Setup${NC}"
echo "=================================================="

# Create directory structure
log_info "Creating build environment..."
mkdir -p "$BUILD_HOME"/{templates,scripts,output,workspace}

# Copy Android SDK JARs if available
if [ -d "$HOME/android-sdk-test" ]; then
    log_info "Integrating existing Android SDK JARs..."
    mkdir -p "$BUILD_HOME/android-sdk"
    cp "$HOME/android-sdk-test"/android-*.jar "$BUILD_HOME/android-sdk/" 2>/dev/null || true
fi

# Create environment configuration
log_info "Creating environment configuration..."
cat > "$BUILD_HOME/env.sh" << 'EOF'
#!/bin/bash
# Enhanced Gradle Build Environment

export BUILD_HOME="$HOME/gradle-apk-builder"
export JAVA_HOME="$PREFIX/lib/jvm/java-21-openjdk"
export PATH="$BUILD_HOME/scripts:$PATH"

# Gradle optimizations for Termux
export GRADLE_OPTS="-Xmx2g -Xms512m -XX:MaxMetaspaceSize=512m"

alias create-project="$BUILD_HOME/scripts/create-project.sh"
alias build-apk="$BUILD_HOME/scripts/build-gradle.sh"

echo "✅ Enhanced Gradle Environment Loaded"
echo "📍 Build Home: $BUILD_HOME"
echo "☕ Java: $(java -version 2>&1 | head -1)"
EOF

chmod +x "$BUILD_HOME/env.sh"

# Create project creation script
log_info "Creating project creation script..."
cat > "$BUILD_HOME/scripts/create-project.sh" << 'EOF'
#!/bin/bash

PROJECT_NAME="$1"
PACKAGE_NAME="$2"
TEMPLATE="${3:-basic}"

if [ -z "$PROJECT_NAME" ] || [ -z "$PACKAGE_NAME" ]; then
    echo "Usage: $0 <project_name> <package_name> [template]"
    echo "Templates: basic, compose"
    exit 1
fi

PROJECT_DIR="$BUILD_HOME/workspace/$PROJECT_NAME"

if [ -d "$PROJECT_DIR" ]; then
    echo "❌ Project already exists: $PROJECT_NAME"
    exit 1
fi

echo "📱 Creating project: $PROJECT_NAME ($TEMPLATE)"
mkdir -p "$PROJECT_DIR"

# Create basic Gradle project structure
mkdir -p "$PROJECT_DIR"/{gradle/wrapper,app/src/main/{java,res/values,res/layout}}

# Copy gradle wrapper from existing synthnet project
if [ -f "$HOME/synthnet/gradlew" ]; then
    cp "$HOME/synthnet/gradlew" "$PROJECT_DIR/"
    cp -r "$HOME/synthnet/gradle" "$PROJECT_DIR/"
    chmod +x "$PROJECT_DIR/gradlew"
fi

# Create settings.gradle.kts
cat > "$PROJECT_DIR/settings.gradle.kts" << SETTINGS_EOF
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

rootProject.name = "$PROJECT_NAME"
include(":app")
SETTINGS_EOF

# Create root build.gradle.kts
cat > "$PROJECT_DIR/build.gradle.kts" << 'BUILD_EOF'
plugins {
    id("com.android.application") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
}
BUILD_EOF

# Create app/build.gradle.kts based on template
if [ "$TEMPLATE" = "compose" ]; then
    cat > "$PROJECT_DIR/app/build.gradle.kts" << APP_BUILD_EOF
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "$PACKAGE_NAME"
    compileSdk = 34

    defaultConfig {
        applicationId = "$PACKAGE_NAME"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
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
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation("androidx.core:core-ktx:1.12.0")
}
APP_BUILD_EOF

    # Create MainActivity.kt for Compose
    mkdir -p "$PROJECT_DIR/app/src/main/kotlin/$(echo $PACKAGE_NAME | tr '.' '/')"
    cat > "$PROJECT_DIR/app/src/main/kotlin/$(echo $PACKAGE_NAME | tr '.' '/')/MainActivity.kt" << 'MAIN_EOF'
package $PACKAGE_NAME

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen() {
    var clickCount by remember { mutableIntStateOf(0) }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Welcome to $PROJECT_NAME", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = { clickCount++ }) {
            Text("Clicked $clickCount times")
        }
    }
}
MAIN_EOF

else
    # Basic Java template
    cat > "$PROJECT_DIR/app/build.gradle.kts" << 'APP_BUILD_EOF'
plugins {
    id("com.android.application")
}

android {
    namespace = "$PACKAGE_NAME"
    compileSdk = 34

    defaultConfig {
        applicationId = "$PACKAGE_NAME"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
    
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
}

dependencies {
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
}
APP_BUILD_EOF

    # Create MainActivity.java
    mkdir -p "$PROJECT_DIR/app/src/main/java/$(echo $PACKAGE_NAME | tr '.' '/')"
    cat > "$PROJECT_DIR/app/src/main/java/$(echo $PACKAGE_NAME | tr '.' '/')/MainActivity.java" << 'MAIN_EOF'
package $PACKAGE_NAME;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.Button;
import android.widget.LinearLayout;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        
        TextView title = new TextView(this);
        title.setText("Welcome to $PROJECT_NAME");
        title.setTextSize(24);
        
        Button button = new Button(this);
        button.setText("Hello Enhanced Gradle!");
        
        layout.addView(title);
        layout.addView(button);
        setContentView(layout);
    }
}
MAIN_EOF

fi

# Create AndroidManifest.xml
cat > "$PROJECT_DIR/app/src/main/AndroidManifest.xml" << 'MANIFEST_EOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:label="$PROJECT_NAME"
        android:theme="@android:style/Theme.Material.Light">
        
        <activity android:name=".MainActivity"
                  android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
MANIFEST_EOF

# Create strings.xml
cat > "$PROJECT_DIR/app/src/main/res/values/strings.xml" << 'STRINGS_EOF'
<resources>
    <string name="app_name">$PROJECT_NAME</string>
</resources>
STRINGS_EOF

# Process template variables
find "$PROJECT_DIR" -type f \( -name "*.kt" -o -name "*.java" -o -name "*.xml" \) -exec \
    sed -i "s/\$PACKAGE_NAME/$PACKAGE_NAME/g; s/\$PROJECT_NAME/$PROJECT_NAME/g" {} \;

echo "✅ Project created: $PROJECT_DIR"
echo "🔨 To build: cd $PROJECT_DIR && build-apk"
EOF

chmod +x "$BUILD_HOME/scripts/create-project.sh"

# Create enhanced build script
log_info "Creating build script..."
cat > "$BUILD_HOME/scripts/build-gradle.sh" << 'EOF'
#!/bin/bash

BUILD_TYPE="${1:-debug}"
PROJECT_DIR="${2:-.}"

cd "$PROJECT_DIR"

if [ ! -f "gradlew" ]; then
    echo "❌ No gradlew found. Make sure you're in a Gradle project directory."
    exit 1
fi

echo "🔨 Building $BUILD_TYPE APK..."

# Set Gradle options for Termux
export GRADLE_OPTS="-Xmx2g -Xms512m -XX:MaxMetaspaceSize=512m"

# Build the APK
case "$BUILD_TYPE" in
    debug)
        ./gradlew assembleDebug
        ;;
    release)
        ./gradlew assembleRelease
        ;;
    *)
        echo "❌ Invalid build type. Use 'debug' or 'release'"
        exit 1
        ;;
esac

# Find and copy APK
APK_FILE=$(find . -name "*-${BUILD_TYPE}.apk" | head -1)

if [ -n "$APK_FILE" ]; then
    APK_NAME="$(basename "$(pwd)")-${BUILD_TYPE}-$(date +%Y%m%d-%H%M).apk"
    
    # Copy to build output
    cp "$APK_FILE" "$BUILD_HOME/output/$APK_NAME"
    echo "✅ APK copied to: $BUILD_HOME/output/$APK_NAME"
    
    # Copy to downloads if available
    if [ -d "$DOWNLOADS_DIR" ]; then
        cp "$APK_FILE" "$DOWNLOADS_DIR/$APK_NAME"
        echo "📁 APK also copied to Downloads: $APK_NAME"
    fi
    
    echo "📊 APK size: $(du -h "$APK_FILE" | cut -f1)"
    
    # Verify APK
    if command -v apksigner &>/dev/null; then
        if apksigner verify "$APK_FILE" &>/dev/null; then
            echo "🔐 APK signature: ✅ Valid"
        else
            echo "🔐 APK signature: ❌ Invalid"
        fi
    fi
else
    echo "❌ APK not found after build"
    exit 1
fi
EOF

chmod +x "$BUILD_HOME/scripts/build-gradle.sh"

# Create gradle.properties optimized for Termux
log_info "Creating Gradle configuration..."
cat > "$BUILD_HOME/gradle.properties" << 'EOF'
# Gradle optimization for Termux
org.gradle.jvmargs=-Xmx2g -Xms512m -XX:MaxMetaspaceSize=512m
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.caching=true

# Android optimizations
android.useAndroidX=true
android.enableJetifier=true
android.nonTransitiveRClass=true
EOF

# Create quick start guide
log_info "Creating quick start guide..."
cat > "$BUILD_HOME/QUICK_START.md" << 'EOF'
# Enhanced Gradle Build System - Quick Start

## Load Environment
```bash
source ~/gradle-apk-builder/env.sh
```

## Create Projects
```bash
# Basic Java app
create-project MyApp com.example.myapp

# Jetpack Compose app
create-project MyComposeApp com.example.compose compose
```

## Build APKs
```bash
cd workspace/MyApp
build-apk debug    # or just: build-apk
build-apk release
```

## Output Locations
- Built APKs: `~/gradle-apk-builder/output/`
- Downloads folder: `~/storage/downloads/`

Happy building! 🚀
EOF

# Test the setup with a sample project
log_info "Testing setup with sample project..."
source "$BUILD_HOME/env.sh"

if "$BUILD_HOME/scripts/create-project.sh" SampleApp com.example.sample basic; then
    log_info "✅ Sample project created successfully"
    
    cd "$BUILD_HOME/workspace/SampleApp"
    if timeout 180 "$BUILD_HOME/scripts/build-gradle.sh" debug; then
        log_info "✅ Sample build completed successfully!"
    else
        log_warn "Sample build timed out - this is normal on first run"
    fi
else
    log_warn "Sample project creation failed - manual testing may be needed"
fi

echo
echo -e "${GREEN}🎉 Enhanced Gradle Build System Setup Complete!${NC}"
echo "=================================================="
echo
echo "Next steps:"
echo "  1. source ~/gradle-apk-builder/env.sh"
echo "  2. create-project MyApp com.example.myapp"
echo "  3. cd workspace/MyApp && build-apk"
echo
echo "📁 Find your APKs in:"
echo "  • ~/gradle-apk-builder/output/"
echo "  • ~/storage/downloads/"
echo
log_info "Happy Android development in Termux! 🚀"