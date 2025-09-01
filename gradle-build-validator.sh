#!/bin/bash

# ===============================================================================
# Gradle Build Environment Validator and Testing Suite
# Production-Ready Testing and Validation for Enhanced Gradle Build System
# ===============================================================================

set -euo pipefail

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

readonly VALIDATOR_VERSION="1.0.0"
readonly TERMUX_BUILD_HOME="$HOME/gradle-apk-builder"

# Logging functions
log_header() {
    echo -e "${BLUE}${BOLD}$1${NC}"
    echo -e "${BLUE}$(printf '=%.0s' {1..60})${NC}"
}

log_info() {
    echo -e "${CYAN}ℹ  $1${NC}"
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

log_test() {
    echo -e "${PURPLE}🧪 $1${NC}"
}

# Test result tracking
declare -i TOTAL_TESTS=0
declare -i PASSED_TESTS=0
declare -i FAILED_TESTS=0
declare -a FAILED_TEST_NAMES=()

# Test framework functions
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    ((TOTAL_TESTS++))
    log_test "Running: $test_name"
    
    if $test_function; then
        log_success "PASS: $test_name"
        ((PASSED_TESTS++))
        return 0
    else
        log_error "FAIL: $test_name"
        ((FAILED_TESTS++))
        FAILED_TEST_NAMES+=("$test_name")
        return 1
    fi
}

# ===== ENVIRONMENT VALIDATION TESTS =====

test_termux_environment() {
    # Check if we're running in Termux
    [ -n "${TERMUX_VERSION:-}" ] || [ -d "/data/data/com.termux" ]
}

test_required_packages() {
    local required_packages=(
        "aapt"
        "aapt2" 
        "d8"
        "apksigner"
        "java"
        "wget"
        "curl"
        "unzip"
    )
    
    for package in "${required_packages[@]}"; do
        if ! command -v "$package" &> /dev/null; then
            log_error "Required package not found: $package"
            return 1
        fi
    done
    
    return 0
}

test_java_installation() {
    if ! command -v java &> /dev/null; then
        return 1
    fi
    
    local java_version=$(java -version 2>&1 | head -1 | grep -oP '(?<=version ")\d+' || echo "unknown")
    
    if [ "$java_version" = "unknown" ]; then
        return 1
    fi
    
    # Check if Java version is supported (8, 11, 17, or 21)
    case "$java_version" in
        8|11|17|21)
            log_info "Java $java_version detected"
            return 0
            ;;
        *)
            log_warn "Java $java_version may not be fully compatible"
            return 0  # Don't fail, just warn
            ;;
    esac
}

