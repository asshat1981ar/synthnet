# Android Development MCP Server

A comprehensive Model Context Protocol (MCP) server designed specifically for Android software development. This server provides tools for project management, build automation, code generation, testing, and deployment.

## Features

### 🏗️ Project Management
- **create_android_project**: Create new Android projects with modern architecture (MVVM, Clean Architecture)
- **analyze_project**: Analyze project structure, dependencies, and security issues
- Support for Jetpack Compose and Hilt dependency injection

### 🔨 Build & Deployment
- **build_apk**: Build Android APKs with debug/release configurations
- **gradle_task**: Execute any Gradle task with custom arguments
- **install_apk**: Install APKs to connected devices
- **list_devices**: List all connected Android devices

### 🧩 Code Generation
- **generate_activity**: Create Activities with optional ViewModels and Compose UI
- **generate_fragment**: Generate Fragments with modern architecture patterns
- **generate_repository**: Create Repository pattern implementations with Room database
- **generate_test_class**: Generate comprehensive test classes

### 🧪 Testing & Quality
- **run_tests**: Execute unit and instrumentation tests with coverage
- **lint_check**: Run Android lint checks with configurable severity levels
- Automated code quality analysis and security scanning

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Start the MCP server:

```bash
python server.py
```

## Available Tools

### Project Creation
```json
{
  "name": "create_android_project",
  "arguments": {
    "project_name": "MyApp",
    "package_name": "com.example.myapp",
    "target_sdk": 34,
    "min_sdk": 21,
    "use_compose": true,
    "use_hilt": true,
    "project_type": "mvvm"
  }
}
```

### APK Building
```json
{
  "name": "build_apk",
  "arguments": {
    "project_path": "/path/to/project",
    "build_type": "debug",
    "output_path": "/output/directory",
    "sign_apk": true
  }
}
```

### Code Generation
```json
{
  "name": "generate_activity",
  "arguments": {
    "project_path": "/path/to/project",
    "activity_name": "UserProfileActivity",
    "package_name": "com.example.myapp",
    "use_compose": true,
    "include_viewmodel": true
  }
}
```

### Testing
```json
{
  "name": "run_tests",
  "arguments": {
    "project_path": "/path/to/project",
    "test_type": "all",
    "coverage": true
  }
}
```

## Architecture Support

### Project Types
- **basic**: Simple Activity-based structure
- **mvvm**: Model-View-ViewModel architecture with LiveData/StateFlow
- **clean_architecture**: Clean Architecture with Repository pattern and Use Cases

### Modern Android Features
- ✅ Jetpack Compose UI
- ✅ Hilt Dependency Injection  
- ✅ Room Database
- ✅ MVVM Architecture
- ✅ Coroutines & Flow
- ✅ Material 3 Design
- ✅ Unit & Integration Testing

## Integration with Development Workflow

This MCP server integrates seamlessly with:
- Android Studio projects
- Gradle build system
- ADB for device management
- Android SDK tools
- CI/CD pipelines

## Requirements

- Python 3.8+
- Android SDK
- Gradle
- ADB (Android Debug Bridge)
- MCP compatible client

## Contributing

This server is part of the SynthNet AI MCP ecosystem. Contributions and improvements are welcome.

## License

Part of the SynthNet AI project ecosystem.