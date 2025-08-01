#!/usr/bin/env python3
"""
Test the view creation functionality in setup.py without requiring MinIO.
"""

import sys
import os

# Test that setup can import and run view creation
try:
    from setup import setup_default_views
    print("✅ Successfully imported setup_default_views from setup.py")
    
    # Test view creation
    print("🧪 Testing view creation...")
    setup_default_views()
    print("✅ View creation completed successfully!")
    
    # Check that views were created
    from view_manager import ViewManager
    vm = ViewManager()
    views = vm.list_views()
    print(f"✅ Found {len(views)} views after setup:")
    for view in views:
        print(f"  - {view['name']}: {view['description']}")
    
except Exception as e:
    print(f"❌ Error testing view setup: {e}")
    sys.exit(1)

print("\n🎉 Setup script view integration test passed!")