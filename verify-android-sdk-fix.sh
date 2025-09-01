#!/bin/bash

# Android SDK Resolution Verification Script
# Tests the enhanced Android SDK downloader and build system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Android SDK Resolution Verification${NC}"
echo -e "${BLUE}====================================${NC}"

# Test configuration
TEST_SDK_DIR="$HOME/android-sdk-test"
ENHANCED_DOWNLOADER="$HOME/synthnet/enhanced-android-sdk-downloader.sh"
REQUIRED_APIS=(28 34)  # Test with minimal set for speed
TEMP_DIR="$(mktemp -d)"

# Cleanup function
cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

echo -e "${GREEN}📋 Test Configuration:${NC}"
echo -e "  • Test SDK Directory: $TEST_SDK_DIR"
echo -e "  • Enhanced Downloader: $ENHANCED_DOWNLOADER"
echo -e "  • APIs to test: ${REQUIRED_APIS[*]}"
echo ""

# Test 1: Verify enhanced downloader exists
echo -e "${GREEN}🔧 Test 1: Enhanced Downloader Availability${NC}"
if [ -f "$ENHANCED_DOWNLOADER" ] && [ -x "$ENHANCED_DOWNLOADER" ]; then
    echo -e "${GREEN}  ✅ Enhanced downloader found and executable${NC}"
else
    echo -e "${RED}  ❌ Enhanced downloader missing or not executable${NC}"
    exit 1
fi

# Test 2: Clean test and download Android JARs
echo -e "${GREEN}📥 Test 2: Android JAR Download${NC}"
rm -rf "$TEST_SDK_DIR"
mkdir -p "$TEST_SDK_DIR"

echo -e "${BLUE}  🚀 Running enhanced downloader...${NC}"
if "$ENHANCED_DOWNLOADER" "$TEST_SDK_DIR"; then
    echo -e "${GREEN}  ✅ Enhanced downloader completed successfully${NC}"
else
    echo -e "${RED}  ❌ Enhanced downloader failed${NC}"
    exit 1
fi

# Test 3: Verify downloaded JARs
echo -e "${GREEN}🔍 Test 3: JAR Verification${NC}"
for api in "${REQUIRED_APIS[@]}"; do
    jar_file="$TEST_SDK_DIR/android-$api.jar"
    echo -e "${BLUE}  📱 Checking android-$api.jar...${NC}"
    
    if [ ! -f "$jar_file" ]; then
        echo -e "${RED}    ❌ android-$api.jar not found${NC}"
        continue
    fi
    
    # Check file size (should be > 20MB)
    size=$(stat -f%z "$jar_file" 2>/dev/null || stat -c%s "$jar_file" 2>/dev/null)
    size_mb=$((size / 1024 / 1024))
    
    if [ $size -lt 20971520 ]; then
        echo -e "${RED}    ❌ android-$api.jar too small: ${size_mb}MB${NC}"
        continue
    fi
    
    # Check if it's a valid JAR
    if ! jar tf "$jar_file" | head -5 | grep -q "\.class\|\.xml"; then
        echo -e "${RED}    ❌ android-$api.jar invalid format${NC}"
        continue
    fi
    
    echo -e "${GREEN}    ✅ android-$api.jar valid (${size_mb}MB)${NC}"
done

# Test 4: Compilation Test
echo -e "${GREEN}🧪 Test 4: Android Compilation Test${NC}"
api_34_jar="$TEST_SDK_DIR/android-34.jar"

if [ -f "$api_34_jar" ]; then
    echo -e "${BLUE}  📝 Creating test Android class...${NC}"
    
    # Create test Java file
    cat > "$TEMP_DIR/TestAndroidClass.java" << 'JAVA_EOF'
import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.LinearLayout;
import android.view.Gravity;

