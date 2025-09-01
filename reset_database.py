#!/usr/bin/env python3
"""
This will delete your existing database and create a fresh one.
"""

import os
import sqlite3
from pathlib import Path


def reset_database():
    db_path = "video_inspiration.db"

    # Check if database exists
    if Path(db_path).exists():
        print(f"🗑️  Removing existing database: {db_path}")
        os.remove(db_path)

    # Create new database with updated schema
    print("🔧 Creating new database with updated schema...")
    from backend.database.manager import setup_database_tables

    setup_database_tables(db_path)

    print("✅ Database reset complete!")
    print("\nNext steps:")
    print("1. Run the main application to search for videos with your new queries")
    print("2. The system will now find videos based on your actual search terms")


if __name__ == "__main__":
    print("🔄 Database Reset Tool")
    print("=" * 40)
    print("This will delete your existing database and ratings.")

    confirm = input("\nContinue? (y/N): ").strip().lower()

    if confirm == "y":
        reset_database()
    else:
        print("❌ Reset cancelled.")
