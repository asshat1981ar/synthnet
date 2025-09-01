#!/usr/bin/env python3
"""
Continuous Workflow Status Generator
Comprehensive status report of the active FORGE-enhanced continuous workflow
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import os

def generate_comprehensive_status():
    print("📊 FORGE-ENHANCED CONTINUOUS WORKFLOW STATUS REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    synthnet_path = Path("/data/data/com.termux/files/home/synthnet")
    android_project = synthnet_path / "SynthNetAI"
    forge_output = synthnet_path / "forge_continuous_output"
    
    # 1. System Overview
    print("🚀 SYSTEM OVERVIEW")
    print("-" * 40)
    
    # Check if workflow is running
    try:
        result = subprocess.run(["pgrep", "-f", "forge_enhanced_continuous_workflow"], 
                              capture_output=True, text=True)
        workflow_running = result.returncode == 0
        if workflow_running:
            pid = result.stdout.strip().split('\n')[0] if result.stdout.strip() else "Unknown"
            print(f"✅ FORGE Workflow Status: ACTIVE (PID: {pid})")
        else:
            print("⚠️ FORGE Workflow Status: NOT RUNNING")
    except:
        print("❓ FORGE Workflow Status: UNKNOWN")
    
    # System uptime estimation
    if forge_output.exists():
        oldest_file = min(forge_output.rglob("*"), key=lambda x: x.stat().st_mtime, default=None)
        if oldest_file:
            uptime = datetime.now() - datetime.fromtimestamp(oldest_file.stat().st_mtime)
            print(f"⏰ Estimated Uptime: {uptime}")
    
    print()
    
    # 2. FORGE Pipeline Status
    print("🔥 FORGE PIPELINE STATUS")
    print("-" * 40)
    
    if (forge_output / "forge_health.json").exists():
        try:
            health_data = json.loads((forge_output / "forge_health.json").read_text())
            system_status = health_data.get("system_status", "unknown").upper()
            print(f"🏥 System Health: {system_status}")
            print()
            
            print("📈 Pipeline Performance:")
            for phase, pipeline in health_data.get("pipelines", {}).items():
                success_rate = pipeline.get("success_rate", 0)
                last_exec = pipeline.get("last_execution")
                
                status_icon = "✅" if success_rate > 70 else "⚠️" if success_rate > 30 else "❌"
                print(f"  {status_icon} {phase.title()}: {success_rate:.1f}% success")
                
                if last_exec:
                    exec_time = datetime.fromisoformat(last_exec.replace('Z', '+00:00'))
                    print(f"     Last executed: {exec_time.strftime('%H:%M:%S')}")
                else:
                    print(f"     Last executed: Never")
        except:
            print("❌ Unable to read health data")
    else:
        print("⚠️ No health data available")
    
    print()
    
    # 3. Cycle Analysis
    print("🔄 CYCLE ANALYSIS")
    print("-" * 40)
    
    cycle_files = sorted(forge_output.glob("forge_cycle_*.json"))
    if cycle_files:
        print(f"📊 Total Cycles Completed: {len(cycle_files)}")
        
        # Latest cycle analysis
        latest_cycle_file = cycle_files[-1]
        try:
            cycle_data = json.loads(latest_cycle_file.read_text())
            
            print(f"🆕 Latest Cycle: #{cycle_data.get('cycle', 'Unknown')}")
            print(f"   Timestamp: {cycle_data.get('timestamp', 'Unknown')}")
            print(f"   Patches Applied: {cycle_data.get('patches_applied', 0)}")
            print(f"   Total Patches: {cycle_data.get('total_patches', 0)}")
            
            pipeline_results = cycle_data.get('pipeline_results', {})
            if pipeline_results:
                print("   Pipeline Results:")
                for phase, success_rate in pipeline_results.items():
                    print(f"     • {phase.title()}: {success_rate:.1f}%")
        except:
            print("❌ Unable to read latest cycle data")
            
        # Cycle frequency analysis
        if len(cycle_files) >= 2:
            try:
                first_cycle = json.loads(cycle_files[0].read_text())
                last_cycle = json.loads(cycle_files[-1].read_text())
                
                first_time = datetime.fromisoformat(first_cycle['timestamp'])
                last_time = datetime.fromisoformat(last_cycle['timestamp'])
                
                total_duration = last_time - first_time
                avg_cycle_time = total_duration / len(cycle_files) if len(cycle_files) > 1 else timedelta(0)
                
                print(f"⏱️ Average Cycle Duration: {avg_cycle_time}")
            except:
                pass
    else:
        print("⚠️ No cycle data available")
    
    print()
    
    # 4. Generated Assets
    print("🧬 GENERATED ASSETS")
    print("-" * 40)
    
    # Count different types of generated files
    models_count = len(list((forge_output / "models").glob("*"))) if (forge_output / "models").exists() else 0
    patches_count = len(list((forge_output / "patches").glob("*.json"))) if (forge_output / "patches").exists() else 0
    analysis_count = len(list((forge_output / "analysis").glob("*.json"))) if (forge_output / "analysis").exists() else 0
    applied_count = len(list(forge_output.glob("applied_*.json")))
    
    print(f"🤖 AI Models: {models_count}")
    print(f"🧬 Generated Patches: {patches_count}")
    print(f"📊 Analysis Reports: {analysis_count}")
    print(f"✅ Applied Patches: {applied_count}")
    
    print()
    
    # 5. Project Impact
    print("📱 PROJECT IMPACT")
    print("-" * 40)
    
    if android_project.exists():
        # Count Kotlin files
        kotlin_files = list(android_project.rglob("*.kt"))
        test_files = list(android_project.rglob("*Test.kt"))
        
        print(f"📄 Kotlin Files: {len(kotlin_files)}")
        print(f"🧪 Test Files: {len(test_files)}")
        
        # Calculate project size
        total_size = sum(f.stat().st_size for f in android_project.rglob("*") if f.is_file())
        print(f"📦 Project Size: {total_size / 1024:.1f} KB")
        
        # Check for recent modifications (sign of active development)
        recent_files = [f for f in kotlin_files if 
                       (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days < 1]
        
        if recent_files:
            print(f"🔥 Recently Modified: {len(recent_files)} files (last 24h)")
        
        # Check for FORGE-generated files
        forge_generated = []
        for kotlin_file in kotlin_files:
            try:
                content = kotlin_file.read_text()
                if "Generated by Continuous Workflow System" in content or "FORGE" in content:
                    forge_generated.append(kotlin_file)
            except:
                continue
        
        if forge_generated:
            print(f"🔥 FORGE-Generated Files: {len(forge_generated)}")
    else:
        print("⚠️ Android project not found")
    
    print()
    
    # 6. Performance Metrics
    print("⚡ PERFORMANCE METRICS")
    print("-" * 40)
    
    # Calculate success rates from cycle history
    if cycle_files:
        total_patches = 0
        applied_patches = 0
        
        for cycle_file in cycle_files:
            try:
                cycle_data = json.loads(cycle_file.read_text())
                total_patches += cycle_data.get('total_patches', 0)
                applied_patches += cycle_data.get('patches_applied', 0)
            except:
                continue
        
        if total_patches > 0:
            success_rate = (applied_patches / total_patches) * 100
            print(f"🎯 Overall Patch Success Rate: {success_rate:.1f}%")
        else:
            print("📊 No patch data available yet")
        
        print(f"📈 Total Patches Generated: {total_patches}")
        print(f"✅ Total Patches Applied: {applied_patches}")
    
    print()
    
    # 7. Resource Usage
    print("💾 RESOURCE USAGE")
    print("-" * 40)
    
    if forge_output.exists():
        # Calculate storage usage
        forge_size = sum(f.stat().st_size for f in forge_output.rglob("*") if f.is_file())
        print(f"💿 FORGE Data Size: {forge_size / 1024:.1f} KB")
        
        # Count total files
        forge_files = len(list(forge_output.rglob("*")))
        print(f"📁 FORGE Files: {forge_files}")
    
    # Check system resources (if available)
    try:
        result = subprocess.run(["df", "-h", "/data"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                disk_info = lines[1].split()
                if len(disk_info) >= 5:
                    print(f"💽 Disk Usage: {disk_info[4]} ({disk_info[2]}/{disk_info[1]})")
    except:
        pass
    
    print()
    
    # 8. Recommendations
    print("💡 RECOMMENDATIONS")
    print("-" * 40)
    
    recommendations = []
    
    if not workflow_running:
        recommendations.append("🔄 Restart the FORGE workflow system")
    
    if cycle_files and len(cycle_files) < 5:
        recommendations.append("⏰ Allow more time for meaningful cycle analysis")
    
    if patches_count == 0:
        recommendations.append("🧬 Check FORGE algorithm configurations")
    
    if applied_count == 0 and patches_count > 0:
        recommendations.append("🔍 Review patch risk thresholds")
    
    if not recommendations:
        recommendations.append("✅ System operating optimally")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print()
    print("=" * 80)
    print("🔥 FORGE-Enhanced Continuous Workflow - Status Report Complete")
    print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    generate_comprehensive_status()