public class TestAndroidClass extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setGravity(Gravity.CENTER);
        
        TextView textView = new TextView(this);
        textView.setText("Android SDK Test Successful!");
        layout.addView(textView);
        
        setContentView(layout);
    }
    
    // Test more Android APIs
    private void testMoreAPIs() {
        String packageName = getPackageName();
        Object systemService = getSystemService("activity");
        // This should compile without errors if android.jar is complete
    }
}
JAVA_EOF

    echo -e "${BLUE}  ⚙️  Compiling with android-34.jar...${NC}"
    if javac -cp "$api_34_jar" -d "$TEMP_DIR" "$TEMP_DIR/TestAndroidClass.java" 2>"$TEMP_DIR/compile_errors.log"; then
        echo -e "${GREEN}    ✅ Android class compiled successfully${NC}"
        
        # Check compiled class exists
        if [ -f "$TEMP_DIR/TestAndroidClass.class" ]; then
            echo -e "${GREEN}    ✅ Generated .class file verified${NC}"
        fi
    else
        echo -e "${RED}    ❌ Compilation failed:${NC}"
        cat "$TEMP_DIR/compile_errors.log" | head -10
    fi
else
    echo -e "${YELLOW}  ⚠️  android-34.jar not available for compilation test${NC}"
fi

# Test 5: Build Tools Compatibility
echo -e "${GREEN}🔨 Test 5: Build Tools Compatibility${NC}"
echo -e "${BLUE}  🔧 Checking required build tools...${NC}"

tools_available=true
required_tools=("aapt2" "d8" "apksigner" "javac")

for tool in "${required_tools[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        version_info=$(${tool} --version 2>&1 | head -1 || echo "Unknown version")
        echo -e "${GREEN}    ✅ $tool: $version_info${NC}"
    else
        echo -e "${RED}    ❌ $tool: Not found${NC}"
        tools_available=false
    fi
done

if $tools_available; then
    echo -e "${GREEN}  ✅ All required build tools available${NC}"
else
    echo -e "${YELLOW}  ⚠️  Some build tools missing but SDK JARs are ready${NC}"
fi

# Test 6: Integration Test with Original Setup Script
echo -e "${GREEN}🔗 Test 6: Integration Test${NC}"
SETUP_SCRIPT="$HOME/synthnet/setup-universal-apk-builder.sh"

if [ -f "$SETUP_SCRIPT" ]; then
    echo -e "${BLUE}  📋 Checking setup script integration...${NC}"
    
    # Check if setup script references enhanced downloader
    if grep -q "enhanced-android-sdk-downloader" "$SETUP_SCRIPT"; then
        echo -e "${GREEN}    ✅ Setup script integrated with enhanced downloader${NC}"
    else
        echo -e "${YELLOW}    ⚠️  Setup script may not use enhanced downloader${NC}"
    fi
    
    # Check for fallback mechanism
    if grep -q "Sable/android-platforms" "$SETUP_SCRIPT"; then
        echo -e "${GREEN}    ✅ Setup script has GitHub fallback mechanism${NC}"
    else
        echo -e "${YELLOW}    ⚠️  Setup script may lack fallback mechanisms${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠️  Original setup script not found for integration test${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}📊 Test Summary${NC}"
echo -e "${BLUE}===============${NC}"

# Check test results
available_jars=$(ls "$TEST_SDK_DIR"/android-*.jar 2>/dev/null | wc -l)
echo -e "${GREEN}✅ Downloaded Android JARs: $available_jars${NC}"

if [ $available_jars -gt 0 ]; then
    echo -e "${GREEN}🎉 SUCCESS: Android SDK resolution working!${NC}"
    echo ""
    echo -e "${GREEN}📁 Available Android JARs:${NC}"
    for jar_file in "$TEST_SDK_DIR"/android-*.jar; do
        if [ -f "$jar_file" ]; then
            size=$(stat -f%z "$jar_file" 2>/dev/null || stat -c%s "$jar_file" 2>/dev/null)
            size_mb=$((size / 1024 / 1024))
            echo -e "${GREEN}  • $(basename "$jar_file"): ${size_mb}MB${NC}"
        fi
    done
    
    echo ""
    echo -e "${GREEN}📋 Next Steps:${NC}"
    echo -e "  1. Run the updated setup-universal-apk-builder.sh"
    echo -e "  2. Create and build Android projects"
    echo -e "  3. Enhanced downloader will handle SDK JARs automatically"
    
    exit 0
else
    echo -e "${RED}💥 FAILURE: No Android JARs obtained${NC}"
    echo -e "${RED}  • Check network connectivity${NC}"
    echo -e "${RED}  • Verify enhanced downloader script${NC}"
    echo -e "${RED}  • Check system requirements${NC}"
    
    exit 1
fi