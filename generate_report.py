#!/usr/bin/env python3
# generate_report.py

import json
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from typing import Dict, Any, List

class ReportGenerator:
    def __init__(self, config_path="config.yaml", findings_path="results/findings_enrichis.json"):
        self.config_path = config_path
        self.findings_path = findings_path
        self.config = self.load_config()
        self.findings_data = self.load_findings()
        self.validate_data()

    def load_config(self):
        """Charge la configuration depuis config.yaml"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def load_findings(self):
        """Charge les findings enrichis depuis le JSON"""
        with open(self.findings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate_data(self):
        """Valide que les données nécessaires sont présentes"""
        if 'findings' not in self.findings_data:
            print("⚠️  Attention: Aucun 'findings' trouvé dans le fichier JSON")
            self.findings_data['findings'] = []
        
        if 'summary' not in self.findings_data:
            print("⚠️  Génération du summary...")
            self.findings_data['summary'] = self._generate_summary()
        
        if 'statistics' not in self.findings_data:
            print("⚠️  Génération des statistiques...")
            self.findings_data['statistics'] = self._generate_statistics()
    
    def _generate_summary(self) -> Dict[str, int]:
        """Génère un summary à partir des findings"""
        findings = self.findings_data.get('findings', [])
        return {
            "total_findings": len(findings),
            "critical": len([f for f in findings if f.get('severity') == 'critical']),
            "high": len([f for f in findings if f.get('severity') == 'high']),
            "medium": len([f for f in findings if f.get('severity') == 'medium']),
            "low": len([f for f in findings if f.get('severity') == 'low']),
            "info": len([f for f in findings if f.get('severity') == 'info']),
        }
    
    def _generate_statistics(self) -> Dict[str, Any]:
        """Génère des statistiques à partir des findings"""
        findings = self.findings_data.get('findings', [])
        
        findings_by_tool = {}
        findings_by_type = {}
        
        for finding in findings:
            tool = finding.get('source_data', {}).get('tool', 'unknown')
            finding_type = finding.get('finding_type', 'unknown')
            
            findings_by_tool[tool] = findings_by_tool.get(tool, 0) + 1
            findings_by_type[finding_type] = findings_by_type.get(finding_type, 0) + 1
        
        return {
            "findings_by_tool": findings_by_tool,
            "findings_by_type": findings_by_type
        }

    def generate_html(self, output_path="output/rapport.html"):
        """Génère le rapport HTML à partir du template Jinja2"""

        # Configuration de Jinja2
        env = Environment(loader=FileSystemLoader('templates'))
        
        # Ajouter des filtres personnalisés
        def format_percentage(value):
            """Format a decimal as percentage"""
            return f"{int(value * 100)}%"
        
        env.filters['percentage'] = format_percentage
        
        template = env.get_template('rapport.html.j2')

        # Lire le CSS pour l'inclure inline
        css_content = ""
        css_path = Path("assets/style.css")
        if css_path.exists():
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
        else:
            print("⚠️  Fichier CSS non trouvé: assets/style.css")

        # Préparer les données pour le template
        context = {
            'audit_metadata': self.findings_data.get('audit_metadata', {}),
            'findings': self.findings_data.get('findings', []),
            'summary': self.findings_data.get('summary', {}),
            'statistics': self.findings_data.get('statistics', {}),
            'report_date': datetime.now().strftime("%Y-%m-%d"),
            'include_appendix': self.config.get('report', {}).get('include_appendix', True),
            'include_roadmap': self.config.get('report', {}).get('include_roadmap', True),
            'logo_path': self.config.get('report', {}).get('logo_path', ''),
            'css_content': css_content,
            'analyzer_version': self.findings_data.get('audit_metadata', {}).get('analyzer_version', '1.0'),
            'ai_model': self.findings_data.get('audit_metadata', {}).get('ai_model', 'Unknown')
        }

        # Mettre à jour les métadonnées depuis config si nécessaire
        if self.config.get('audit'):
            context['audit_metadata'].update({
                'client_name': self.config['audit'].get('client_name', context['audit_metadata'].get('client_name', 'À définir')),
                'audit_date': self.config['audit'].get('audit_date', context['audit_metadata'].get('audit_date', '')),
                'audit_end_date': self.config['audit'].get('audit_end_date', context['audit_metadata'].get('audit_end_date', '')),
                'audit_type': self.config['audit'].get('audit_type', context['audit_metadata'].get('audit_type', 'Pentest')),
                'scope': self.config['audit'].get('scope', context['audit_metadata'].get('scope', [])),
                'testeurs': self.config['audit'].get('testeurs', context['audit_metadata'].get('testeurs', [])),
                'contact_client': self.config['audit'].get('contact_client', context['audit_metadata'].get('contact_client', ''))
            })

        # Générer le HTML
        html_content = template.render(**context)

        # Sauvegarder le HTML
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Rapport HTML généré: {output_path}")
        return html_content

    def generate_pdf(self, html_content=None, output_path="output/rapport.pdf"):
        """Génère le rapport PDF à partir du HTML"""

        if html_content is None:
            # Générer d'abord le HTML si pas fourni
            html_content = self.generate_html()

        # Convertir HTML en PDF avec WeasyPrint
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Créer le PDF
        html = HTML(string=html_content, base_url='.')
        html.write_pdf(output_path)

        print(f"✅ Rapport PDF généré: {output_path}")

    def generate_reports(self):
        """Génère les rapports selon la configuration"""
        report_format = self.config.get('report', {}).get('format', 'both')
        output_dir = self.config.get('report', {}).get('output_dir', 'output')

        html_path = f"{output_dir}/rapport.html"
        pdf_path = f"{output_dir}/rapport.pdf"

        if report_format in ['html', 'both']:
            html_content = self.generate_html(html_path)
        else:
            html_content = None

        if report_format in ['pdf', 'both']:
            self.generate_pdf(html_content, pdf_path)

        # Display summary
        print("\n" + "="*60)
        print("📊 GÉNÉRATION DU RAPPORT TERMINÉE")
        print("="*60)
        print(f"Client: {self.findings_data.get('audit_metadata', {}).get('client_name', 'N/A')}")
        print(f"Type: {self.findings_data.get('audit_metadata', {}).get('audit_type', 'N/A')}")
        
        summary = self.findings_data.get('summary', {})
        print(f"\nTotal Findings: {summary.get('total_findings', 0)}")
        print(f"  🔴 Critical: {summary.get('critical', 0)}")
        print(f"  🟠 High: {summary.get('high', 0)}")
        print(f"  🟡 Medium: {summary.get('medium', 0)}")
        print(f"  🔵 Low: {summary.get('low', 0)}")
        print(f"  ⚪ Info: {summary.get('info', 0)}")
        
        # Display average confidence if available
        stats = self.findings_data.get('statistics', {})
        if 'average_confidence' in stats:
            avg_conf = stats['average_confidence']
            print(f"\n🎯 Confiance moyenne: {int(avg_conf * 100)}%")
        
        # Display analyzer info if available
        metadata = self.findings_data.get('audit_metadata', {})
        if 'analyzer_version' in metadata:
            print(f"\n🔧 Analyseur: v{metadata.get('analyzer_version', '1.0')}")
            print(f"🤖 Modèle IA: {metadata.get('ai_model', 'Unknown')}")
        
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description='Générer un rapport de pentest professionnel')
    parser.add_argument('--config', default='config.yaml', help='Chemin vers le fichier de configuration')
    parser.add_argument('--findings', default='results/findings_enrichis.json', help='Chemin vers le fichier findings JSON')
    parser.add_argument('--format', choices=['html', 'pdf', 'both'], help='Format du rapport (override config)')
    parser.add_argument('--output', help='Répertoire de sortie (override config)')

    args = parser.parse_args()

    # Générer le rapport
    generator = ReportGenerator(config_path=args.config, findings_path=args.findings)

    # Override config si arguments fournis
    if args.format:
        generator.config['report']['format'] = args.format
    if args.output:
        generator.config['report']['output_dir'] = args.output

    generator.generate_reports()


if __name__ == "__main__":
    main()
