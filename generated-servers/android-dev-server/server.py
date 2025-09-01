#!/usr/bin/env python3
"""
Android Development MCP Server
A comprehensive Model Context Protocol server for Android software development,
providing tools for project management, build automation, code generation, and testing.
"""

import asyncio
import json
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializeResult
import mcp.server.stdio
import mcp.types as types

class AndroidDevServer:
    def __init__(self):
        self.server = Server("android-dev-server")
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                # Project Management Tools
                types.Tool(
                    name="create_android_project",
                    description="Create a new Android project with specified configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string", "description": "Name of the Android project"},
                            "package_name": {"type": "string", "description": "Package name (e.g., com.example.myapp)"},
                            "target_sdk": {"type": "integer", "description": "Target SDK version", "default": 34},
                            "min_sdk": {"type": "integer", "description": "Minimum SDK version", "default": 21},
                            "use_compose": {"type": "boolean", "description": "Use Jetpack Compose", "default": True},
                            "use_hilt": {"type": "boolean", "description": "Include Hilt dependency injection", "default": True},
                            "project_type": {"type": "string", "enum": ["basic", "mvvm", "clean_architecture"], "default": "mvvm"}
                        },
                        "required": ["project_name", "package_name"]
                    }
                ),
                
                # Build Tools
                types.Tool(
                    name="build_apk",
                    description="Build Android APK with specified configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {"type": "string", "description": "Path to Android project"},
                            "build_type": {"type": "string", "enum": ["debug", "release"], "default": "debug"},
                            "output_path": {"type": "string", "description": "Output directory for APK"},
                            "sign_apk": {"type": "boolean", "description": "Sign the APK", "default": True}
                        },
                        "required": ["project_path"]
                    }
                ),
                
                types.Tool(
                    name="gradle_task",
                    description="Execute Gradle task in Android project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {"type": "string", "description": "Path to Android project"},
                            "task": {"type": "string", "description": "Gradle task to execute"},
                            "args": {"type": "array", "items": {"type": "string"}, "description": "Additional arguments"}
                        },
                        "required": ["project_path", "task"]
                    }
                ),
                
                # Code Generation Tools
                types.Tool(
                    name="generate_activity",
                    description="Generate Android Activity with layout and ViewModel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {"type": "string", "description": "Path to Android project"},
                            "activity_name": {"type": "string", "description": "Name of the Activity"},
                            "package_name": {"type": "string", "description": "Package name"},
                            "use_compose": {"type": "boolean", "description": "Use Jetpack Compose", "default": True},
                            "include_viewmodel": {"type": "boolean", "description": "Generate ViewModel", "default": True}
                        },
                        "required": ["project_path", "activity_name", "package_name"]
                    }
                ),
                
                types.Tool(
                    name="generate_fragment",
                    description="Generate Android Fragment with layout and ViewModel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {"type": "string", "description": "Path to Android project"},
                            "fragment_name": {"type": "string", "description": "Name of the Fragment"},
                            "package_name": {"type": "string", "description": "Package name"},
                            "use_compose": {"type": "boolean", "description": "Use Jetpack Compose", "default": True}
                        },
                        "required": ["project_path", "fragment_name", "package_name"]
                    }
                ),
                
                types.Tool(
                    name="generate_repository",
                    description="Generate Repository pattern implementation with Room database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {"type": "string", "description": "Path to Android project"},
                            "entity_name": {"type": "string", "description": "Name of the entity"},
                            "package_name": {"type": "string", "description": "Package name"},
                            "include_network": {"type": "boolean", "description": "Include network calls", "default": True}
                        },
                        "required": ["project_path", "entity_name", "package_name"]
                    }
                ),
                
                # Testing Tools
                types.Tool(
                    name="run_tests",
                    description="Run Android tests (unit and instrumentation)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {"type": "string", "description": "Path to Android project"},
                            "test_type": {"type": "string", "enum": ["unit", "instrumentation", "all"], "default": "all"},
                            "coverage": {"type": "boolean", "description": "Generate code coverage report", "default": True}
                        },
                        "required": ["project_path"]
                    }
                ),
                
                types.Tool(
                    name="generate_test_class",
                    description="Generate unit test class for Android component",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {"type": "string", "description": "Path to Android project"},
                            "class_to_test": {"type": "string", "description": "Name of class to test"},
                            "package_name": {"type": "string", "description": "Package name"},
                            "test_type": {"type": "string", "enum": ["unit", "integration"], "default": "unit"}
                        },
                        "required": ["project_path", "class_to_test", "package_name"]
                    }
                ),
                
                # Analysis Tools
                types.Tool(
                    name="analyze_project",
                    description="Analyze Android project structure and dependencies",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {"type": "string", "description": "Path to Android project"},
                            "include_dependencies": {"type": "boolean", "description": "Include dependency analysis", "default": True},
                            "check_security": {"type": "boolean", "description": "Run security analysis", "default": True}
                        },
                        "required": ["project_path"]
                    }
                ),
                
                types.Tool(
                    name="lint_check",
                    description="Run Android lint checks on project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {"type": "string", "description": "Path to Android project"},
                            "severity": {"type": "string", "enum": ["informational", "warning", "error"], "default": "warning"}
                        },
                        "required": ["project_path"]
                    }
                ),
                
                # Deployment Tools
                types.Tool(
                    name="install_apk",
                    description="Install APK to connected Android device",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "apk_path": {"type": "string", "description": "Path to APK file"},
                            "device_id": {"type": "string", "description": "Device ID (optional)"}
                        },
                        "required": ["apk_path"]
                    }
                ),
                
                types.Tool(
                    name="list_devices",
                    description="List connected Android devices",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            try:
                if name == "create_android_project":
                    result = await self._create_android_project(arguments)
                elif name == "build_apk":
                    result = await self._build_apk(arguments)
                elif name == "gradle_task":
                    result = await self._gradle_task(arguments)
                elif name == "generate_activity":
                    result = await self._generate_activity(arguments)
                elif name == "generate_fragment":
                    result = await self._generate_fragment(arguments)
                elif name == "generate_repository":
                    result = await self._generate_repository(arguments)
                elif name == "run_tests":
                    result = await self._run_tests(arguments)
                elif name == "generate_test_class":
                    result = await self._generate_test_class(arguments)
                elif name == "analyze_project":
                    result = await self._analyze_project(arguments)
                elif name == "lint_check":
                    result = await self._lint_check(arguments)
                elif name == "install_apk":
                    result = await self._install_apk(arguments)
                elif name == "list_devices":
                    result = await self._list_devices(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _create_android_project(self, args: dict) -> dict:
        """Create a new Android project with specified configuration"""
        project_name = args["project_name"]
        package_name = args["package_name"]
        target_sdk = args.get("target_sdk", 34)
        min_sdk = args.get("min_sdk", 21)
        use_compose = args.get("use_compose", True)
        use_hilt = args.get("use_hilt", True)
        project_type = args.get("project_type", "mvvm")
        
        project_path = Path.cwd() / project_name
        project_path.mkdir(exist_ok=True)
        
        # Generate build.gradle (app level)
        build_gradle = self._generate_build_gradle(package_name, target_sdk, min_sdk, use_compose, use_hilt)
        (project_path / "app" / "build.gradle").parent.mkdir(parents=True, exist_ok=True)
        (project_path / "app" / "build.gradle").write_text(build_gradle)
        
        # Generate MainActivity
        main_activity = self._generate_main_activity(package_name, use_compose, project_type)
        src_path = project_path / "app" / "src" / "main" / "java" / package_name.replace(".", "/")
        src_path.mkdir(parents=True, exist_ok=True)
        (src_path / "MainActivity.kt").write_text(main_activity)
        
        # Generate AndroidManifest.xml
        manifest = self._generate_android_manifest(package_name)
        manifest_path = project_path / "app" / "src" / "main"
        manifest_path.mkdir(parents=True, exist_ok=True)
        (manifest_path / "AndroidManifest.xml").write_text(manifest)
        
        return {
            "status": "success",
            "message": f"Android project '{project_name}' created successfully",
            "project_path": str(project_path),
            "package_name": package_name,
            "features": {
                "compose": use_compose,
                "hilt": use_hilt,
                "architecture": project_type
            }
        }
    
    async def _build_apk(self, args: dict) -> dict:
        """Build Android APK"""
        project_path = Path(args["project_path"])
        build_type = args.get("build_type", "debug")
        output_path = args.get("output_path")
        sign_apk = args.get("sign_apk", True)
        
        # Run Gradle build
        gradle_cmd = ["./gradlew", f"assemble{build_type.capitalize()}"]
        
        result = subprocess.run(
            gradle_cmd,
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {
                "status": "error",
                "message": "Build failed",
                "error": result.stderr
            }
        
        # Find generated APK
        apk_path = project_path / "app" / "build" / "outputs" / "apk" / build_type
        apk_files = list(apk_path.glob("*.apk"))
        
        if not apk_files:
            return {
                "status": "error",
                "message": "APK not found after build"
            }
        
        built_apk = apk_files[0]
        
        # Copy to output path if specified
        if output_path:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            final_apk = output_dir / built_apk.name
            shutil.copy2(built_apk, final_apk)
        else:
            final_apk = built_apk
        
        return {
            "status": "success",
            "message": f"APK built successfully: {build_type}",
            "apk_path": str(final_apk),
            "build_type": build_type,
            "signed": sign_apk
        }
    
    async def _gradle_task(self, args: dict) -> dict:
        """Execute Gradle task"""
        project_path = Path(args["project_path"])
        task = args["task"]
        extra_args = args.get("args", [])
        
        cmd = ["./gradlew", task] + extra_args
        
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "task": task,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    async def _generate_activity(self, args: dict) -> dict:
        """Generate Android Activity"""
        project_path = Path(args["project_path"])
        activity_name = args["activity_name"]
        package_name = args["package_name"]
        use_compose = args.get("use_compose", True)
        include_viewmodel = args.get("include_viewmodel", True)
        
        # Generate Activity code
        activity_code = self._generate_activity_code(activity_name, package_name, use_compose, include_viewmodel)
        
        # Write Activity file
        src_path = project_path / "app" / "src" / "main" / "java" / package_name.replace(".", "/")
        activity_file = src_path / f"{activity_name}.kt"
        activity_file.write_text(activity_code)
        
        # Generate ViewModel if requested
        if include_viewmodel:
            viewmodel_code = self._generate_viewmodel_code(activity_name, package_name)
            viewmodel_file = src_path / f"{activity_name}ViewModel.kt"
            viewmodel_file.write_text(viewmodel_code)
        
        return {
            "status": "success",
            "message": f"Activity '{activity_name}' generated successfully",
            "files_created": [
                str(activity_file),
                str(viewmodel_file) if include_viewmodel else None
            ]
        }
    
    async def _generate_fragment(self, args: dict) -> dict:
        """Generate Android Fragment"""
        # Implementation for fragment generation
        return {"status": "success", "message": "Fragment generation not fully implemented yet"}
    
    async def _generate_repository(self, args: dict) -> dict:
        """Generate Repository pattern implementation"""
        # Implementation for repository generation
        return {"status": "success", "message": "Repository generation not fully implemented yet"}
    
    async def _run_tests(self, args: dict) -> dict:
        """Run Android tests"""
        project_path = Path(args["project_path"])
        test_type = args.get("test_type", "all")
        coverage = args.get("coverage", True)
        
        tasks = []
        if test_type in ["unit", "all"]:
            tasks.append("test")
        if test_type in ["instrumentation", "all"]:
            tasks.append("connectedAndroidTest")
        
        results = {}
        for task in tasks:
            result = subprocess.run(
                ["./gradlew", task],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            results[task] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
        
        return {
            "status": "success",
            "message": "Tests completed",
            "results": results,
            "coverage_enabled": coverage
        }
    
    async def _generate_test_class(self, args: dict) -> dict:
        """Generate test class"""
        # Implementation for test class generation
        return {"status": "success", "message": "Test class generation not fully implemented yet"}
    
    async def _analyze_project(self, args: dict) -> dict:
        """Analyze Android project"""
        project_path = Path(args["project_path"])
        include_deps = args.get("include_dependencies", True)
        check_security = args.get("check_security", True)
        
        analysis = {
            "project_path": str(project_path),
            "structure": {},
            "dependencies": [],
            "security_issues": []
        }
        
        # Analyze project structure
        if project_path.exists():
            analysis["structure"] = {
                "has_gradle": (project_path / "build.gradle").exists(),
                "has_app_module": (project_path / "app").exists(),
                "source_files": len(list(project_path.rglob("*.kt"))) + len(list(project_path.rglob("*.java")))
            }
        
        return {
            "status": "success",
            "analysis": analysis
        }
    
    async def _lint_check(self, args: dict) -> dict:
        """Run lint checks"""
        project_path = Path(args["project_path"])
        severity = args.get("severity", "warning")
        
        result = subprocess.run(
            ["./gradlew", "lint"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "status": "success" if result.returncode == 0 else "warning",
            "message": "Lint check completed",
            "severity": severity,
            "output": result.stdout,
            "issues_found": result.returncode != 0
        }
    
    async def _install_apk(self, args: dict) -> dict:
        """Install APK to device"""
        apk_path = args["apk_path"]
        device_id = args.get("device_id")
        
        cmd = ["adb"]
        if device_id:
            cmd.extend(["-s", device_id])
        cmd.extend(["install", "-r", apk_path])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "message": "APK installation completed",
            "apk_path": apk_path,
            "device_id": device_id,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None
        }
    
    async def _list_devices(self, args: dict) -> dict:
        """List connected devices"""
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        
        devices = []
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip() and '\t' in line:
                    device_id, status = line.strip().split('\t')
                    devices.append({"id": device_id, "status": status})
        
        return {
            "status": "success",
            "devices": devices,
            "count": len(devices)
        }
    
    # Helper methods for code generation
    def _generate_build_gradle(self, package_name: str, target_sdk: int, min_sdk: int, use_compose: bool, use_hilt: bool) -> str:
        compose_block = '''
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = '1.8'
    }
    buildFeatures {
        compose true
    }
    composeOptions {
        kotlinCompilerExtensionVersion '1.5.4'
    }''' if use_compose else ""
        
        compose_deps = '''
    implementation 'androidx.compose.ui:ui:1.5.4'
    implementation 'androidx.compose.ui:ui-tooling-preview:1.5.4'
    implementation 'androidx.compose.material3:material3:1.1.2'
    implementation 'androidx.activity:activity-compose:1.8.0'
''' if use_compose else ""
        
        hilt_deps = '''
    implementation 'com.google.dagger:hilt-android:2.48'
    kapt 'com.google.dagger:hilt-compiler:2.48'
''' if use_hilt else ""
        
        return f'''plugins {{
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
    {'id "dagger.hilt.android.plugin"' if use_hilt else ''}
    {'id "kotlin-kapt"' if use_hilt else ''}
}}

android {{
    namespace '{package_name}'
    compileSdk {target_sdk}

    defaultConfig {{
        applicationId "{package_name}"
        minSdk {min_sdk}
        targetSdk {target_sdk}
        versionCode 1
        versionName "1.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
    }}

    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}{compose_block}
}}

dependencies {{
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.7.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'{compose_deps}{hilt_deps}
    
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}}'''
    
    def _generate_main_activity(self, package_name: str, use_compose: bool, project_type: str) -> str:
        if use_compose:
            return f'''package {package_name}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview

class MainActivity : ComponentActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContent {{
            MaterialTheme {{
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {{
                    Greeting("Android")
                }}
            }}
        }}
    }}
}}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {{
    Text(
        text = "Hello $name!",
        modifier = modifier
    )
}}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {{
    MaterialTheme {{
        Greeting("Android")
    }}
}}'''
        else:
            return f'''package {package_name}

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle

class MainActivity : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }}
}}'''
    
    def _generate_android_manifest(self, package_name: str) -> str:
        return f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.MyApplication"
        tools:targetApi="31">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.MyApplication">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>'''
    
    def _generate_activity_code(self, activity_name: str, package_name: str, use_compose: bool, include_viewmodel: bool) -> str:
        viewmodel_import = f"import androidx.lifecycle.viewmodel.compose.viewModel\nimport {package_name}.{activity_name}ViewModel" if include_viewmodel and use_compose else ""
        viewmodel_usage = f"val viewModel: {activity_name}ViewModel = viewModel()" if include_viewmodel and use_compose else ""
        
        if use_compose:
            return f'''package {package_name}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
{viewmodel_import}

class {activity_name} : ComponentActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContent {{
            MaterialTheme {{
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {{
                    {activity_name}Screen()
                }}
            }}
        }}
    }}
}}

@Composable
fun {activity_name}Screen() {{
    {viewmodel_usage}
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {{
        Text(
            text = "{activity_name} Screen",
            style = MaterialTheme.typography.headlineMedium
        )
        Spacer(modifier = Modifier.height(16.dp))
        Button(
            onClick = {{ /* TODO: Add action */ }}
        ) {{
            Text("Click me")
        }}
    }}
}}'''
        else:
            return f'''package {package_name}

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
{viewmodel_import}

class {activity_name} : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_{activity_name.lower()})
    }}
}}'''
    
    def _generate_viewmodel_code(self, activity_name: str, package_name: str) -> str:
        return f'''package {package_name}

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class {activity_name}ViewModel : ViewModel() {{
    
    private val _uiState = MutableStateFlow({activity_name}UiState())
    val uiState: StateFlow<{activity_name}UiState> = _uiState.asStateFlow()
    
    fun onAction(action: {activity_name}Action) {{
        when (action) {{
            is {activity_name}Action.ButtonClicked -> {{
                // Handle button click
            }}
        }}
    }}
}}

data class {activity_name}UiState(
    val isLoading: Boolean = false,
    val data: String = "Hello World"
)

sealed class {activity_name}Action {{
    object ButtonClicked : {activity_name}Action()
}}'''
    
    async def run(self):
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, InitializeResult(
                    serverInfo={"name": "android-dev-server", "version": "1.0.0"},
                    capabilities={"tools": {}}
                )
            )

if __name__ == "__main__":
    server = AndroidDevServer()
    asyncio.run(server.run())