test_build_environment_structure() {
    local required_dirs=(
        "$TERMUX_BUILD_HOME"
        "$TERMUX_BUILD_HOME/templates"
        "$TERMUX_BUILD_HOME/scripts"
        "$TERMUX_BUILD_HOME/output"
        "$TERMUX_BUILD_HOME/workspace"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            log_error "Required directory missing: $dir"
            return 1
        fi
    done
    
    return 0
}

test_gradle_wrapper() {
    if [ ! -f "$TERMUX_BUILD_HOME/gradlew" ]; then
        return 1
    fi
    
    if [ ! -x "$TERMUX_BUILD_HOME/gradlew" ]; then
        return 1
    fi
    
    return 0
}

test_templates_availability() {
    local required_templates=(
        "basic"
        "kotlin"
        "compose"
        "library"
    )
    
    for template in "${required_templates[@]}"; do
        if [ ! -d "$TERMUX_BUILD_HOME/templates/$template" ]; then
            log_error "Template missing: $template"
            return 1
        fi
        
        # Check if template has required metadata
        if [ ! -f "$TERMUX_BUILD_HOME/templates/$template/template.properties" ]; then
            log_error "Template metadata missing: $template/template.properties"
            return 1
        fi
    done
    
    return 0
}

test_build_scripts() {
    local required_scripts=(
        "create-project.sh"
        "enhanced-build.sh"
        "resolve-dependencies.sh"
    )
    
    for script in "${required_scripts[@]}"; do
        local script_path="$TERMUX_BUILD_HOME/scripts/$script"
        if [ ! -f "$script_path" ]; then
            log_error "Build script missing: $script"
            return 1
        fi
        
        if [ ! -x "$script_path" ]; then
            log_error "Build script not executable: $script"
            return 1
        fi
    done
    
    return 0
}

# ===== FUNCTIONAL VALIDATION TESTS =====

test_project_creation_basic() {
    local test_project="ValidatorTestBasic"
    local test_package="com.test.validator.basic"
    local workspace="$TERMUX_BUILD_HOME/workspace"
    
    # Clean up any existing test project
    rm -rf "$workspace/$test_project"
    
    # Create project
    if ! "$TERMUX_BUILD_HOME/scripts/create-project.sh" -t basic "$test_project" "$test_package" &>/dev/null; then
        return 1
    fi
    
    # Verify project structure
    local project_dir="$workspace/$test_project"
    if [ ! -d "$project_dir" ]; then
        return 1
    fi
    
    if [ ! -f "$project_dir/app/build.gradle.kts" ]; then
        return 1
    fi
    
    if [ ! -f "$project_dir/app/src/main/AndroidManifest.xml" ]; then
        return 1
    fi
    
    # Clean up
    rm -rf "$project_dir"
    
    return 0
}

test_project_creation_kotlin() {
    local test_project="ValidatorTestKotlin"
    local test_package="com.test.validator.kotlin"
    local workspace="$TERMUX_BUILD_HOME/workspace"
    
    # Clean up any existing test project
    rm -rf "$workspace/$test_project"
    
    # Create project
    if ! "$TERMUX_BUILD_HOME/scripts/create-project.sh" -t kotlin "$test_project" "$test_package" &>/dev/null; then
        return 1
    fi
    
    # Verify Kotlin-specific files
    local project_dir="$workspace/$test_project"
    if [ ! -f "$project_dir/app/src/main/kotlin/com/test/validator/kotlin/MainActivity.kt" ]; then
        return 1
    fi
    
    # Clean up
    rm -rf "$project_dir"
    
    return 0
}

test_project_creation_compose() {
    local test_project="ValidatorTestCompose"
    local test_package="com.test.validator.compose"
    local workspace="$TERMUX_BUILD_HOME/workspace"
    
    # Clean up any existing test project
    rm -rf "$workspace/$test_project"
    
    # Create project
    if ! "$TERMUX_BUILD_HOME/scripts/create-project.sh" -t compose "$test_project" "$test_package" &>/dev/null; then
        return 1
    fi
    
    # Verify Compose-specific files
    local project_dir="$workspace/$test_project"
    if [ ! -f "$project_dir/app/src/main/kotlin/com/test/validator/compose/MainActivity.kt" ]; then
        return 1
    fi
    
    if [ ! -d "$project_dir/app/src/main/kotlin/com/test/validator/compose/ui" ]; then
        return 1
    fi
    
    # Clean up
    rm -rf "$project_dir"
    
    return 0
}

test_gradle_build_basic() {
    local test_project="ValidatorBuildTest"
    local test_package="com.test.validator.build"
    local workspace="$TERMUX_BUILD_HOME/workspace"
    local project_dir="$workspace/$test_project"
    
    # Clean up any existing test project
    rm -rf "$project_dir"
    
    # Create a minimal project
    if ! "$TERMUX_BUILD_HOME/scripts/create-project.sh" -t basic "$test_project" "$test_package" &>/dev/null; then
        return 1
    fi
    
    # Try to build (with timeout to prevent hanging)
    cd "$project_dir" || return 1
    
    # Test Gradle wrapper works
    if ! timeout 60 ./gradlew --version &>/dev/null; then
        cd - &>/dev/null
        rm -rf "$project_dir"
        return 1
    fi
    
    # Test dependency resolution
    if ! timeout 120 ./gradlew dependencies --configuration=debugRuntimeClasspath &>/dev/null; then
        cd - &>/dev/null
        rm -rf "$project_dir"
        return 1
    fi
    
    cd - &>/dev/null
    rm -rf "$project_dir"
    
    return 0
}

test_android_sdk_integration() {
    # Check if Android SDK JARs are available
    local android_sdk_dir="$TERMUX_BUILD_HOME/android-sdk"
    
    if [ ! -d "$android_sdk_dir" ]; then
        # Check fallback location
        android_sdk_dir="$HOME/android-sdk-test"
        if [ ! -d "$android_sdk_dir" ]; then
            log_warn "Android SDK directory not found - some features may be limited"
            return 0  # Don't fail, just warn
        fi
    fi
    
    # Check for at least one API level
    if ! ls "$android_sdk_dir"/android-*.jar &>/dev/null; then
        log_warn "No Android API JAR files found - APK builds may fail"
        return 0  # Don't fail, just warn
    fi
    
    return 0
}

test_apk_signing_capability() {
    # Check if apksigner is available and working
    if ! command -v apksigner &>/dev/null; then
        return 1
    fi
    
    # Try to verify apksigner help (basic functionality test)
    if ! apksigner --help &>/dev/null; then
        return 1
    fi
    
    return 0
}

test_build_tools_integration() {
    # Test each Android build tool
    local build_tools=(
        "aapt"
        "aapt2"
        "d8"
    )
    
    for tool in "${build_tools[@]}"; do
        if ! command -v "$tool" &>/dev/null; then
            log_error "Build tool not available: $tool"
            return 1
        fi
        
        # Basic functionality test
        case "$tool" in
            aapt|aapt2)
                if ! $tool --help &>/dev/null && ! $tool version &>/dev/null; then
                    log_error "Build tool not working: $tool"
                    return 1
                fi
                ;;
            d8)
                if ! $tool --help &>/dev/null; then
                    log_error "Build tool not working: $tool"
                    return 1
                fi
                ;;
        esac
    done
    
    return 0
}

