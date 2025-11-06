#!/bin/bash
# example_usage.sh - Example workflow for using Fricadelle

echo "🍔 Fricadelle - Pentest Report Generator"
echo "=========================================="
echo ""

# Step 1: Setup
echo "📁 Step 1: Setting up directories..."
mkdir -p results/scans output
echo "   ✅ Directories created"
echo ""

# Step 2: Install best AI model
echo "🤖 Step 2: Installing recommended AI model..."
echo "   Run: ollama pull qwen2.5:14b"
echo "   (Or use default: ollama pull llama3.2)"
echo ""

# Step 3: Place any type of file
echo "📥 Step 3: Place ANY type of file in results/scans/"
echo "   Fricadelle accepts:"
echo "   ✅ Automated scans (nmap JSON, nuclei, etc.)"
echo "   ✅ Command outputs (kerbrute, crackmapexec, etc.)"
echo "   ✅ Manual notes (observations.txt)"
echo "   ✅ Simple messages (findings.txt)"
echo "   ✅ Any format: JSON, XML, CSV, YAML, TXT, etc."
echo ""
echo "   Examples:"
echo "   - cp nmap_scan.json results/scans/"
echo "   - cp kerbrute_output.txt results/scans/"
echo "   - echo 'SMB signing disabled on DC01' > results/scans/note.txt"
echo ""
echo "   ⚠️  Make sure Ollama is running: ollama serve"
echo ""

# Step 4: Update config
echo "⚙️  Step 4: Update config.yaml with your client information"
echo "   Edit: audit.client_name, audit.scope, audit.testeurs, etc."
echo ""

# Step 5: Parse and enrich with best model
echo "🔍 Step 5: Analyze with AI (RECOMMENDED: use qwen2.5:14b)"
echo "   Run: python parse_and_enrich.py --model qwen2.5:14b"
echo "   OR:  python parse_and_enrich.py  (uses default model)"
echo ""
echo "   This will:"
echo "   - Scan ALL files in results/scans/ (ANY format)"
echo "   - Detect encoding automatically"
echo "   - Send each to Ollama for intelligent analysis"
echo "   - Extract real vulnerabilities (not just info)"
echo "   - Validate quality (min. 100 char descriptions)"
echo "   - Generate results/findings_enrichis.json"
echo ""
echo "   Options:"
echo "   --model qwen2.5:14b    Use best model for security analysis"
echo "   --quiet                Reduce verbosity"
echo "   --scans-dir /path      Use custom scans directory"
echo "   --output custom.json   Custom output file"
echo "   --help                 See all options and recommended models"
echo ""

# Step 6: Generate report
echo "📊 Step 6: Generate the professional PDF report"
echo "   Run: python generate_report.py"
echo "   This will create:"
echo "   - output/rapport.pdf (professional PDF report)"
echo ""
echo "   Options:"
echo "   --findings custom.json    Use custom findings file"
echo "   --output /path            Custom output directory"
echo ""

echo "✨ That's it! Your professional pentest report is ready."
echo ""
echo "💡 Tips:"
echo "   - See AI_MODELS_GUIDE.md for best AI model recommendations"
echo "   - Use qwen2.5:14b for highest quality analysis (recommended)"
echo "   - Mix automated scans with manual notes - it all works!"
echo "   - Edit fricadelle_config.yaml to customize AI parameters"
echo "   - Edit templates/rapport.html.j2 to customize the report"
echo "   - Edit assets/style.css to change the styling"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Full documentation"
echo "   - AI_MODELS_GUIDE.md - AI model comparison and recommendations"
echo "   - QUICKSTART.md - Quick start guide"
echo "   - ARCHITECTURE.md - Technical architecture"
echo ""
