#!/usr/bin/env python3
"""
CLI tool for managing DuckDB views in the conversation analytics system.
"""

import sys
import argparse
from view_manager import ViewManager

def list_views(args):
    """List all available views."""
    vm = ViewManager()
    views = vm.list_views()
    
    if not views:
        print("No views found.")
        return
    
    print(f"\n📊 Available Views ({len(views)} total):")
    print("=" * 60)
    
    for view in views:
        print(f"\n🔍 {view['name']}")
        print(f"   Description: {view['description']}")
        print(f"   Tags: {', '.join(view['tags'])}")
        print(f"   Created: {view.get('created', 'Unknown')}")


def create_view(args):
    """Create a new view."""
    vm = ViewManager()
    
    try:
        success = vm.create_view(
            view_name=args.name,
            description=args.description,
            sql_query=args.sql,
            tags=args.tags.split(',') if args.tags else [],
            replace=args.replace
        )
        
        if success:
            print(f"✅ Successfully created view '{args.name}'")
        
    except Exception as e:
        print(f"❌ Failed to create view: {e}")
        sys.exit(1)


def delete_view(args):
    """Delete a view."""
    vm = ViewManager()
    
    if not args.force:
        confirm = input(f"Are you sure you want to delete view '{args.name}'? (y/N): ")
        if confirm.lower() not in ['y', 'yes']:
            print("Cancelled.")
            return
    
    success = vm.delete_view(args.name)
    
    if success:
        print(f"✅ Successfully deleted view '{args.name}'")
    else:
        print(f"❌ View '{args.name}' not found")


def show_view(args):
    """Show details of a specific view."""
    vm = ViewManager()
    view = vm.get_view(args.name)
    
    if not view:
        print(f"❌ View '{args.name}' not found")
        sys.exit(1)
    
    print(f"\n🔍 View: {view['name']}")
    print("=" * 60)
    print(f"Description: {view['description']}")
    print(f"Tags: {', '.join(view['tags'])}")
    print(f"Created: {view.get('created', 'Unknown')}")
    print(f"Updated: {view.get('updated', 'Unknown')}")
    print(f"\nSQL Query:")
    print(view['sql_query'])


def create_defaults(args):
    """Create default views."""
    vm = ViewManager()
    print("Creating default views...")
    vm.create_default_views()
    print("✅ Default views created successfully!")


def test_view(args):
    """Test a view by executing it."""
    vm = ViewManager()
    view = vm.get_view(args.name)
    
    if not view:
        print(f"❌ View '{args.name}' not found")
        sys.exit(1)
    
    print(f"🧪 Testing view '{args.name}'...")
    
    try:
        conn = vm._get_duckdb_connection()
        
        # Create the view
        create_sql = f"CREATE OR REPLACE VIEW {args.name} AS {view['sql_query']}"
        conn.execute(create_sql)
        
        # Test query with limit
        limit = args.limit or 5
        test_sql = f"SELECT * FROM {args.name} LIMIT {limit}"
        result = conn.execute(test_sql).fetchall()
        
        if result:
            columns = [desc[0] for desc in conn.description]
            print(f"✅ View works! Got {len(result)} rows")
            print(f"Columns: {', '.join(columns)}")
            print(f"\nSample data (first {min(len(result), 3)} rows):")
            for i, row in enumerate(result[:3]):
                print(f"  Row {i+1}: {dict(zip(columns, row))}")
        else:
            print("✅ View works but returned no data")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ View test failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Manage DuckDB views for conversation analytics")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List views
    list_parser = subparsers.add_parser('list', help='List all views')
    list_parser.set_defaults(func=list_views)
    
    # Create view
    create_parser = subparsers.add_parser('create', help='Create a new view')
    create_parser.add_argument('name', help='View name')
    create_parser.add_argument('description', help='View description')
    create_parser.add_argument('sql', help='SQL query for the view')
    create_parser.add_argument('--tags', help='Comma-separated tags')
    create_parser.add_argument('--replace', action='store_true', help='Replace existing view')
    create_parser.set_defaults(func=create_view)
    
    # Delete view
    delete_parser = subparsers.add_parser('delete', help='Delete a view')
    delete_parser.add_argument('name', help='View name to delete')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    delete_parser.set_defaults(func=delete_view)
    
    # Show view
    show_parser = subparsers.add_parser('show', help='Show view details')
    show_parser.add_argument('name', help='View name to show')
    show_parser.set_defaults(func=show_view)
    
    # Test view
    test_parser = subparsers.add_parser('test', help='Test a view by executing it')
    test_parser.add_argument('name', help='View name to test')
    test_parser.add_argument('--limit', type=int, help='Limit number of rows to return (default: 5)')
    test_parser.set_defaults(func=test_view)
    
    # Create defaults
    defaults_parser = subparsers.add_parser('create-defaults', help='Create default views')
    defaults_parser.set_defaults(func=create_defaults)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()