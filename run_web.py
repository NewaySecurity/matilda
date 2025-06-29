#!/usr/bin/env python
"""
Launcher script for Matilda web interface
"""

import os
import sys
from pathlib import Path

# Add web directory to Python path
web_dir = Path(__file__).parent / "web"
sys.path.append(str(web_dir))

# Import app from web module
try:
    from app import app
except ImportError as e:
    print(f"Error: {e}")
    print("Make sure you have installed the required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    # Run the Flask app
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    
    print("\n" + "=" * 70)
    print(f"MATILDA - Web Interface")
    print("=" * 70)
    print(f"\nOpen your browser and navigate to: http://localhost:{port}")
    print("\nPress Ctrl+C to exit")
    print("=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