# ===== PERFORMANCE VALIDATION TESTS =====

test_memory_requirements() {
    # Check available memory
    local available_mem=$(free -m | awk '/^Mem:/{print $7}' || echo "unknown")
    
    if [ "$available_mem" = "unknown" ]; then
        log_warn "Cannot determine available memory"
        return 0
    fi
    
    # Recommend at least 1GB available for builds
    if [ "$available_mem" -lt 1024 ]; then
        log_warn "Low memory detected ($available_mem MB). Builds may be slow or fail."
        log_info "Consider freeing memory before large builds"
    fi
    
    return 0
}

test_storage_requirements() {
    # Check available storage in build directory
    local available_space=$(df -BM "$TERMUX_BUILD_HOME" | tail -1 | awk '{print $4}' | sed 's/M//')
    
    if [ "$available_space" -lt 1024 ]; then
        log_warn "Low storage space detected ($available_space MB)"
        log_info "Consider cleaning up before creating large projects"
    fi
    
    return 0
}

# ===== COMPREHENSIVE VALIDATION SUITE =====

run_environment_validation() {
    log_header "Environment Validation Tests"
    
    run_test "Termux Environment Detection" test_termux_environment
    run_test "Required Packages Available" test_required_packages
    run_test "Java Installation" test_java_installation
    run_test "Build Environment Structure" test_build_environment_structure
    run_test "Gradle Wrapper" test_gradle_wrapper
    run_test "Project Templates" test_templates_availability
    run_test "Build Scripts" test_build_scripts
    
    echo
}

run_functional_validation() {
    log_header "Functional Validation Tests"
    
    run_test "Basic Project Creation" test_project_creation_basic
    run_test "Kotlin Project Creation" test_project_creation_kotlin
    run_test "Compose Project Creation" test_project_creation_compose
    run_test "Gradle Build System" test_gradle_build_basic
    run_test "Android SDK Integration" test_android_sdk_integration
    run_test "APK Signing Capability" test_apk_signing_capability
    run_test "Build Tools Integration" test_build_tools_integration
    
    echo
}

run_performance_validation() {
    log_header "Performance Validation Tests"
    
    run_test "Memory Requirements" test_memory_requirements
    run_test "Storage Requirements" test_storage_requirements
    
    echo
}

# ===== DIAGNOSTIC FUNCTIONS =====

