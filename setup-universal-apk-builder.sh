#!/bin/bash

# Universal APK Build Environment Setup for Termux
# Based on lessons learned from SynthNet AI build process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Universal APK Build Environment Setup${NC}"
echo -e "${BLUE}===============================================${NC}"

# Set global variables
TERMUX_APK_HOME="$HOME/termux-apk-builder"
DOWNLOADS_DIR="$HOME/storage/downloads"

echo -e "${YELLOW}📍 Build environment will be created at: $TERMUX_APK_HOME${NC}"

# Create directory structure
echo -e "${GREEN}📁 Creating directory structure...${NC}"
mkdir -p "$TERMUX_APK_HOME"/{tools/{android-build-tools,sdk,keystores},templates,libs/{common,compose,networking,database},scripts,config/{build-profiles,signing,dependencies},workspace,output}

# Install required packages
echo -e "${GREEN}📦 Installing required packages...${NC}"
pkg install -y aapt aapt2 d8 apksigner android-tools openjdk-21 kotlin wget curl unzip

# Set up environment variables
echo -e "${GREEN}🔧 Setting up environment variables...${NC}"
cat > "$TERMUX_APK_HOME/env.sh" << 'EOF'
#!/bin/bash
# Universal APK Builder Environment Variables

export TERMUX_APK_HOME="$HOME/termux-apk-builder"
export JAVA_HOME="$PREFIX/lib/jvm/java-21-openjdk"
export ANDROID_HOME="$PREFIX"
export PATH="$TERMUX_APK_HOME/scripts:$PATH"

# Build configuration
export APK_DEFAULT_MIN_SDK="26"
export APK_DEFAULT_TARGET_SDK="34"
export APK_DEFAULT_COMPILE_SDK="34"

echo "✅ APK Builder environment loaded"
echo "📍 Build home: $TERMUX_APK_HOME"
echo "☕ Java version: $(java -version 2>&1 | head -1)"
echo "🔨 Build tools: $(which aapt2)"
EOF

chmod +x "$TERMUX_APK_HOME/env.sh"

# Download Android SDK JARs using Enhanced Downloader
echo -e "${GREEN}📥 Downloading Android SDK JARs with Enhanced Downloader...${NC}"

# Create enhanced downloader if it doesn't exist
ENHANCED_DOWNLOADER="$HOME/synthnet/enhanced-android-sdk-downloader.sh"
if [ ! -f "$ENHANCED_DOWNLOADER" ]; then
    echo -e "${RED}❌ Enhanced downloader not found at: $ENHANCED_DOWNLOADER${NC}"
    echo -e "${YELLOW}⚠️  Falling back to basic download method...${NC}"
    
    cd "$TERMUX_APK_HOME/tools/sdk/"
    for api in 28 29 30 31 32 33 34; do
        if [ ! -f "android-$api.jar" ]; then
            echo -e "${BLUE}  📱 Trying to download Android API $api...${NC}"
            # Try GitHub Sable repository as primary source
            if wget -q --timeout=60 "https://raw.githubusercontent.com/Sable/android-platforms/master/android-$api/android.jar" -O "android-$api.jar"; then
                echo -e "${GREEN}  ✅ Android API $api downloaded from GitHub${NC}"
            else
                echo -e "${RED}  ❌ Failed to download Android API $api${NC}"
                rm -f "android-$api.jar"
            fi
        else
            echo -e "${YELLOW}  ⏭️  Android API $api already exists${NC}"
        fi
    done
else
    echo -e "${GREEN}🔧 Using Enhanced Android SDK Downloader...${NC}"
    "$ENHANCED_DOWNLOADER" "$TERMUX_APK_HOME/tools/sdk/"
    
    # Verify at least API 34 was downloaded (most critical for modern builds)
    if [ ! -f "$TERMUX_APK_HOME/tools/sdk/android-34.jar" ]; then
        echo -e "${RED}❌ Critical: android-34.jar not available${NC}"
        echo -e "${YELLOW}⚠️  APK builds may fail without Android SDK JARs${NC}"
    else
        echo -e "${GREEN}✅ Android SDK JARs ready for builds${NC}"
    fi
fi

