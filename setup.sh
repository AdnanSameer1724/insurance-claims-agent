#!/bin/bash

# Insurance Claims Processing Agent - Setup Script
# Synapx Technical Assessment

echo "============================================================"
echo "  Insurance Claims Processing Agent - Setup"
echo "============================================================"
echo ""

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ Found: $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
    echo "✓ Virtual environment activated (Windows)"
else
    echo "⚠️  Warning: Could not activate virtual environment"
fi
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "Note: If network is available, uncomment packages in requirements.txt"
echo "For now, trying to install pdfplumber for PDF support..."
pip install pdfplumber 2>/dev/null || echo "⚠️  pdfplumber not installed - PDF support limited"
echo ""

# Run tests
echo "Running test suite..."
python3 run_tests.py
echo ""

echo "============================================================"
echo "  Setup Complete!"
echo "============================================================"
echo ""
echo "Usage:"
echo "  1. Process a single claim:"
echo "     python3 claims_processor_simple.py <path_to_claim.pdf|.txt>"
echo ""
echo "  2. Run test suite:"
echo "     python3 run_tests.py"
echo ""
echo "Sample claims are provided in:"
echo "  - sample_claim.txt (injury/specialist queue)"
echo "  - sample_claim_fasttrack.txt (low damage)"
echo "  - sample_claim_fraud.txt (investigation)"
echo "  - sample_claim_incomplete.txt (manual review)"
echo ""
echo "============================================================"
