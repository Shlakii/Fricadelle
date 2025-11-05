#!/usr/bin/env python3
# generate_report.py

import json
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

class ReportGenerator:
    def __init__(self, config_path="config.yaml", findings_path="results/findings_enrichis.json"):
        self.config_path = config_path
        self.findings_path = findings_path
        self.config = self.load_config()
        self.findings_data = self.load_findings()
        
    def load_config(self):
        """Charge la configuration depuis config.yaml"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_findings(self):
        """Charge les findings enrichis depuis le JSON"""
        with open(self.findings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_html(self, output_path="output/rapport.html"):
        """Génère le rapport HTML à partir du template Jinja2"""
        
        # Configuration de Jinja2
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('rapport.html.j2')
        
        # Préparer les données pour le template
        context = {
            'audit_metadata': self.findings_data.get('audit_metadata', {}),
            'findings': self.findings_data.get('findings', []),
            'summary': self.findings_data.get('summary', {}),
            'statistics': self.findings_data.get('statistics', {}),
            'report_date': datetime.now().strftime("%Y-%m-%d"),
            'include_appendix': self.config.get('report', {}).get('include_appendix', True),
            'include_roadmap': self.config.get('report', {}).get('include_roadmap', True),
            'logo_path': self.config.get('report', {}).get('logo_path', '')
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
        
        print("\n" + "="*60)
        print("📊 GÉNÉRATION DU RAPPORT TERMINÉE")
        print("="*60)
        print(f"Client: {self.findings_data.get('audit_metadata', {}).get('client_name', 'N/A')}")
        print(f"Total Findings: {self.findings_data.get('summary', {}).get('total_findings', 0)}")
        print(f"  - Critical: {self.findings_data.get('summary', {}).get('critical', 0)}")
        print(f"  - High: {self.findings_data.get('summary', {}).get('high', 0)}")
        print(f"  - Medium: {self.findings_data.get('summary', {}).get('medium', 0)}")
        print(f"  - Low: {self.findings_data.get('summary', {}).get('low', 0)}")
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