# Create debug keystore
echo -e "${GREEN}🔐 Creating debug keystore...${NC}"
if [ ! -f "$TERMUX_APK_HOME/tools/keystores/debug.keystore" ]; then
    keytool -genkey -v \
        -keystore "$TERMUX_APK_HOME/tools/keystores/debug.keystore" \
        -storepass android \
        -alias androiddebugkey \
        -keypass android \
        -keyalg RSA \
        -keysize 2048 \
        -validity 10000 \
        -dname "CN=Android Debug,O=Android,C=US"
    echo -e "${GREEN}✅ Debug keystore created${NC}"
else
    echo -e "${YELLOW}⏭️  Debug keystore already exists${NC}"
fi

# Create basic build script
echo -e "${GREEN}📜 Creating build scripts...${NC}"
cat > "$TERMUX_APK_HOME/scripts/build-apk.sh" << 'EOF'
#!/bin/bash

# Universal APK Builder Script
# Usage: build-apk.sh <project_name> [debug|release] [api_level]

source "$TERMUX_APK_HOME/env.sh"

PROJECT_NAME="$1"
BUILD_TYPE="${2:-debug}"
API_LEVEL="${3:-34}"

if [ -z "$PROJECT_NAME" ]; then
    echo "❌ Usage: build-apk.sh <project_name> [debug|release] [api_level]"
    exit 1
fi

PROJECT_DIR="$TERMUX_APK_HOME/workspace/$PROJECT_NAME"
BUILD_DIR="$PROJECT_DIR/build"
OUTPUT_APK="$TERMUX_APK_HOME/output/$PROJECT_NAME-$BUILD_TYPE-$(date +%Y%m%d).apk"
ANDROID_JAR="$TERMUX_APK_HOME/tools/sdk/android-$API_LEVEL.jar"

echo "🔨 Building $PROJECT_NAME ($BUILD_TYPE, API $API_LEVEL)"

# Verify project exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project not found: $PROJECT_DIR"
    exit 1
fi

# Verify Android JAR exists
if [ ! -f "$ANDROID_JAR" ]; then
    echo "❌ Android JAR not found: $ANDROID_JAR"
    exit 1
fi

# Clean build directory
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"/{classes,dex,resources}

echo "📦 Compiling resources..."
if [ -d "$PROJECT_DIR/res" ]; then
    aapt2 compile --dir "$PROJECT_DIR/res" -o "$BUILD_DIR/resources/compiled.zip"
    aapt2 link -o "$BUILD_DIR/app.ap_" \
        --manifest "$PROJECT_DIR/AndroidManifest.xml" \
        --java "$BUILD_DIR/classes" \
        -I "$ANDROID_JAR" \
        "$BUILD_DIR/resources/compiled.zip"
else
    # Create minimal APK with just manifest
    aapt package -f -M "$PROJECT_DIR/AndroidManifest.xml" \
        -I "$ANDROID_JAR" \
        -F "$BUILD_DIR/app.ap_"
fi

