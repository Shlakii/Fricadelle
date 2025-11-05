#!/usr/bin/env python3
# parse_and_enrich.py

import os
import json
import re
import ollama
from pathlib import Path
from datetime import datetime

class VulnerabilityAnalyzer:
    def __init__(self, scans_dir="results/scans", ollama_model="llama3.2"):
        self.scans_dir = scans_dir
        self.model = ollama_model
        self.findings = []
        self.findings_counter = 1
        
    def scan_directory(self):
        """Scanne le dossier et récupère tous les fichiers"""
        files = []
        for root, dirs, filenames in os.walk(self.scans_dir):
            for filename in filenames:
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
    
    def send_to_ollama(self, raw_data, filename):
        """
        Envoie les données brutes à Ollama pour analyse intelligente.
        L'IA doit :
        1. Identifier si c'est une vulnérabilité
        2. Extraire les infos clés
        3. Générer description + remédiation
        """
        
        prompt = f"""Tu es un expert en cybersécurité français. 

Analyse ce résultat de scan/test de pénétration (from {filename}):

{raw_data}

IMPORTANT: Réponds SEULEMENT si tu identifies au minimum UNE vulnérabilité ou problème de sécurité.
Si c'est juste une information technique sans risque (port ouvert sans service vulnerable, ping simple, etc), réponds: {{"vulnerabilities": []}}

Pour CHAQUE vulnérabilité identifiée, fournis une réponse JSON avec cette structure (en français):

{{
  "vulnerabilities": [
    {{
      "title": "Titre court et explicite",
      "severity": "critical|high|medium|low",
      "cvss_score": 7.5,
      "cve_ids": ["CVE-2023-12345"],
      "finding_type": "Type de finding (ex: Weak Credentials, Configuration Error, Known Vulnerability, etc.)",
      "description": "Description DÉTAILLÉE en français (2-3 paragraphes). Explique:\\n1. Qu'est-ce que c'est?\\n2. Pourquoi c'est un problème?\\n3. L'impact pour l'entreprise",
      "remediation": "Étapes concrètes et détaillées en français pour corriger:\\n1. Étape 1\\n2. Étape 2\\netc.",
      "business_impact": "Quel est l'impact métier? (accès non autorisé, perte de données, etc.)",
      "affected_assets": ["asset1", "asset2"],
      "evidence": "Snippet ou preuve courte du finding"
    }}
  ]
}}

Réponds EXCLUSIVEMENT en JSON valide. Pas de texte avant ni après."""

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )
            
            # Parse la réponse JSON
            result = json.loads(response['response'])
            return result.get('vulnerabilities', [])
        
        except json.JSONDecodeError:
            print(f"⚠️  Erreur parsing JSON de Ollama. Réponse brute:\n{response['response']}")
            return []
        except Exception as e:
            print(f"❌ Erreur Ollama: {e}")
            return []
    
    def process_all_files(self):
        """Traite tous les fichiers du dossier"""
        files = self.scan_directory()
        print(f"📁 Trouvé {len(files)} fichier(s)")
        
        for filepath in files:
            print(f"\n🔍 Traitement: {os.path.basename(filepath)}")
            
            try:
                parsed = self.parse_file(filepath)
                
                # Convertir en texte pour Ollama
                if parsed['type'] == 'json':
                    raw_text = json.dumps(parsed['content'], indent=2)[:2000]  # Limiter la taille
                else:
                    raw_text = parsed['content'][:2000]
                
                # Envoyer à Ollama
                vulnerabilities = self.send_to_ollama(raw_text, parsed['filename'])
                
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
                            "raw_output": raw_text
                        },
                        "affected_assets": vuln.get('affected_assets', []),
                        "evidence": vuln.get('evidence'),
                        "status": "open"
                    }
                    self.findings.append(finding)
                    self.findings_counter += 1
                    print(f"  ✅ Trouvé: {vuln.get('title')}")
            
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
        
        return self.findings
    
    def save_findings(self, output_file="results/findings_enrichis.json"):
        """Sauvegarde les findings en JSON"""
        
        # Calculer le summary
        summary = {
            "total_findings": len(self.findings),
            "critical": len([f for f in self.findings if f['severity'] == 'critical']),
            "high": len([f for f in self.findings if f['severity'] == 'high']),
            "medium": len([f for f in self.findings if f['severity'] == 'medium']),
            "low": len([f for f in self.findings if f['severity'] == 'low']),
        }
        
        # Calculer les statistiques par outil
        findings_by_tool = {}
        findings_by_type = {}
        
        for finding in self.findings:
            tool = finding.get('source_data', {}).get('tool', 'unknown')
            finding_type = finding.get('finding_type', 'unknown')
            
            findings_by_tool[tool] = findings_by_tool.get(tool, 0) + 1
            findings_by_type[finding_type] = findings_by_type.get(finding_type, 0) + 1
        
        output = {
            "audit_metadata": {
                "client_name": "À définir",
                "audit_date": datetime.now().strftime("%Y-%m-%d"),
                "audit_type": "Pentest",
                "scope": ["À définir"]
            },
            "findings": self.findings,
            "summary": summary,
            "statistics": {
                "findings_by_tool": findings_by_tool,
                "findings_by_type": findings_by_type
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Findings sauvegardés: {output_file}")
        print(f"📊 Total: {summary['total_findings']} findings (Critical: {summary['critical']}, High: {summary['high']})")


# Utilisation
if __name__ == "__main__":
    analyzer = VulnerabilityAnalyzer()
    analyzer.process_all_files()
    analyzer.save_findings()
