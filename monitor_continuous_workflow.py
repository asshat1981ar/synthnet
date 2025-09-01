#!/usr/bin/env python3
"""
Monitor FORGE-Enhanced Continuous Workflow System
Real-time monitoring of the continuous workflow system
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime

async def monitor_workflow():
    synthnet_path = Path("/data/data/com.termux/files/home/synthnet")
    forge_output = synthnet_path / "forge_continuous_output"
    
    print("🔍 FORGE Continuous Workflow Monitor")
    print("=" * 50)
    print("Monitoring active workflow system...")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    cycle_count = 0
    last_health_check = None
    
    while True:
        try:
            # Check for new cycle results
            cycle_files = sorted(forge_output.glob("forge_cycle_*.json"))
            if cycle_files:
                latest_cycle = cycle_files[-1]
                current_cycle = int(latest_cycle.stem.split('_')[-1])
                
                if current_cycle > cycle_count:
                    cycle_count = current_cycle
                    
                    # Read latest cycle data
                    cycle_data = json.loads(latest_cycle.read_text())
                    
                    print(f"🔥 FORGE Cycle #{cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                    print(f"   🎯 Triage Success: {cycle_data['pipeline_results']['triage']:.1f}%")
                    print(f"   🔍 Localization Success: {cycle_data['pipeline_results']['localization']:.1f}%")
                    print(f"   🧬 Generation Success: {cycle_data['pipeline_results']['generation']:.1f}%")
                    print(f"   📊 Validation Success: {cycle_data['pipeline_results']['validation']:.1f}%")
                    print(f"   ✅ Patches Applied: {cycle_data['patches_applied']}/{cycle_data['total_patches']}")
                    print()
            
            # Check system health
            health_file = forge_output / "forge_health.json"
            if health_file.exists():
                health_data = json.loads(health_file.read_text())
                current_health_time = health_data['timestamp']
                
                if current_health_time != last_health_check:
                    last_health_check = current_health_time
                    
                    print(f"💚 System Health - {datetime.now().strftime('%H:%M:%S')}")
                    print(f"   Status: {health_data['system_status'].upper()}")
                    for phase, pipeline in health_data['pipelines'].items():
                        print(f"   {phase.title()}: {pipeline['success_rate']:.1f}% success")
                    print()
            
            # Check for patches
            patch_files = list((forge_output / "patches").glob("patch_*.json"))
            applied_files = list(forge_output.glob("applied_*.json"))
            
            if len(patch_files) != getattr(monitor_workflow, 'last_patch_count', 0):
                monitor_workflow.last_patch_count = len(patch_files)
                print(f"🧬 Patches: {len(patch_files)} generated, {len(applied_files)} applied")
                print()
            
            await asyncio.sleep(5)  # Check every 5 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Monitor error: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(monitor_workflow())