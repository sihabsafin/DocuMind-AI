# ⚡ Quick Start Guide - DocuMind AI

Get started with DocuMind AI in 5 minutes!

---

## 🎯 What You'll Need

1. **Python 3.11+** installed
2. **Groq API Key** (free from [console.groq.com](https://console.groq.com))
3. **5 minutes** of your time

---

## 🚀 Installation (3 Steps)

### Step 1: Clone & Navigate
```bash
git clone <repository-url>
cd documind-ai
```

### Step 2: Run Setup Script
```bash
# Make script executable (Linux/Mac)
chmod +x setup.sh
./setup.sh

# Or manually:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Configure API Key
```bash
# Edit .env file
nano .env  # or use your favorite editor

# Add your Groq API key:
GROQ_API_KEY=your_key_here
```

**Get your free Groq API key:**
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up (it's free!)
3. Go to API Keys
4. Create new key
5. Copy and paste into `.env`

---

## ▶️ Run the App

```bash
streamlit run app.py
```

Your browser will automatically open to `http://localhost:8501`

---

## 📖 Using DocuMind AI

### 1️⃣ Upload Your Document
- Click "Browse files" or drag & drop
- Supported formats: PDF, DOCX, TXT, Markdown
- Max size: 50 MB (configurable)

### 2️⃣ Configure (Optional)
**Sidebar Settings:**
- **Model**: Choose AI model (default: gemma2-9b-it)
- **Style**: Pick writing style (technical, simple, executive, etc.)
- **Quality**: Balance speed vs quality (fast, balanced, premium)

**Advanced Settings:**
- Chunk Size: 1000 tokens (default)
- Chunk Overlap: 200 tokens (default)

### 3️⃣ Process
Click **"🚀 Process & Summarize"**

Watch the progress:
1. 📖 Processing document
2. ✂️ Chunking text
3. 🤖 Generating summaries

### 4️⃣ Review Results
**Four summary levels automatically generated:**

📍 **TL;DR Tab**
- Ultra-concise 1-2 sentence overview
- Perfect for quick understanding

📍 **Bullet Points Tab**
- 5-7 key points
- Structured and scannable

📍 **Executive Tab**
- Professional business summary
- Includes context and recommendations

📍 **Detailed Tab**
- Comprehensive analysis
- Preserves structure and nuance

### 5️⃣ Export
Download your summaries in:
- 📄 Markdown (.md)
- 📝 Plain Text (.txt)
- 🔧 JSON (.json)

---

## 💡 Example Workflow

```bash
# 1. Start the app
streamlit run app.py

# 2. In the browser:
#    - Upload: research_paper.pdf
#    - Style: Academic
#    - Quality: Premium
#    - Click: Process & Summarize

# 3. Wait ~30 seconds for 20-page paper

# 4. Review summaries:
#    - TL;DR: "This paper presents..."
#    - Executive: Full context summary
#    - Detailed: Section-by-section analysis

# 5. Export: Download as Markdown
```

---

## 🎨 Customization Tips

### Change Default Model
Edit `.env`:
```env
DEFAULT_MODEL=llama-3.1-70b-versatile  # Higher quality
# or
DEFAULT_MODEL=llama-3.1-8b-instant     # Faster
```

### Adjust Processing
```env
CHUNK_SIZE=1500          # Larger chunks (slower, better context)
CHUNK_OVERLAP=300        # More overlap (better coherence)
MAX_FILE_SIZE_MB=100     # Allow larger files
```

### Summary Styles Explained

| Style | Best For | Example Use |
|-------|----------|-------------|
| **Technical** | Engineers, researchers | Technical documentation |
| **Simple** | General audience | Blog posts, reports |
| **Executive** | Business leaders | Board reports, memos |
| **Academic** | Researchers, students | Research papers |
| **Legal** | Legal professionals | Contracts, legal docs |

---

## 🔍 Advanced Features

### Section-Specific Summarization
*Coming soon!*
```python
# Select specific sections
summarizer.summarize_section("Methodology")
summarizer.summarize_section("Conclusion")
```

### Multi-Document Processing
*Coming soon!*
```python
# Compare multiple documents
summarizer.compare_documents([doc1, doc2, doc3])
```

### Research Agent
*Coming soon!*
```python
# Search and summarize from the web
agent.research("AI summarization techniques 2024")
```

---

## 🐛 Troubleshooting

**Problem: "ModuleNotFoundError"**
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt
```

**Problem: "API key not found"**
```bash
# Solution: Check .env file
cat .env | grep GROQ_API_KEY

# Make sure it's set correctly
GROQ_API_KEY=gsk_...
```

**Problem: App is slow**
```bash
# Solution 1: Use faster model
DEFAULT_MODEL=llama-3.1-8b-instant

# Solution 2: Reduce chunk size
CHUNK_SIZE=500
```

**Problem: Out of memory**
```bash
# Solution: Reduce max file size
MAX_FILE_SIZE_MB=25
MAX_PAGES=500
```

---

## 📱 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + R` | Refresh app |
| `Ctrl/Cmd + K` | Clear cache |
| `Ctrl/Cmd + /` | Show shortcuts |

---

## 🎓 Learning Resources

### Understanding the Technology

**What is Map-Reduce?**
- Splits document into chunks
- Summarizes each chunk independently
- Combines summaries intelligently
- Best for long documents

**What is Refine Strategy?**
- Starts with first chunk
- Iteratively refines with each new chunk
- Higher quality, slower
- Best for premium summaries

**What is Groq?**
- Lightning-fast AI inference
- Free tier available
- Runs Gemma-2, LLaMA-3 models
- Much faster than standard APIs

### Sample Documents to Try

1. **Research Paper** (PDF)
   - Test academic style
   - Try detailed summary

2. **Business Report** (DOCX)
   - Test executive style
   - Compare summary levels

3. **Technical Documentation** (Markdown)
   - Test technical style
   - Check section preservation

---

## ✅ Next Steps

1. ✅ Run your first document
2. 📊 Try different styles
3. 🎯 Test various document types
4. 💾 Export and share
5. ⭐ Star the repo!

---

## 🆘 Getting Help

**Quick Questions:**
- Check [README.md](README.md)
- Review [DEPLOYMENT.md](DEPLOYMENT.md)

**Issues:**
- GitHub Issues: [Create an issue](https://github.com/yourusername/documind-ai/issues)

**Community:**
- Discord: [Join community](https://discord.gg/documind)
- Email: support@documind.ai

---

## 🎉 You're Ready!

**Start summarizing documents like a pro!**

```bash
streamlit run app.py
```

Happy summarizing! 📄✨
