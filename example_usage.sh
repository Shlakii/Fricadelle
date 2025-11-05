#!/bin/bash
# example_usage.sh - Example workflow for using Fricadelle

echo "🛡️  Fricadelle - Pentest Report Generator"
echo "=========================================="
echo ""

# Step 1: Setup
echo "📁 Step 1: Setting up directories..."
mkdir -p results/scans output
echo "   ✅ Directories created"
echo ""

# Step 2: Place scan results (this is manual)
echo "📥 Step 2: Place your scan results in results/scans/"
echo "   Examples:"
echo "   - cp nmap_scan.json results/scans/"
echo "   - cp kerbrute_output.txt results/scans/"
echo "   - cp crackmapexec.txt results/scans/"
echo ""
echo "   ⚠️  Make sure Ollama is running: ollama serve"
echo ""

# Step 3: Update config
echo "⚙️  Step 3: Update config.yaml with your client information"
echo "   Edit: audit.client_name, audit.scope, audit.testeurs, etc."
echo ""

# Step 4: Parse and enrich (commented out as it requires Ollama)
echo "🤖 Step 4: Parse scan results and enrich with AI analysis"
echo "   Run: python parse_and_enrich.py"
echo "   This will:"
echo "   - Scan all files in results/scans/"
echo "   - Send each to Ollama for AI analysis"
echo "   - Extract vulnerabilities"
echo "   - Generate results/findings_enrichis.json"
echo ""

# Step 5: Generate report
echo "📊 Step 5: Generate the professional report"
echo "   Run: python generate_report.py --config config.yaml"
echo "   This will create:"
echo "   - output/rapport.html (interactive HTML report)"
echo "   - output/rapport.pdf (professional PDF report)"
echo ""

echo "✨ That's it! Your professional pentest report is ready."
echo ""
echo "💡 Tips:"
echo "   - Use --format html to generate only HTML"
echo "   - Use --format pdf to generate only PDF"
echo "   - Edit templates/rapport.html.j2 to customize the report"
echo "   - Edit assets/style.css to change the styling"
