Write-Host "🔧 Setting up Video Inspiration Finder..."

# Create virtual environment if it doesn't exist
if (-Not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..."
# On Windows, activate.ps1 is inside venv\Scripts
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "📚 Installing dependencies..."
pip install requests pandas scikit-learn numpy python-dotenv flask flask-cors

Write-Host "✅ Setup complete!"

# Functions
function Get-VideoCount {
    if (Test-Path "video_inspiration.db") {
        try {
            return (& sqlite3 video_inspiration.db "SELECT COUNT(*) FROM videos;")
        } catch {
            return 0
        }
    } else {
        return 0
    }
}

function Get-UnratedCount {
    if (Test-Path "video_inspiration.db") {
        try {
            return (& sqlite3 video_inspiration.db "SELECT COUNT(*) FROM videos v LEFT JOIN preferences p ON v.id = p.video_id WHERE p.video_id IS NULL;")
        } catch {
            return 0
        }
    } else {
        return 0
    }
}

# Check current state
$video_count = Get-VideoCount
$unrated_count = Get-UnratedCount

Write-Host ""
Write-Host "📊 Current Status:"
Write-Host "   Total videos: $video_count"
Write-Host "   Unrated videos: $unrated_count"
Write-Host ""

# Main menu
Write-Host "Choose what you want to do:"
Write-Host "1. 🌐 Launch Dashboard (recommended)"
Write-Host "2. 📱 Interactive CLI Rating Session"
Write-Host "3. 🔍 Search for More Videos"
Write-Host "4. 🛠️ Full Setup (Search + Rate + Dashboard)"
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🌐 Launching Dashboard..."
        if (($unrated_count -eq 0) -and ($video_count -gt 0)) {
            Write-Host "⚠️  All videos are rated. Searching for more videos first..."
            python search_more_videos.py
        } elseif ($video_count -eq 0) {
            Write-Host "⚠️  No videos found. Searching for videos first..."
            python main.py --search-only 2>$null
            if ($LASTEXITCODE -ne 0) { python search_more_videos.py }
        }
        Write-Host ""
        Write-Host "📱 Dashboard will be available at: http://localhost:5001"
        Write-Host "🛑 Press Ctrl+C to stop the server"
        Write-Host "----------------------------------------"
        python dashboard_api.py
    }
    "2" {
        Write-Host ""
        Write-Host "📱 Starting Interactive Rating Session..."
        python main.py
    }
    "3" {
        Write-Host ""
        Write-Host "🔍 Searching for more videos..."
        python search_more_videos.py
        Write-Host ""
        Write-Host "✅ Search complete! You can now:"
        Write-Host "   • Run 'setup.ps1' again and choose option 1 for Dashboard"
        Write-Host "   • Run 'python dashboard_api.py' directly"
    }
    "4" {
        Write-Host ""
        Write-Host "🛠️  Running Full Setup..."
        Write-Host "🔍 Step 1: Searching for videos..."
        python main.py --search-only 2>$null
        if ($LASTEXITCODE -ne 0) { python search_more_videos.py }
        Write-Host ""
        Write-Host "📱 Step 2: Starting rating session..."
        Write-Host "💡 Tip: Rate at least 10 videos to activate AI recommendations"
        Write-Host "   (You can press 'q' anytime to skip to dashboard)"
        python main.py
    }
    Default {
        Write-Host "❌ Invalid choice. Please run 'setup.ps1' again."
        exit 1
    }
}
