#!/usr/bin/env python3
"""
Clear CareDocQA Database - Remove Duplicate Uploads
This script cleans up the SQLite database and document storage
"""

import sqlite3
import os
import shutil
from pathlib import Path

def clear_database():
    """Clear the documents database and file storage"""
    print("🗑️  Clearing CareDocQA Database...")
    
    # Database file path
    db_path = Path("data/documents.db")
    documents_dir = Path("data/documents")
    
    try:
        # Clear SQLite database
        if db_path.exists():
            print(f"📄 Clearing database: {db_path}")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get count before deletion
            cursor.execute("SELECT COUNT(*) FROM documents")
            count_before = cursor.fetchone()[0]
            print(f"🔢 Documents before cleanup: {count_before}")
            
            # Clear all documents
            cursor.execute("DELETE FROM documents")
            conn.commit()
            
            # Reset auto-increment counter
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='documents'")
            conn.commit()
            
            conn.close()
            print("✅ Database cleared successfully!")
        else:
            print("ℹ️  No database file found")
    
        # Clear document files
        if documents_dir.exists():
            print(f"📁 Clearing document files: {documents_dir}")
            file_count = len(list(documents_dir.glob("*")))
            print(f"🔢 Files before cleanup: {file_count}")
            
            # Remove all files in documents directory
            for file_path in documents_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
                    
            print("✅ Document files cleared successfully!")
        else:
            print("ℹ️  No documents directory found")
            
        print("\n🎉 Database cleanup complete!")
        print("📋 Next steps:")
        print("1. Upload some sample documents")
        print("2. Ask questions about them")
        print("3. Test the clean system")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        print("💡 Make sure no services are currently running")

def show_current_status():
    """Show current database status"""
    print("\n📊 Current Database Status:")
    
    db_path = Path("data/documents.db")
    documents_dir = Path("data/documents")
    
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            doc_count = cursor.fetchone()[0]
            print(f"📄 Documents in database: {doc_count}")
            
            if doc_count > 0:
                cursor.execute("""
                    SELECT original_filename, upload_timestamp, file_size 
                    FROM documents 
                    ORDER BY upload_timestamp DESC 
                    LIMIT 10
                """)
                documents = cursor.fetchall()
                print("\n📋 Recent documents:")
                for doc in documents:
                    filename, timestamp, size = doc
                    print(f"  • {filename} ({size} bytes) - {timestamp}")
            
            conn.close()
        except Exception as e:
            print(f"❌ Error reading database: {e}")
    else:
        print("📄 No database file exists")
    
    if documents_dir.exists():
        file_count = len(list(documents_dir.glob("*")))
        print(f"📁 Files in storage: {file_count}")
    else:
        print("📁 No documents directory exists")

if __name__ == "__main__":
    print("🏥 CareDocQA Database Management")
    print("=" * 40)
    
    # Show current status
    show_current_status()
    
    print("\n" + "=" * 40)
    
    # Ask for confirmation
    response = input("\n❓ Do you want to clear all documents? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        clear_database()
        
        # Show status after cleanup
        print("\n" + "=" * 40)
        show_current_status()
    else:
        print("✅ No changes made to database")
        print("💡 Run again with 'y' to clear database") 