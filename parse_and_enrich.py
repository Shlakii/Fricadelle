#!/usr/bin/env python3
# parse_and_enrich.py

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from ai_analyzer import AIAnalyzer

class VulnerabilityAnalyzer:
    def __init__(self, scans_dir="results/scans", ollama_model="llama3.2", enable_validation=True):
        self.scans_dir = scans_dir
        self.model = ollama_model
        self.findings = []
        self.findings_counter = 1
        self.enable_validation = enable_validation
        self.analyzer = AIAnalyzer(model=ollama_model)
        self.analysis_errors = []

    def scan_directory(self):
        """Scanne le dossier et récupère tous les fichiers"""
        files = []
        for root, dirs, filenames in os.walk(self.scans_dir):
            for filename in filenames:
                # Ignorer les fichiers cachés et .gitkeep
                if not filename.startswith('.') and filename != '.gitkeep':
                    files.append(os.path.join(root, filename))
        return files

    def parse_file(self, filepath):
        """Parse un fichier selon son type"""
        filename = os.path.basename(filepath)

        if filepath.endswith('.json'):
            with open(filepath, encoding='utf-8') as f:
                return {"type": "json", "content": json.load(f), "filename": filename}

        elif filepath.endswith('.csv'):
            with open(filepath, encoding='utf-8') as f:
                return {"type": "csv", "content": f.read(), "filename": filename}

        else:  # Fichier texte brut
            with open(filepath, encoding='utf-8') as f:
                return {"type": "text", "content": f.read(), "filename": filename}

    def analyze_with_ai(self, raw_data: str, filename: str) -> List[Dict[str, Any]]:
        """
        Analyze scan data using the improved AI analyzer.
        
        Args:
            raw_data: Raw scan data to analyze
            filename: Name of the scan file
            
        Returns:
            List of validated vulnerabilities
        """
        try:
            # Use the improved AI analyzer
            vulnerabilities, errors = self.analyzer.analyze_scan_data(
                raw_data=raw_data,
                filename=filename,
                validate=self.enable_validation
            )
            
            # Track any errors
            if errors:
                self.analysis_errors.extend(errors)
                for error in errors:
                    print(f"  ⚠️  {error}")
            
            # Enrich each vulnerability
            enriched_vulns = []
            for vuln in vulnerabilities:
                enriched = self.analyzer.enrich_vulnerability(vuln)
                enriched_vulns.append(enriched)
            
            return enriched_vulns
            
        except Exception as e:
            error_msg = f"Error analyzing {filename}: {str(e)}"
            self.analysis_errors.append(error_msg)
            print(f"  ❌ {error_msg}")
            return []

    def process_all_files(self):
        """Traite tous les fichiers du dossier avec l'analyseur amélioré"""
        files = self.scan_directory()
        print(f"📁 Trouvé {len(files)} fichier(s) à analyser\n")
        
        if not files:
            print("⚠️  Aucun fichier trouvé dans results/scans/")
            print("   Placez vos fichiers de scan dans ce dossier et relancez.")
            return self.findings

        for filepath in files:
            print(f"🔍 Analyse: {os.path.basename(filepath)}")

            try:
                parsed = self.parse_file(filepath)

                # Convertir en texte pour l'analyseur
                if parsed['type'] == 'json':
                    raw_text = json.dumps(parsed['content'], indent=2)[:4000]
                else:
                    raw_text = parsed['content'][:4000]

                # Analyser avec le nouvel analyseur IA
                vulnerabilities = self.analyze_with_ai(raw_text, parsed['filename'])

                # Ajouter aux findings
                for vuln in vulnerabilities:
                    finding = {
                        "id": f"VULN-{str(self.findings_counter).zfill(3)}",
                        "title": vuln.get('title'),
                        "severity": vuln.get('severity'),
                        "cvss_score": vuln.get('cvss_score'),
                        "cve_ids": vuln.get('cve_ids', []),
                        "finding_type": vuln.get('finding_type'),
                        "description": vuln.get('description'),
                        "remediation": vuln.get('remediation'),
                        "business_impact": vuln.get('business_impact'),
                        "source_data": {
                            "tool": parsed['filename'],
                            "raw_output": raw_text[:500]  # Limiter la taille
                        },
                        "affected_assets": vuln.get('affected_assets', []),
                        "evidence": vuln.get('evidence'),
                        "confidence_score": vuln.get('confidence_score', 0.7),
                        "exploitation_complexity": vuln.get('exploitation_complexity', 'medium'),
                        "status": "open"
                    }
                    self.findings.append(finding)
                    
                    # Display with confidence indicator
                    confidence = vuln.get('confidence_score', 0.7)
                    confidence_icon = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
                    
                    print(f"  ✅ {vuln.get('severity', 'unknown').upper()}: {vuln.get('title')} "
                          f"{confidence_icon} (confiance: {confidence:.0%})")
                    self.findings_counter += 1

                if not vulnerabilities:
                    print(f"  ℹ️  Aucune vulnérabilité détectée")

            except Exception as e:
                error_msg = f"Erreur lors du traitement de {filepath}: {str(e)}"
                print(f"  ❌ {error_msg}")
                self.analysis_errors.append(error_msg)

            print()  # Ligne vide pour lisibilité

        return self.findings

    def save_findings(self, output_file="results/findings_enrichis.json"):
        """Sauvegarde les findings enrichis en JSON avec métadonnées complètes"""

        # Calculer le summary
        summary = {
            "total_findings": len(self.findings),
            "critical": len([f for f in self.findings if f['severity'] == 'critical']),
            "high": len([f for f in self.findings if f['severity'] == 'high']),
            "medium": len([f for f in self.findings if f['severity'] == 'medium']),
            "low": len([f for f in self.findings if f['severity'] == 'low']),
            "info": len([f for f in self.findings if f['severity'] == 'info']),
        }

        # Calculer les statistiques par outil
        findings_by_tool = {}
        findings_by_type = {}
        avg_confidence = 0.0

        for finding in self.findings:
            tool = finding.get('source_data', {}).get('tool', 'unknown')
            finding_type = finding.get('finding_type', 'unknown')
            confidence = finding.get('confidence_score', 0.7)

            findings_by_tool[tool] = findings_by_tool.get(tool, 0) + 1
            findings_by_type[finding_type] = findings_by_type.get(finding_type, 0) + 1
            avg_confidence += confidence

        if self.findings:
            avg_confidence /= len(self.findings)

        # Créer l'output enrichi
        output = {
            "audit_metadata": {
                "client_name": "À définir dans config.yaml",
                "audit_date": datetime.now().strftime("%Y-%m-%d"),
                "audit_type": "Pentest",
                "scope": ["À définir dans config.yaml"],
                "generation_date": datetime.now().isoformat(),
                "analyzer_version": "2.0",
                "ai_model": self.model
            },
            "findings": self.findings,
            "summary": summary,
            "statistics": {
                "findings_by_tool": findings_by_tool,
                "findings_by_type": findings_by_type,
                "average_confidence": round(avg_confidence, 2),
                "total_errors": len(self.analysis_errors)
            },
            "analysis_errors": self.analysis_errors if self.analysis_errors else []
        }

        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print("="*60)
        print(f"✅ Findings sauvegardés: {output_file}")
        print(f"📊 Total: {summary['total_findings']} findings")
        print(f"   🔴 Critical: {summary['critical']}")
        print(f"   🟠 High: {summary['high']}")
        print(f"   🟡 Medium: {summary['medium']}")
        print(f"   🔵 Low: {summary['low']}")
        print(f"   ⚪ Info: {summary['info']}")
        print(f"   🎯 Confiance moyenne: {avg_confidence:.0%}")
        if self.analysis_errors:
            print(f"   ⚠️  Erreurs d'analyse: {len(self.analysis_errors)}")
        print("="*60)