show_system_info() {
    log_header "System Information"
    
    echo -e "${CYAN}Environment:${NC}"
    echo "  OS: $(uname -o) $(uname -r)"
    echo "  Architecture: $(uname -m)"
    echo "  Shell: $SHELL"
    
    if [ -n "${TERMUX_VERSION:-}" ]; then
        echo "  Termux Version: $TERMUX_VERSION"
    fi
    
    echo
    echo -e "${CYAN}Java Environment:${NC}"
    if command -v java &>/dev/null; then
        java -version 2>&1 | head -3 | sed 's/^/  /'
        echo "  JAVA_HOME: ${JAVA_HOME:-not set}"
    else
        echo "  Java: Not installed"
    fi
    
    echo
    echo -e "${CYAN}Memory and Storage:${NC}"
    if command -v free &>/dev/null; then
        echo "  Memory:"
        free -h | sed 's/^/    /'
    fi
    
    echo "  Storage (Build Home):"
    df -h "$TERMUX_BUILD_HOME" 2>/dev/null | tail -1 | sed 's/^/    /' || echo "    Unable to check"
    
    echo
    echo -e "${CYAN}Build Environment:${NC}"
    echo "  Build Home: $TERMUX_BUILD_HOME"
    echo "  Templates: $(ls -1 "$TERMUX_BUILD_HOME/templates" 2>/dev/null | wc -l) available"
    echo "  Workspace: $(ls -1 "$TERMUX_BUILD_HOME/workspace" 2>/dev/null | wc -l) projects"
    echo "  Output APKs: $(ls -1 "$TERMUX_BUILD_HOME/output"/*.apk 2>/dev/null | wc -l) files"
    
    echo
}

show_validation_report() {
    log_header "Validation Report"
    
    echo -e "${WHITE}Total Tests: $TOTAL_TESTS${NC}"
    echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
    echo -e "${RED}Failed: $FAILED_TESTS${NC}"
    
    if [ $FAILED_TESTS -gt 0 ]; then
        echo
        echo -e "${RED}Failed Tests:${NC}"
        for test_name in "${FAILED_TEST_NAMES[@]}"; do
            echo -e "  ${RED}❌ $test_name${NC}"
        done
    fi
    
    echo
    
    local success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    if [ $success_rate -ge 90 ]; then
        log_success "Validation Score: $success_rate% - Excellent! 🎉"
    elif [ $success_rate -ge 75 ]; then
        log_info "Validation Score: $success_rate% - Good, some issues to address"
    elif [ $success_rate -ge 50 ]; then
        log_warn "Validation Score: $success_rate% - Several issues need attention"
    else
        log_error "Validation Score: $success_rate% - Major issues require fixing"
    fi
    
    echo
}

show_usage() {
    cat << USAGE
Enhanced Gradle Build Environment Validator v$VALIDATOR_VERSION

Usage: $0 [options]

Options:
    -e, --environment     Run environment validation tests only
    -f, --functional      Run functional validation tests only  
    -p, --performance     Run performance validation tests only
    -a, --all            Run all validation tests (default)
    -s, --system-info    Show system information
    -q, --quick          Run quick validation (essential tests only)
    -v, --verbose        Verbose output
    -h, --help           Show this help message

Examples:
    $0                   # Run all tests
    $0 --environment     # Test environment setup only
    $0 --quick           # Quick validation
    $0 --system-info     # Show system information

USAGE
}

# ===== MAIN FUNCTION =====

main() {
    local run_environment=false
    local run_functional=false
    local run_performance=false
    local run_all=true
    local show_system=false
    local quick_mode=false
    local verbose=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                run_environment=true
                run_all=false
                shift
                ;;
            -f|--functional)
                run_functional=true
                run_all=false
                shift
                ;;
            -p|--performance)
                run_performance=true
                run_all=false
                shift
                ;;
            -a|--all)
                run_all=true
                shift
                ;;
            -s|--system-info)
                show_system=true
                shift
                ;;
            -q|--quick)
                quick_mode=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    log_header "Enhanced Gradle Build Environment Validator v$VALIDATOR_VERSION"
    echo
    
    if [ "$show_system" = true ]; then
        show_system_info
    fi
    
    # Run validation tests
    if [ "$run_all" = true ]; then
        run_environment_validation
        run_functional_validation
        run_performance_validation
    else
        if [ "$run_environment" = true ]; then
            run_environment_validation
        fi
        
        if [ "$run_functional" = true ]; then
            run_functional_validation
        fi
        
        if [ "$run_performance" = true ]; then
            run_performance_validation
        fi
    fi
    
    # Quick mode runs only essential tests
    if [ "$quick_mode" = true ]; then
        log_header "Quick Validation Mode"
        run_test "Environment Setup" test_build_environment_structure
        run_test "Required Tools" test_required_packages
        run_test "Java Available" test_java_installation
        run_test "Templates Available" test_templates_availability
        echo
    fi
    
    show_validation_report
    
    # Exit with appropriate code
    if [ $FAILED_TESTS -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function if script is executed directly
if [ "$0" = "${BASH_SOURCE[0]}" ]; then
    main "$@"
fi