echo "☕ Compiling Java sources..."
java_files=$(find "$PROJECT_DIR/src" -name "*.java" 2>/dev/null || true)
if [ -n "$java_files" ]; then
    echo "$java_files" | xargs javac -cp "$ANDROID_JAR" -d "$BUILD_DIR/classes"
    
    echo "🔄 Converting to DEX..."
    d8 --lib "$ANDROID_JAR" --output "$BUILD_DIR/dex/" "$BUILD_DIR/classes"/*.class
else
    # Create minimal DEX for manifest-only APK
    echo 'public class MainActivity { public static void main(String[] args) {} }' > "$BUILD_DIR/MainActivity.java"
    javac -cp "$ANDROID_JAR" -d "$BUILD_DIR/classes" "$BUILD_DIR/MainActivity.java"
    d8 --lib "$ANDROID_JAR" --output "$BUILD_DIR/dex/" "$BUILD_DIR/classes"/*.class
fi

echo "📱 Packaging APK..."
cp "$BUILD_DIR/app.ap_" "$BUILD_DIR/unsigned.apk"
cd "$BUILD_DIR/dex"
zip -r "../unsigned.apk" classes.dex

echo "🔐 Signing APK..."
if [ "$BUILD_TYPE" = "release" ]; then
    if [ -f "$TERMUX_APK_HOME/tools/keystores/release.keystore" ]; then
        apksigner sign --ks "$TERMUX_APK_HOME/tools/keystores/release.keystore" \
                       --out "$OUTPUT_APK" \
                       "$BUILD_DIR/unsigned.apk"
    else
        echo "⚠️  Release keystore not found, using debug keystore"
        apksigner sign --ks "$TERMUX_APK_HOME/tools/keystores/debug.keystore" \
                       --ks-pass pass:android \
                       --out "$OUTPUT_APK" \
                       "$BUILD_DIR/unsigned.apk"
    fi
else
    apksigner sign --ks "$TERMUX_APK_HOME/tools/keystores/debug.keystore" \
                   --ks-pass pass:android \
                   --out "$OUTPUT_APK" \
                   "$BUILD_DIR/unsigned.apk"
fi

echo "✅ Verifying APK..."
apksigner verify "$OUTPUT_APK"

echo "🎉 Build complete!"
echo "📱 APK: $OUTPUT_APK"
echo "📏 Size: $(du -h "$OUTPUT_APK" | cut -f1)"

# Copy to downloads folder if it exists
if [ -d "$HOME/storage/downloads" ]; then
    cp "$OUTPUT_APK" "$HOME/storage/downloads/"
    echo "📁 APK copied to Downloads folder"
fi

# Show APK info
echo ""
echo "📋 APK Information:"
aapt dump badging "$OUTPUT_APK" | head -5
EOF

chmod +x "$TERMUX_APK_HOME/scripts/build-apk.sh"

# Create project template generator
cat > "$TERMUX_APK_HOME/scripts/create-project.sh" << 'EOF'
#!/bin/bash

# Project Template Generator
# Usage: create-project.sh <project_name> <package_name> [template_type]

source "$TERMUX_APK_HOME/env.sh"

PROJECT_NAME="$1"
PACKAGE_NAME="$2"
TEMPLATE_TYPE="${3:-basic}"

if [ -z "$PROJECT_NAME" ] || [ -z "$PACKAGE_NAME" ]; then
    echo "❌ Usage: create-project.sh <project_name> <package_name> [template_type]"
    echo "   Examples:"
    echo "     create-project.sh MyApp com.example.myapp"
    echo "     create-project.sh MyApp com.example.myapp basic"
    exit 1
fi

PROJECT_DIR="$TERMUX_APK_HOME/workspace/$PROJECT_NAME"

if [ -d "$PROJECT_DIR" ]; then
    echo "❌ Project already exists: $PROJECT_DIR"
    exit 1
fi

echo "📱 Creating project: $PROJECT_NAME"
echo "📦 Package: $PACKAGE_NAME"
echo "📋 Template: $TEMPLATE_TYPE"

# Create project structure
mkdir -p "$PROJECT_DIR"/{src,res/{drawable,values,layout}}

# Create AndroidManifest.xml
cat > "$PROJECT_DIR/AndroidManifest.xml" << MANIFEST_EOF
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="$PACKAGE_NAME"
    android:versionCode="1"
    android:versionName="1.0.0">

    <uses-sdk android:minSdkVersion="26" 
              android:targetSdkVersion="34" />
    
    <uses-permission android:name="android.permission.INTERNET" />
              
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

# Create MainActivity.java
mkdir -p "$PROJECT_DIR/src/$(echo $PACKAGE_NAME | tr '.' '/')"
cat > "$PROJECT_DIR/src/$(echo $PACKAGE_NAME | tr '.' '/')/MainActivity.java" << JAVA_EOF
package $PACKAGE_NAME;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.LinearLayout;
import android.view.Gravity;
import android.graphics.Color;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Create a simple layout programmatically
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setGravity(Gravity.CENTER);
        layout.setBackgroundColor(Color.WHITE);
        
        TextView titleView = new TextView(this);
        titleView.setText("$PROJECT_NAME");
        titleView.setTextSize(24);
        titleView.setTextColor(Color.BLACK);
        titleView.setGravity(Gravity.CENTER);
        
        TextView subtitleView = new TextView(this);
        subtitleView.setText("Built with Universal APK Builder");
        subtitleView.setTextSize(16);
        subtitleView.setTextColor(Color.GRAY);
        subtitleView.setGravity(Gravity.CENTER);
        
        layout.addView(titleView);
        layout.addView(subtitleView);
        
        setContentView(layout);
    }
}
JAVA_EOF

# Create strings.xml
cat > "$PROJECT_DIR/res/values/strings.xml" << STRINGS_EOF
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">$PROJECT_NAME</string>
    <string name="hello_world">Hello from $PROJECT_NAME!</string>
</resources>
STRINGS_EOF

echo "✅ Project $PROJECT_NAME created successfully!"
echo "📁 Location: $PROJECT_DIR"
echo ""
echo "🔨 To build the APK, run:"
echo "   build-apk.sh $PROJECT_NAME"
echo ""
echo "📱 To build and copy to Downloads:"
echo "   build-apk.sh $PROJECT_NAME debug"
EOF

chmod +x "$TERMUX_APK_HOME/scripts/create-project.sh"

# Create quick start guide
cat > "$TERMUX_APK_HOME/QUICK_START.md" << 'EOF'
# Universal APK Builder - Quick Start Guide

## 🚀 Getting Started

### Load Environment
```bash
source ~/termux-apk-builder/env.sh
```

### Create Your First App
```bash
# Create a new project
create-project.sh MyFirstApp com.example.myfirstapp

# Build the APK
build-apk.sh MyFirstApp

# Your APK will be in ~/termux-apk-builder/output/ and ~/storage/downloads/
```

### Available Commands
- `create-project.sh <name> <package>` - Create new project
- `build-apk.sh <project> [debug|release] [api]` - Build APK
- Check ~/termux-apk-builder/scripts/ for more tools

### Project Structure
```
workspace/
  MyProject/
    AndroidManifest.xml
    src/com/example/package/MainActivity.java
    res/values/strings.xml
    build/ (generated)
```

### Output Locations
- Built APKs: `~/termux-apk-builder/output/`
- Auto-copied to: `~/storage/downloads/` (for easy installation)

Happy building! 🎉
EOF

# Add environment loading to bashrc
echo -e "${GREEN}🔗 Adding environment to shell...${NC}"
if ! grep -q "termux-apk-builder" "$HOME/.bashrc" 2>/dev/null; then
    echo "" >> "$HOME/.bashrc"
    echo "# Universal APK Builder" >> "$HOME/.bashrc"
    echo "alias apk-env='source \$HOME/termux-apk-builder/env.sh'" >> "$HOME/.bashrc"
    echo "alias apk-build='source \$HOME/termux-apk-builder/env.sh && build-apk.sh'" >> "$HOME/.bashrc"
    echo "alias apk-create='source \$HOME/termux-apk-builder/env.sh && create-project.sh'" >> "$HOME/.bashrc"
fi

# Create a test project to verify installation
echo -e "${GREEN}🧪 Creating test project...${NC}"
source "$TERMUX_APK_HOME/env.sh"
"$TERMUX_APK_HOME/scripts/create-project.sh" TestApp com.termux.testapp basic

# Build the test project
echo -e "${GREEN}🔨 Building test APK...${NC}"
"$TERMUX_APK_HOME/scripts/build-apk.sh" TestApp debug

echo -e "${GREEN}✅ Universal APK Build Environment Setup Complete!${NC}"
echo -e "${BLUE}===============================================${NC}"
echo ""
echo -e "${YELLOW}🎯 Quick Start:${NC}"
echo -e "  1. Run: ${GREEN}apk-env${NC} (loads environment)"
echo -e "  2. Run: ${GREEN}apk-create MyApp com.example.myapp${NC}"
echo -e "  3. Run: ${GREEN}apk-build MyApp${NC}"
echo ""
echo -e "${YELLOW}📁 Locations:${NC}"
echo -e "  • Build environment: ${GREEN}$TERMUX_APK_HOME${NC}"
echo -e "  • Output APKs: ${GREEN}$TERMUX_APK_HOME/output/${NC}"
echo -e "  • Downloads: ${GREEN}$HOME/storage/downloads/${NC}"
echo ""
echo -e "${YELLOW}📖 Documentation:${NC}"
echo -e "  • Quick guide: ${GREEN}cat $TERMUX_APK_HOME/QUICK_START.md${NC}"
echo -e "  • Full plan: ${GREEN}cat $HOME/synthnet/UNIVERSAL_APK_BUILD_PLAN.md${NC}"
echo ""
echo -e "${GREEN}🎉 Happy Android building in Termux! 🚀${NC}"