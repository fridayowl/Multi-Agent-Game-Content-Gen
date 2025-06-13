#!/usr/bin/env python3
"""
Quick test to verify your agents are working
Save this as: quick_test.py in your root directory
"""

import asyncio
import json
import sys
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*50}")
    print(f"🧪 {title}")
    print(f"{'='*50}")

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n{step_num}️⃣  {description}")
    print("-" * 40)

async def test_integration():
    """Main test function"""
    print_header("Quick Agent Integration Test")
    
    # Test 1: Check Python environment
    print_step(1, "Checking Python Environment")
    print(f"✅ Python version: {sys.version.split()[0]}")
    print(f"✅ Current directory: {Path.cwd()}")
    
    # Test 2: Import agents
    print_step(2, "Testing Agent Imports")
    world_designer = None
    asset_generator = None
    
    try:
        from world_designer.agent import root_agent as world_designer
        print("✅ World Designer imported successfully!")
    except ImportError as e:
        print(f"❌ World Designer import failed: {e}")
        print("   → Check that world_designer/agent.py exists and has root_agent")
    except Exception as e:
        print(f"❌ World Designer error: {e}")
    
    try:
        from asset_generator.agent import root_agent as asset_generator
        print("✅ Asset Generator imported successfully!")
    except ImportError as e:
        print(f"❌ Asset Generator import failed: {e}")
        print("   → Check that asset_generator/agent.py exists and has root_agent")
        print("   → Your asset_generator/agent.py might be incomplete (only 4 lines)")
    except Exception as e:
        print(f"❌ Asset Generator error: {e}")
    
    # If either agent failed to import, stop here
    if not world_designer or not asset_generator:
        print(f"\n❌ Cannot continue - agent imports failed")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Make sure both agent.py files have complete code")
        print("2. Check that both agents define 'root_agent'")
        print("3. Verify folder structure matches ADK requirements")
        return False
    
    # Test 3: Check agent status
    print_step(3, "Checking Agent Status")
    try:
        wd_status = await world_designer.get_status()
        print(f"✅ World Designer status: {wd_status.get('status', 'Unknown')}")
        
        # Show more details if available
        if 'model' in wd_status:
            print(f"   Model: {wd_status['model']}")
        if 'capabilities' in wd_status:
            print(f"   Capabilities: {len(wd_status['capabilities'])} features")
            
    except Exception as e:
        print(f"⚠️  World Designer status check failed: {e}")
    
    try:
        ag_status = await asset_generator.get_status()
        print(f"✅ Asset Generator status: {ag_status.get('status', 'Unknown')}")
        print(f"   Blender Available: {ag_status.get('blender_available', False)}")
        blender_path = ag_status.get('blender_path', 'Not found')
        if blender_path and blender_path != 'Not found':
            print(f"   Blender Path: {blender_path}")
        else:
            print(f"   Blender Path: ⚠️  Not found (will generate scripts only)")
            
    except Exception as e:
        print(f"⚠️  Asset Generator status check failed: {e}")
    
    # Test 4: Test World Designer
    print_step(4, "Testing World Designer")
    world_json = None
    
    try:
        prompt = "Create a small medieval house with a tree"
        print(f"📝 Prompt: '{prompt}'")
        
        world_json = await world_designer.generate_world(prompt)
        
        print(f"✅ World generated successfully!")
        print(f"   Theme: {world_json.get('theme', 'Unknown')}")
        print(f"   Buildings: {len(world_json.get('buildings', []))}")
        print(f"   Environment: {'Yes' if world_json.get('environment') else 'No'}")
        print(f"   Props: {len(world_json.get('props', []))}")
        
        # Show sample building if available
        buildings = world_json.get('buildings', [])
        if buildings:
            building = buildings[0]
            print(f"   Sample Building: {building.get('type', 'Unknown')} at {building.get('position', {})}")
        
        # Save the world for inspection
        world_file = Path("test_world.json")
        with open(world_file, 'w') as f:
            json.dump(world_json, f, indent=2)
        print(f"   💾 Saved world to: {world_file}")
        
    except Exception as e:
        print(f"❌ World Designer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Test Asset Generator
    print_step(5, "Testing Asset Generator")
    
    if not world_json:
        print("❌ No world JSON available from previous step")
        return False
    
    try:
        print(f"🏗️  Generating assets from world design...")
        
        assets = await asset_generator.generate_assets(world_json)
        
        print(f"✅ Assets generated successfully!")
        summary = assets.get('generation_summary', {})
        print(f"   Total Assets: {summary.get('total_assets', 0)}")
        print(f"   Buildings: {summary.get('buildings_count', 0)}")
        print(f"   Environment: {summary.get('environment_count', 0)}")
        print(f"   Props: {summary.get('props_count', 0)}")
        
        output_dir = Path(assets.get('output_directory', 'generated_assets'))
        print(f"   📁 Output Directory: {output_dir}")
        
        # Check what files were actually created
        if output_dir.exists():
            print(f"\n📋 Generated Files:")
            
            # Check models
            models_dir = output_dir / "models"
            if models_dir.exists():
                model_files = list(models_dir.glob("*"))
                print(f"   🎯 3D Models: {len(model_files)}")
                for file in model_files[:3]:  # Show first 3
                    print(f"     - {file.name} ({file.stat().st_size} bytes)")
                if len(model_files) > 3:
                    print(f"     ... and {len(model_files) - 3} more")
            
            # Check scripts
            scripts_dir = output_dir / "blender_scripts"
            if scripts_dir.exists():
                script_files = list(scripts_dir.glob("*.py"))
                print(f"   📜 Blender Scripts: {len(script_files)}")
                for file in script_files[:3]:  # Show first 3
                    print(f"     - {file.name}")
                if len(script_files) > 3:
                    print(f"     ... and {len(script_files) - 3} more")
            
            # Check manifest
            manifest_file = output_dir / "asset_manifest.json"
            if manifest_file.exists():
                print(f"   📄 Asset Manifest: ✅ Created")
            else:
                print(f"   📄 Asset Manifest: ❌ Missing")
        else:
            print(f"   ⚠️  Output directory not found: {output_dir}")
        
    except Exception as e:
        print(f"❌ Asset Generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Final success check
    print_step(6, "Final Results")
    
    success_checks = [
        ("World Designer Import", world_designer is not None),
        ("Asset Generator Import", asset_generator is not None),
        ("World Generation", world_json is not None),
        ("Asset Generation", assets is not None),
        ("Output Files", output_dir.exists() if 'output_dir' in locals() else False)
    ]
    
    all_passed = True
    for check_name, passed in success_checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 SUCCESS! Your Multi-Agent Pipeline is Working!")
        print(f"🚀 Ready for full development!")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Check generated files in: {output_dir if 'output_dir' in locals() else 'generated_assets/'}")
        print(f"2. Try different prompts with your World Designer")
        print(f"3. Examine the Blender scripts if Blender isn't directly available")
        print(f"4. Move on to building the Character Creator Agent")
        
        return True
    else:
        print(f"\n❌ Some tests failed. Check the error messages above.")
        return False

def print_troubleshooting():
    """Print troubleshooting tips"""
    print(f"\n🔧 TROUBLESHOOTING GUIDE")
    print(f"{'='*50}")
    
    print(f"\n❌ Import Errors:")
    print(f"   • Check agent.py files exist and have 'root_agent' defined")
    print(f"   • Make sure __init__.py files are present")
    print(f"   • Verify ADK is installed: pip install adk")
    
    print(f"\n❌ World Designer Issues:")
    print(f"   • Check if your world_designer/agent.py has complete code")
    print(f"   • Verify API keys are set in .env file")
    print(f"   • Test with simpler prompts first")
    
    print(f"\n❌ Asset Generator Issues:")
    print(f"   • Your asset_generator/agent.py might be incomplete (only 4 lines)")
    print(f"   • Install Blender or it will generate scripts only")
    print(f"   • Check folder permissions for output directory")
    
    print(f"\n❌ Blender Issues:")
    print(f"   • Blender not required - scripts will be generated instead")
    print(f"   • Install Blender from blender.org for direct 3D model generation")
    
    print(f"\n🆘 Need Help?")
    print(f"   • Check log files in generated directories")
    print(f"   • Run: python -c 'import sys; print(sys.path)' to check Python path")
    print(f"   • Verify you're in the right directory: {Path.cwd()}")

async def main():
    """Main function"""
    try:
        success = await test_integration()
        
        if not success:
            print_troubleshooting()
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print_troubleshooting()
        sys.exit(1)

if __name__ == "__main__":
    print("🎮 Multi-Agent Game Content Pipeline - Quick Test")
    print("Starting comprehensive agent integration test...")
    
    asyncio.run(main())