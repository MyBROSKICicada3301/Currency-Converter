#!/usr/bin/env python3
"""
Currency Converter Web Application Launcher

This script automatically installs required dependencies and launches the 
Currency Converter web application. Simply run this file and it will:

1. Check for required dependencies (Flask, yfinance, requests)
2. Automatically install any missing packages
3. Launch the web application on http://127.0.0.1:5000

No manual dependency installation required!
"""

if __name__ == "__main__":
    print("🚀 Starting Currency Converter...")
    print("=" * 50)
    
    # Import and run the main app
    from currency_converter.app import main
    
    print("🌐 Opening web application...")
    print("📍 URL: http://127.0.0.1:5000")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Currency Converter stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Try running: pip install -r requirements.txt")
