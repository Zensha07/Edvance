#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("Flask app loaded successfully!")
    print("Starting server on http://127.0.0.1:5001")
    app.run(debug=True, host='127.0.0.1', port=5001)
except Exception as e:
    print(f"Error loading Flask app: {e}")
    import traceback
    traceback.print_exc()
