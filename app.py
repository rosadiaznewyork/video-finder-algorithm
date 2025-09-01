#!/usr/bin/env python3
"""
MyTube - YouTube Video Recommendation System
Single entry point for all functionality
"""
import argparse
import sys
import os
import subprocess
import time
import sqlite3
from pathlib import Path


def install():
    """Install dependencies and set up the application"""
    print("🔧 MyTube - Installation")
    print("========================")

    # Find Python interpreter
    if subprocess.run(["which", "python3"], capture_output=True).returncode == 0:
        python_cmd = "python3"
    elif subprocess.run(["which", "python"], capture_output=True).returncode == 0:
        python_cmd = "python"
    else:
        print("❌ No Python found. Install Python 3 and re-run.")
        print("   macOS: brew install python@3.12")
        print("   Ubuntu: sudo apt install python3 python3-venv")
        return False

    print(f"🐍 Using: {python_cmd}")

    # Create virtual environment
    if not Path("venv").exists():
        print("📦 Creating virtual environment...")
        subprocess.run([python_cmd, "-m", "venv", "venv"], check=True)
    else:
        print("📦 Virtual environment already exists")

    # Find venv Python
    venv_python = (
        "venv/bin/python" if Path("venv/bin/python").exists() else "venv/bin/python3"
    )
    if not Path(venv_python).exists():
        print("❌ Virtual environment creation failed")
        return False

    # Install dependencies
    print("📚 Installing dependencies...")
    subprocess.run(
        [venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True
    )
    subprocess.run(
        [
            venv_python,
            "-m",
            "pip",
            "install",
            "requests",
            "pandas",
            "scikit-learn",
            "numpy",
            "python-dotenv",
            "flask",
            "flask-cors",
        ],
        check=True,
    )

    # Check for .env file
    if not Path(".env").exists():
        print("⚠️  No .env file found!")
        print("Please create a .env file with your YouTube API key:")
        print("   YOUTUBE_API_KEY=your_api_key_here")
        print("")
        print("Get your API key at: https://console.developers.google.com/")
        print("")
        print("📊 Quota Usage Info:")
        print("   • YouTube API has a default quota of 10,000 units/day")
        print("   • Each search uses ~108 quota units (search + video details)")
        print("   • Initial app startup uses ~315 units (3 searches)")
        print("   • 'python app.py search' uses ~324 units (3 searches)")
        print("")

    print("✅ Installation complete!")
    print("")
    print("🚀 To start the application:")
    print("   python app.py           # Start web dashboard")
    print("   python app.py search    # Search for more videos")
    return True


def check_has_videos():
    """Check if database has videos"""
    if not Path("video_inspiration.db").exists():
        return False

    try:
        conn = sqlite3.connect("video_inspiration.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM videos")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except:
        return False


def run_web(port=8000, debug=False, auto_open=True):
    """Run the web dashboard"""
    from backend.web import create_app

    print("🚀 MyTube - Web Dashboard")
    print("=========================")

    # Check if database and videos exist
    if not check_has_videos():
        print("📋 No videos found in database. Loading initial videos...")
        try:
            _load_initial_videos()
            # Verify videos were actually loaded
            if check_has_videos():
                print("✅ Initial videos loaded successfully!")
            else:
                print("⚠️  Warning: No videos were loaded (API may have failed)")
                print("Dashboard will start in demo mode.")
        except Exception as e:
            print(f"⚠️  Could not load initial videos: {e}")
            print("   This is likely due to YouTube API quota limits.")
            print(
                "   Dashboard will start in demo mode - you can still explore the interface!"
            )
            print("   API quotas reset daily, so try again tomorrow.")
        print("")

    # Start dashboard
    print(f"🌐 Starting dashboard server on port {port}...")
    print(f"📱 Dashboard will be available at: http://localhost:{port}")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 40)

    # Auto-open browser
    if auto_open:
        import threading

        def open_browser():
            time.sleep(2)
            import webbrowser

            webbrowser.open(f"http://localhost:{port}")

        threading.Thread(target=open_browser, daemon=True).start()

    try:
        app = create_app()
        app.run(host="0.0.0.0", port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped!")
    except Exception as e:
        print(f"Error starting dashboard: {e}")


def _load_initial_videos():
    """Load initial videos when starting the web app for the first time"""
    import os
    from dotenv import load_dotenv
    from backend.database.manager import setup_database_tables
    from backend.database.video_operations import (
        save_videos_to_database,
        save_video_features_to_database,
    )
    from backend.services.youtube_service import YouTubeService
    from backend.ml.feature_extraction import extract_all_features_from_video
    from backend.config.search_config import get_search_queries

    load_dotenv()

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise Exception("YOUTUBE_API_KEY not found in environment variables")

    db_path = "video_inspiration.db"
    setup_database_tables(db_path)

    youtube_service = YouTubeService(api_key)
    all_queries = get_search_queries()

    # Use first 3 queries for initial load to save quota
    initial_queries = all_queries[:3]
    print(f"      Searching {len(initial_queries)} topics...")

    all_videos = []
    for query in initial_queries:
        try:
            videos = youtube_service.search_and_get_details(
                query, 5
            )  # Only 5 videos per query to save quota
            all_videos.extend(videos)
            print(
                f"      Found {len(videos)} videos for '{query}' (quota used: ~105 units)"
            )
        except Exception as e:
            print(f"      Warning: Could not search '{query}': {e}")

    unique_videos = YouTubeService.remove_duplicate_videos(all_videos)
    print(f"      Total unique videos: {len(unique_videos)}")

    if unique_videos:
        save_videos_to_database(unique_videos, db_path)
        for video in unique_videos:
            features = extract_all_features_from_video(video)
            save_video_features_to_database(video["id"], features, db_path)
        print(f"      Saved {len(unique_videos)} videos to database")
    else:
        raise Exception("No videos were found (likely due to API quota limits)")


def run_search():
    """Search for videos and add them to the database"""
    import os
    from dotenv import load_dotenv
    from backend.database.manager import setup_database_tables
    from backend.database.video_operations import (
        save_videos_to_database,
        save_video_features_to_database,
    )
    from backend.services.youtube_service import YouTubeService
    from backend.ml.feature_extraction import extract_all_features_from_video
    from backend.config.search_config import get_search_queries
    import random

    load_dotenv()

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("❌ Error: YOUTUBE_API_KEY not found in environment variables")
        print("Please create a .env file with your YouTube API key:")
        print("   YOUTUBE_API_KEY=your_api_key_here")
        return

    db_path = "video_inspiration.db"
    setup_database_tables(db_path)

    youtube_service = YouTubeService(api_key)
    all_queries = get_search_queries()

    # Use different queries for search vs initial load
    if len(all_queries) > 3:
        search_queries = all_queries[3:6]  # Use queries 3-6 for search command
    else:
        search_queries = all_queries.copy()
        random.shuffle(search_queries)
        search_queries = search_queries[:3]  # Limit to 3 queries

    print(f"🔍 Searching {len(search_queries)} topics for videos...")
    print(f"   Estimated quota usage: ~{len(search_queries) * 110} units")

    all_videos = []
    for i, query in enumerate(search_queries, 1):
        print(f"  [{i}/{len(search_queries)}] Searching: {query}")
        try:
            videos = youtube_service.search_and_get_details(
                query, 8
            )  # Reduced from 10 to 8
            all_videos.extend(videos)
            print(f"      Found {len(videos)} videos (quota used: ~108 units)")
        except Exception as e:
            print(f"      Error searching '{query}': {e}")

    unique_videos = YouTubeService.remove_duplicate_videos(all_videos)

    if unique_videos:
        print(f"💾 Saving {len(unique_videos)} unique videos to database...")
        save_videos_to_database(unique_videos, db_path)

        print("🧠 Extracting features for ML recommendations...")
        for i, video in enumerate(unique_videos, 1):
            if i % 10 == 0:  # Show progress every 10 videos
                print(f"      Processing features: {i}/{len(unique_videos)}")
            features = extract_all_features_from_video(video)
            save_video_features_to_database(video["id"], features, db_path)

        estimated_quota_used = len(search_queries) * 108
        print(f"✅ Successfully added {len(unique_videos)} videos to the database!")
        print(f"   Estimated quota used: ~{estimated_quota_used} units")
    else:
        print("❌ No new videos found.")
        print("   This might be due to YouTube API quota limits or network issues.")
        print("   API quotas reset daily. Try again later.")


def check_frontend_built():
    """Check if the frontend is built"""
    dist_path = Path("frontend/dist")
    return dist_path.exists() and (dist_path / "index.html").exists()


def build_frontend():
    """Build the frontend"""
    print("🔨 Building Vue frontend...")
    try:
        subprocess.run(["npm", "run", "build"], cwd="frontend", check=True)
        print("✅ Frontend built successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Frontend build failed!")
        return False
    except FileNotFoundError:
        print("❌ npm not found. Make sure Node.js is installed.")
        print("💡 Install Node.js and run: cd frontend && npm install")
        return False


def start_vue_dev_server():
    """Start Vue development server"""
    print("🔥 Vue Development Mode")
    print("=======================")
    print("📱 Vue app will be available at: http://localhost:3000")
    print("🔌 API calls will be proxied to Flask backend")
    print("📝 Note: Start Flask API separately with: python app.py --port 8000")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    try:
        subprocess.run(["npm", "run", "dev"], cwd="frontend")
    except KeyboardInterrupt:
        print("\n👋 Vue dev server stopped!")
    except FileNotFoundError:
        print("❌ npm not found. Make sure Node.js is installed.")
        print("💡 Run: cd frontend && npm install")


def ensure_venv():
    """Ensure we're running in the virtual environment"""
    if Path("venv").exists() and not sys.executable.startswith(
        str(Path("venv").absolute())
    ):
        # We have a venv but we're not using it
        venv_python = (
            "venv/bin/python"
            if Path("venv/bin/python").exists()
            else "venv/bin/python3"
        )
        if Path(venv_python).exists():
            # Re-run with venv python
            os.execv(venv_python, [venv_python] + sys.argv)


def main():
    # Auto-switch to venv if available (except for install command)
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] != "install"):
        ensure_venv()

    parser = argparse.ArgumentParser(
        description="MyTube - YouTube Video Recommendation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  install                      # Install dependencies and set up
  run                         # Start web dashboard (default)
  search                      # Search for more videos
  dev                         # Start Vue development server

Examples:
  python app.py install       # First-time setup
  python app.py run           # Start web dashboard (production)
  python app.py dev           # Vue development server
  python app.py run --dev     # Vue development server (alternative)
  python app.py run --build   # Force rebuild frontend
  python app.py run --port 3000 --debug  # Custom options
  python app.py search        # Search for videos
        """,
    )

    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["install", "run", "search", "dev"],
        help="Command to execute (default: run)",
    )

    parser.add_argument(
        "--port", type=int, default=8000, help="Port for web server (default: 8000)"
    )

    parser.add_argument(
        "--debug", action="store_true", help="Run web server in debug mode"
    )

    parser.add_argument(
        "--no-browser", action="store_true", help="Don't auto-open browser for web mode"
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        help="Start Vue dev server instead of production build",
    )

    parser.add_argument(
        "--build", action="store_true", help="Force rebuild frontend before starting"
    )

    args = parser.parse_args()

    if args.command == "install":
        install()
    elif args.command == "search":
        run_search()
    elif args.command == "dev":
        start_vue_dev_server()
    elif args.command == "run":
        if args.dev:
            start_vue_dev_server()
        else:
            # Production mode - ensure frontend is built
            if args.build or not check_frontend_built():
                if not build_frontend():
                    print("⚠️  Frontend build failed, but continuing with Flask API...")
            run_web(port=args.port, debug=args.debug, auto_open=not args.no_browser)


if __name__ == "__main__":
    main()
