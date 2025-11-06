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

    def clean_json_response(self, response_text):
        """Nettoie la réponse Ollama en retirant les backticks markdown"""
        response_text = response_text.strip()

        # Retirer les backticks si présents
        if response_text.startswith('```'):
            # Trouver le premier { et le dernier }
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                response_text = response_text[start:end]

        return response_text

    def send_to_ollama(self, raw_data, filename):
        """
        Envoie les données brutes à Ollama pour analyse intelligente.
        L'IA doit :
        1. Identifier si c'est une vulnérabilité
        2. Extraire les infos clés
        3. Générer description + remédiation
        """

        prompt = f"""Tu es un analyste cybersécurité expert. Tu dois UNIQUEMENT retourner du JSON valide.

DONNÉES À ANALYSER (fichier: {filename}):
{raw_data}

CONSIGNES ABSOLUES:
- Réponds UNIQUEMENT en JSON
- PAS de texte explicatif
- PAS de "Bonjour", "Voici", "D'après"
- JUSTE le JSON brut

RÈGLES DE DÉTECTION:
1. Identifie si c'est bien une vulnérabilité.
2. Si rien de critique, retourne: {{"vulnerabilities": []}}

EXEMPLE DE FORMAT JSON REQUIS (COPIE LE FORMAT MAIS ADAPTE LE CONTENU PAR RAPPORT A LA VULNERABILITE TROUVEE):
{{
  "vulnerabilities": [
    {{
      "title": "Titre",
      "severity": "Niveau de sévérité",
      "cvss_score": Score CVSS,
      "cve_ids": [],
      "finding_type": "Type de vulnérabilité",
      "description": "Description détaillée de la vulnérabilité",
      "remediation": "Explication du ou des moyens de remédiations",
      "business_impact": "Description de l'impact métier",
      "affected_assets": ["Asset affecté par la vulnérabilité"],
      "evidence": "Preuve que la vulnérabilité existe"
    }}
  ]
}}

RÉPONDS MAINTENANT (UNIQUEMENT JSON):"""

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": 0.1,  # Rendre l'IA plus déterministe
                    "num_predict": 800   # Limiter la longueur
                }
            )

            response_text = response['response'].strip()

            # Nettoyer la réponse
            cleaned_response = self.clean_json_response(response_text)

            # Si la réponse ne commence pas par {, c'est probablement du texte
            if not cleaned_response.startswith('{'):
                print(f"⚠️  L'IA a répondu en texte au lieu de JSON pour {filename}")
                print(f"   Essai de récupération...")
                # Chercher le JSON dans la réponse
                start = cleaned_response.find('{')
                end = cleaned_response.rfind('}') + 1
                if start != -1 and end > start:
                    cleaned_response = cleaned_response[start:end]
                else:
                    return []

            # Parse la réponse JSON
            result = json.loads(cleaned_response)
            return result.get('vulnerabilities', [])

        except json.JSONDecodeError:
            print(f"⚠️  Erreur parsing JSON de Ollama pour {filename}")
            print(f"Réponse brute:\n{response['response'][:500]}...")
            return []
        except Exception as e:
            print(f"❌ Erreur Ollama: {e}")
            return []

    def process_all_files(self):
        """Traite tous les fichiers du dossier"""
        files = self.scan_directory()
        print(f"📁 Trouvé {len(files)} fichier(s)\n")

        for filepath in files:
            print(f"🔍 Traitement: {os.path.basename(filepath)}")

            try:
                parsed = self.parse_file(filepath)

                # Convertir en texte pour Ollama
                if parsed['type'] == 'json':
                    raw_text = json.dumps(parsed['content'], indent=2)[:3000]
                else:
                    raw_text = parsed['content'][:3000]

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
                            "raw_output": raw_text[:500]  # Limiter la taille
                        },
                        "affected_assets": vuln.get('affected_assets', []),
                        "evidence": vuln.get('evidence'),
                        "status": "open"
                    }
                    self.findings.append(finding)
                    self.findings_counter += 1
                    print(f"  ✅ {vuln.get('severity').upper()}: {vuln.get('title')}")

                if not vulnerabilities:
                    print(f"  ℹ️  Aucune vulnérabilité détectée")

            except Exception as e:
                print(f"  ❌ Erreur: {e}")

            print()  # Ligne vide pour lisibilité

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

        print("="*60)
        print(f"✅ Findings sauvegardés: {output_file}")
        print(f"📊 Total: {summary['total_findings']} findings")
        print(f"   🔴 Critical: {summary['critical']}")
        print(f"   🟠 High: {summary['high']}")
        print(f"   🟡 Medium: {summary['medium']}")
        print(f"   🔵 Low: {summary['low']}")
        print("="*60)


# Utilisation
if __name__ == "__main__":
    analyzer = VulnerabilityAnalyzer()
    analyzer.process_all_files()
    analyzer.save_findings()