# Utilisation
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyser les scans de sécurité avec IA améliorée',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python parse_and_enrich.py
  python parse_and_enrich.py --scans-dir /path/to/scans
  python parse_and_enrich.py --model llama3.2 --no-validation
  python parse_and_enrich.py --output custom_findings.json
        """
    )
    
    parser.add_argument(
        '--scans-dir',
        default='results/scans',
        help='Répertoire contenant les fichiers de scan (défaut: results/scans)'
    )
    
    parser.add_argument(
        '--model',
        default='llama3.2',
        help='Modèle Ollama à utiliser (défaut: llama3.2)'
    )
    
    parser.add_argument(
        '--output',
        default='results/findings_enrichis.json',
        help='Fichier de sortie pour les findings (défaut: results/findings_enrichis.json)'
    )
    
    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='Désactiver la validation des vulnérabilités par l\'IA'
    )
    
    args = parser.parse_args()
    
    print("🛡️  Fricadelle - Analyseur de Vulnérabilités Amélioré")
    print("="*60)
    print(f"📁 Répertoire de scans: {args.scans_dir}")
    print(f"🤖 Modèle IA: {args.model}")
    print(f"✅ Validation: {'Activée' if not args.no_validation else 'Désactivée'}")
    print("="*60)
    print()
    
    analyzer = VulnerabilityAnalyzer(
        scans_dir=args.scans_dir,
        ollama_model=args.model,
        enable_validation=not args.no_validation
    )
    
    analyzer.process_all_files()
    analyzer.save_findings(args.output)
