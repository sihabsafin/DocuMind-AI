#!/bin/bash

# DocuMind AI - Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "🚀 DocuMind AI - Setup Script"
echo "================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.11+ is required. Found: $python_version"
    exit 1
fi
echo "✅ Python version OK: $python_version"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/uploads
mkdir -p data/processed
mkdir -p data/summaries
touch data/uploads/.gitkeep
touch data/processed/.gitkeep
touch data/summaries/.gitkeep
echo "✅ Directories created"
echo ""

# Setup environment file
echo "🔐 Setting up environment configuration..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping..."
else
    cp .env.example .env
    echo "✅ .env file created from template"
    echo "⚠️  IMPORTANT: Edit .env and add your GROQ_API_KEY"
fi
echo ""

# Download spaCy model (optional)
echo "📚 Downloading spaCy model (optional)..."
read -p "Do you want to download spaCy English model? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python -m spacy download en_core_web_sm
    echo "✅ spaCy model downloaded"
else
    echo "⏭️  Skipping spaCy model download"
fi
echo ""

# Create Streamlit config
echo "🎨 Setting up Streamlit configuration..."
if [ -f ".streamlit/secrets.toml" ]; then
    echo "⚠️  Streamlit secrets already exist. Skipping..."
else
    cp .streamlit/secrets.toml.example .streamlit/secrets.toml
    echo "✅ Streamlit secrets template created"
    echo "⚠️  IMPORTANT: Edit .streamlit/secrets.toml and add your API keys"
fi
echo ""

# Test imports
echo "🧪 Testing imports..."
python -c "
import streamlit as st
import langchain
from langchain_groq import ChatGroq
import tiktoken
print('✅ All core imports successful')
"
echo ""

# Success message
echo "================================"
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file and add your GROQ_API_KEY"
echo "   Get your key from: https://console.groq.com"
echo ""
echo "2. Run the application:"
echo "   streamlit run app.py"
echo ""
echo "3. Open your browser at:"
echo "   http://localhost:8501"
echo ""
echo "📖 For more information, see README.md"
echo "================================"
