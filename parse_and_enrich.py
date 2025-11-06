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

    def validate_vulnerability(self, vuln, filename):
        """Valide qu'une vulnérabilité contient toutes les informations requises avec qualité suffisante"""
        required_fields = ['title', 'severity', 'cvss_score', 'finding_type', 
                          'description', 'remediation', 'business_impact', 
                          'affected_assets', 'evidence']
        
        # Vérifier la présence de tous les champs
        for field in required_fields:
            if field not in vuln or not vuln[field]:
                print(f"   ⚠️  Champ manquant ou vide: {field}")
                return False
        
        # Valider la sévérité
        valid_severities = ['critical', 'high', 'medium', 'low']
        if vuln['severity'].lower() not in valid_severities:
            print(f"   ⚠️  Sévérité invalide: {vuln['severity']} (doit être: critical, high, medium, ou low)")
            return False
        
        # Normaliser la sévérité
        vuln['severity'] = vuln['severity'].lower()
        
        # Valider le score CVSS
        try:
            score = float(vuln['cvss_score'])
            if score < 0.0 or score > 10.0:
                print(f"   ⚠️  Score CVSS invalide: {score} (doit être entre 0.0 et 10.0)")
                return False
        except (ValueError, TypeError):
            print(f"   ⚠️  Score CVSS non numérique: {vuln['cvss_score']}")
            return False
        
        # Vérifier la longueur minimale des descriptions
        if len(str(vuln['description'])) < 100:
            print(f"   ⚠️  Description trop courte ({len(str(vuln['description']))} caractères, minimum 100)")
            return False
        
        if len(str(vuln['remediation'])) < 80:
            print(f"   ⚠️  Remédiation trop courte ({len(str(vuln['remediation']))} caractères, minimum 80)")
            return False
        
        if len(str(vuln['business_impact'])) < 50:
            print(f"   ⚠️  Impact métier trop court ({len(str(vuln['business_impact']))} caractères, minimum 50)")
            return False
        
        # Vérifier que affected_assets est une liste non vide
        if not isinstance(vuln['affected_assets'], list) or len(vuln['affected_assets']) == 0:
            print(f"   ⚠️  Liste des actifs affectés vide ou invalide")
            return False
        
        # Vérifier que cve_ids est une liste (peut être vide)
        if 'cve_ids' not in vuln:
            vuln['cve_ids'] = []
        if not isinstance(vuln['cve_ids'], list):
            vuln['cve_ids'] = []
        
        return True

    def send_to_ollama(self, raw_data, filename):
        """
        Envoie les données brutes à Ollama pour analyse intelligente.
        L'IA doit :
        1. Identifier si c'est une vulnérabilité
        2. Extraire les infos clés
        3. Générer description + remédiation
        """

        prompt = f"""Tu es un expert en cybersécurité et pentesting. Ton rôle est d'analyser des résultats de scans de sécurité et d'identifier les VRAIES vulnérabilités exploitables.

DONNÉES BRUTES À ANALYSER (fichier: {filename}):
{raw_data}

INSTRUCTIONS CRITIQUES:
1. Tu dois UNIQUEMENT retourner du JSON valide, sans aucun texte avant ou après
2. Analyse ATTENTIVEMENT les données pour identifier les vulnérabilités RÉELLES
3. NE PAS considérer comme vulnérabilité:
   - Les ports ouverts standards sans faille connue
   - Les services normaux sans version vulnérable
   - Les informations techniques sans risque réel
   - Les simples énumérations sans exploitation possible

4. CONSIDÉRER comme vulnérabilité:
   - Credentials valides découverts (passwords faibles, comptes compromis)
   - Services avec CVE connus et exploitables
   - Configurations dangereuses (SMB signing disabled, LDAP anonymous bind, etc.)
   - Failles d'authentification ou d'autorisation
   - Exposition de données sensibles
   - Possibilité d'élévation de privilèges
   - Chemins d'attaque exploitables

5. Pour CHAQUE vulnérabilité identifiée, tu DOIS fournir:
   - title: Titre clair et précis (max 100 caractères)
   - severity: "critical", "high", "medium", ou "low" (UNIQUEMENT ces valeurs)
   - cvss_score: Score CVSS v3.1 réaliste (0.0 à 10.0)
   - cve_ids: Liste des CVE si applicable (vide [] si aucun)
   - finding_type: Catégorie précise (ex: "Weak Credentials", "Misconfiguration", "Known Vulnerability", "Information Disclosure")
   - description: Analyse DÉTAILLÉE (minimum 200 caractères) expliquant:
     * Ce qui a été trouvé exactement
     * Pourquoi c'est une vulnérabilité
     * Comment cela peut être exploité
     * Le contexte technique complet
   - remediation: Plan de remédiation DÉTAILLÉ (minimum 150 caractères) avec:
     * Actions immédiates à prendre
     * Étapes de correction détaillées et numérotées
     * Recommandations de configuration
     * Meilleures pratiques de sécurité
   - business_impact: Impact métier CONCRET (minimum 100 caractères):
     * Conséquences pour l'entreprise
     * Risques financiers/réputationnels
     * Scénarios d'attaque réalistes
   - affected_assets: Liste PRÉCISE des assets affectés (IPs, hostnames, usernames, services)
   - evidence: Citation EXACTE de la preuve technique extraite des données brutes

6. ÉVALUATION DE LA CRITICITÉ:
   - critical (9.0-10.0): Exploitation immédiate possible, accès root/admin, RCE, compromission totale
   - high (7.0-8.9): Accès non autorisé, exfiltration de données, mouvement latéral
   - medium (4.0-6.9): Configuration faible, information disclosure, DoS
   - low (0.1-3.9): Informations mineures, hardening recommendations

7. Si AUCUNE vulnérabilité réelle n'est trouvée, retourne: {{"vulnerabilities": []}}

FORMAT JSON REQUIS (à respecter STRICTEMENT):
{{
  "vulnerabilities": [
    {{
      "title": "Titre clair et précis de la vulnérabilité",
      "severity": "critical",
      "cvss_score": 9.5,
      "cve_ids": ["CVE-2023-1234"],
      "finding_type": "Catégorie de la vulnérabilité",
      "description": "Description technique détaillée et complète de la vulnérabilité, expliquant le contexte, l'exploitation possible et les risques associés. Minimum 200 caractères.",
      "remediation": "1. Action immédiate requise\n2. Étape de correction détaillée\n3. Configuration recommandée\n4. Bonnes pratiques à suivre\n5. Mesures de prévention\nMinimum 150 caractères.",
      "business_impact": "Impact concret pour l'entreprise: description des conséquences métier, risques financiers, réputationnels et opérationnels. Scénarios d'attaque réalistes. Minimum 100 caractères.",
      "affected_assets": ["192.168.1.10", "user@domain.local", "hostname.domain"],
      "evidence": "Preuve technique exacte extraite des données brutes"
    }}
  ]
}}

RÉPONDS MAINTENANT (UNIQUEMENT LE JSON, RIEN D'AUTRE):"""

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": 0.2,  # Légèrement plus créatif pour les descriptions
                    "num_predict": 2000   # Augmenté pour des réponses plus détaillées
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
            vulnerabilities = result.get('vulnerabilities', [])
            
            # Valider chaque vulnérabilité
            validated_vulns = []
            for vuln in vulnerabilities:
                if self.validate_vulnerability(vuln, filename):
                    validated_vulns.append(vuln)
                else:
                    print(f"   ⚠️  Vulnérabilité rejetée car elle ne respecte pas les critères de qualité")
            
            return validated_vulns

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

                # Convertir en texte pour Ollama avec plus de contexte
                if parsed['type'] == 'json':
                    raw_text = json.dumps(parsed['content'], indent=2)[:8000]  # Augmenté de 3000 à 8000
                else:
                    raw_text = parsed['content'][:8000]  # Augmenté de 3000 à 8000

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
