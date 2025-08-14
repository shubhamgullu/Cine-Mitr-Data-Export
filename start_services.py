"""
Startup script to run both FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def run_fastapi():
    """Run FastAPI backend server"""
    print("🚀 Starting FastAPI backend server...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])

def run_streamlit():
    """Run Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", 
        "run", 
        "cinemitr_dashboard.py", 
        "--server.port", "8501"
    ])

def main():
    """Main startup function"""
    print("🎬 Starting CineMitr Content Management System")
    print("=" * 50)
    
    # Start FastAPI backend
    fastapi_process = run_fastapi()
    time.sleep(3)  # Give FastAPI time to start
    
    # Start Streamlit frontend
    streamlit_process = run_streamlit()
    
    print("\n✅ Both services started successfully!")
    print("📊 Streamlit Dashboard: http://localhost:8501")
    print("🔗 FastAPI Backend: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep the main process running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if fastapi_process.poll() is not None:
                print("❌ FastAPI process stopped unexpectedly")
                break
                
            if streamlit_process.poll() is not None:
                print("❌ Streamlit process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        # Terminate processes
        fastapi_process.terminate()
        streamlit_process.terminate()
        
        # Wait for graceful shutdown
        try:
            fastapi_process.wait(timeout=5)
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if not terminated gracefully
            fastapi_process.kill()
            streamlit_process.kill()
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()