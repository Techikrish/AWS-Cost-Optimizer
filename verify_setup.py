#!/usr/bin/env python3
"""
AWS Cost Optimizer - Setup Verification Script
Verifies that all dependencies are installed and working
"""

import sys
import subprocess

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    import_name = import_name or package_name
    try:
        __import__(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} not installed")
        return False

def check_python_packages():
    """Check all required Python packages"""
    print("\n🔍 Checking Python packages...")
    packages = [
        ('Flask', 'flask'),
        ('Flask-CORS', 'flask_cors'),
        ('boto3', 'boto3'),
        ('cryptography', 'cryptography'),
        ('python-dotenv', 'dotenv'),
        ('requests', 'requests')
    ]
    
    all_ok = True
    for package, import_name in packages:
        if not check_package(package, import_name):
            all_ok = False
    
    return all_ok

def check_nodejs():
    """Check Node.js installation"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"✅ Node.js {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False

def check_npm_packages():
    """Check npm packages"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        print(f"✅ npm {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ npm not found")
        return False

def main():
    print("🚀 AWS Cost Optimizer - Setup Verification")
    print("==========================================\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Python Packages", check_python_packages),
        ("Node.js", check_nodejs),
        ("npm", check_npm_packages)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        results.append(check_func())
    
    print("\n" + "="*40)
    if all(results):
        print("✅ All checks passed! Ready to start.")
        print("\nRun these commands:")
        print("  Terminal 1: cd backend && source venv/bin/activate && python main.py")
        print("  Terminal 2: cd frontend && npm run dev")
        return 0
    else:
        print("❌ Some checks failed. Install missing dependencies.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
