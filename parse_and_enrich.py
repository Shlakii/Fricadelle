#!/usr/bin/env python3
# parse_and_enrich.py

import os
import json
import re
import ollama
import chardet
import yaml
from pathlib import Path
from datetime import datetime

class VulnerabilityAnalyzer:
    def __init__(self, scans_dir="results/scans", ollama_model="llama3.2", verbose=True):
        self.scans_dir = scans_dir
        self.model = ollama_model
        self.findings = []
        self.findings_counter = 1
        self.verbose = verbose
        self.processed_files = []
        self.skipped_files = []
        self.errors = []

    def log(self, message, level="INFO"):
        """Log avec niveau de verbosité"""
        if self.verbose:
            prefix = {
                "INFO": "ℹ️",
                "SUCCESS": "✅",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "DEBUG": "🔍"
            }.get(level, "ℹ️")
            print(f"{prefix} {message}")

    def scan_directory(self):
        """Scanne le dossier et récupère tous les fichiers"""
        files = []
        for root, dirs, filenames in os.walk(self.scans_dir):
            for filename in filenames:
                # Ignorer les fichiers cachés, .gitkeep, et README
                if not filename.startswith('.') and filename.lower() not in ['.gitkeep', 'readme.txt', 'readme.md']:
                    files.append(os.path.join(root, filename))
        return files

    def detect_encoding(self, filepath):
        """Détecte l'encodage d'un fichier"""
        try:
            with open(filepath, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except:
            return 'utf-8'

    def parse_file(self, filepath):
        """Parse un fichier selon son type avec détection d'encodage automatique"""
        filename = os.path.basename(filepath)
        
        # Détecter l'encodage
        encoding = self.detect_encoding(filepath)
        self.log(f"Encodage détecté pour {filename}: {encoding}", "DEBUG")

        try:
            # Essayer de parser comme JSON d'abord
            if filepath.endswith('.json'):
                try:
                    with open(filepath, encoding=encoding) as f:
                        content = json.load(f)
                        return {"type": "json", "content": content, "filename": filename}
                except json.JSONDecodeError:
                    # Si le JSON est invalide, le traiter comme du texte
                    self.log(f"Fichier {filename} n'est pas un JSON valide, traité comme texte", "WARNING")
                    with open(filepath, encoding=encoding) as f:
                        return {"type": "text", "content": f.read(), "filename": filename}

            # Essayer CSV
            elif filepath.endswith('.csv'):
                with open(filepath, encoding=encoding) as f:
                    return {"type": "csv", "content": f.read(), "filename": filename}

            # Essayer XML
            elif filepath.endswith('.xml'):
                with open(filepath, encoding=encoding) as f:
                    return {"type": "xml", "content": f.read(), "filename": filename}

            # YAML
            elif filepath.endswith(('.yml', '.yaml')):
                try:
                    with open(filepath, encoding=encoding) as f:
                        content = yaml.safe_load(f)
                        return {"type": "yaml", "content": content, "filename": filename}
                except:
                    with open(filepath, encoding=encoding) as f:
                        return {"type": "text", "content": f.read(), "filename": filename}

            # Fichier texte brut (défaut pour tout le reste)
            else:
                with open(filepath, encoding=encoding) as f:
                    return {"type": "text", "content": f.read(), "filename": filename}
                    
        except Exception as e:
            self.log(f"Erreur lors du parsing de {filename}: {e}", "ERROR")
            # Tentative de lecture brute en dernier recours
            try:
                with open(filepath, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    return {"type": "text", "content": content, "filename": filename}
            except:
                raise

    def clean_json_response(self, response_text):
        """Nettoie la réponse Ollama en retirant les backticks markdown et en corrigeant les newlines mal échappées"""
        response_text = response_text.strip()

        # Retirer les backticks si présents
        if response_text.startswith('```'):
            # Trouver le premier { et le dernier }
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                response_text = response_text[start:end]

        # Corriger les newlines non échappées dans les strings JSON
        # On cherche les patterns où il y a un newline literal dans une string
        # Pattern: "texte\n texte" (newline literal) -> "texte\\n texte" (newline échappé)

        # Approche: on traite ligne par ligne et on détecte si on est dans une string
        lines = response_text.split('\n')
        result = []
        in_string = False

        for line in lines:
            # Compter les quotes non échappées
            i = 0
            while i < len(line):
                if line[i] == '"' and (i == 0 or line[i-1] != '\\'):
                    in_string = not in_string
                i += 1

            # Si on était en string et on continue, ajouter \\n
            if in_string and result:
                result[-1] += '\\n' + line
            else:
                result.append(line)

        return '\n'.join(result)

    def validate_vulnerability(self, vuln, filename):
        """Valide qu'une vulnérabilité contient toutes les informations requises avec qualité suffisante"""

        # Champs CRITIQUES (obligatoires et strictes)
        critical_fields = ['title', 'severity', 'cvss_score', 'finding_type',
                          'description', 'remediation', 'business_impact']

        # Champs FLEXIBLES (optionnels ou avec validation légère)
        flexible_fields = {
            'affected_assets': [],
            'evidence': 'Evidence non disponible',
            'cve_ids': []
        }

        # Vérifier les champs CRITIQUES
        for field in critical_fields:
            if field not in vuln or vuln[field] is None:
                self.log(f"Champ critique manquant pour {filename}: {field}", "WARNING")
                return False

            value = vuln[field]
            if isinstance(value, str) and not value.strip():
                self.log(f"Champ critique vide pour {filename}: {field}", "WARNING")
                return False

        # Valider la sévérité
        valid_severities = ['critical', 'high', 'medium', 'low']
        if vuln['severity'].lower() not in valid_severities:
            self.log(f"Sévérité invalide pour {filename}: {vuln['severity']} (doit être: critical, high, medium, ou low)", "WARNING")
            return False

        # Normaliser la sévérité
        vuln['severity'] = vuln['severity'].lower()

        # Valider le score CVSS
        try:
            score = float(vuln['cvss_score'])
            if score < 0.0 or score > 10.0:
                self.log(f"Score CVSS invalide pour {filename}: {score} (doit être entre 0.0 et 10.0)", "WARNING")
                return False
        except (ValueError, TypeError):
            self.log(f"Score CVSS non numérique pour {filename}: {vuln['cvss_score']}", "WARNING")
            return False

        # Vérifier la longueur minimale des descriptions CRITIQUES
        if len(str(vuln['description']).strip()) < 100:
            self.log(f"Description trop courte pour {filename} ({len(str(vuln['description']).strip())} caractères, minimum 100)", "WARNING")
            return False

        if len(str(vuln['remediation']).strip()) < 80:
            self.log(f"Remédiation trop courte pour {filename} ({len(str(vuln['remediation']).strip())} caractères, minimum 80)", "WARNING")
            return False

        if len(str(vuln['business_impact']).strip()) < 50:
            self.log(f"Impact métier trop court pour {filename} ({len(str(vuln['business_impact']).strip())} caractères, minimum 50)", "WARNING")
            return False

        # Traiter les champs FLEXIBLES
        # affected_assets : peut être vide, sinon doit être une liste
        if 'affected_assets' not in vuln:
            vuln['affected_assets'] = []
        elif not isinstance(vuln['affected_assets'], list):
            vuln['affected_assets'] = []

        # evidence : peut être vide ou très court, on le met par défaut si manquant
        if 'evidence' not in vuln or not vuln['evidence']:
            vuln['evidence'] = 'Evidence non disponible'

        # cve_ids : doit être une liste (peut être vide)
        if 'cve_ids' not in vuln:
            vuln['cve_ids'] = []
        elif not isinstance(vuln['cve_ids'], list):
            vuln['cve_ids'] = []

        return True

    def send_to_ollama(self, raw_data, filename):
        """
        Envoie les données brutes à Ollama pour analyse intelligente.
        L'IA doit :
        1. Identifier si c'est une vulnérabilité
        2. Extraire les infos clés
        3. Générer description + remédiation + impact + assets + evidence
        """

        prompt = f"""Tu es un expert en cybersécurité et pentesting. Ton rôle est d'analyser TOUT TYPE de données de sécurité et d'identifier les VRAIES vulnérabilités exploitables.

CONTEXTE IMPORTANT:
Tu vas recevoir N'IMPORTE QUEL type de données : résultats de scans automatiques (nmap, nuclei, etc.), output de commandes manuelles, notes écrites par un pentester, ou même de simples messages texte. Ton travail est de COMPRENDRE le contenu, d'IDENTIFIER les risques de sécurité réels, et de les DOCUMENTER professionnellement.

DONNÉES À ANALYSER (fichier: {filename}):
{raw_data}

INSTRUCTIONS CRITIQUES:
1. Tu dois UNIQUEMENT retourner du JSON valide, sans aucun texte avant ou après
2. Les newlines dans les strings doivent être échappés: utiliser \\n au lieu de vraies newlines
3. Analyse ATTENTIVEMENT les données pour identifier les vulnérabilités RÉELLES
4. ADAPTE-TOI au type de contenu que tu reçois:
   - Si c'est un résultat de scan automatique: extrais les vraies vulnérabilités
   - Si c'est l'output d'une commande: analyse ce que cela révèle sur la sécurité
   - Si c'est une note textuelle: comprends l'intention et identifie le risque
   - Si c'est un message simple: interprète-le dans un contexte de sécurité

5. NE PAS considérer comme vulnérabilité:
   - Les ports ouverts standards sans faille connue
   - Les services normaux sans version vulnérable
   - Les informations techniques sans risque réel
   - Les simples énumérations sans exploitation possible

6. CONSIDÉRER comme vulnérabilité:
   - Credentials valides découverts (passwords faibles, comptes compromis)
   - Services avec CVE connus et exploitables
   - Configurations dangereuses (SMB signing disabled, LDAP anonymous bind, etc.)
   - Failles d'authentification ou d'autorisation
   - Exposition de données sensibles
   - Possibilité d'élévation de privilèges
   - Chemins d'attaque exploitables
   - Toute note/observation du pentester indiquant un risque réel

7. Pour CHAQUE vulnérabilité identifiée, tu DOIS fournir CES 9 CHAMPS:

   CHAMPS OBLIGATOIRES (strictement requis):

   a) title (STRING): Titre clair et précis en français (max 100 caractères)

   b) severity (STRING): UNIQUEMENT "critical", "high", "medium", ou "low"

   c) cvss_score (NUMBER): Score CVSS v3.1 réaliste entre 0.0 et 10.0

   e) finding_type (STRING): Catégorie précise en français
      Exemples: "Credentials Faibles", "Mauvaise Configuration", "Vulnérabilité Connue", "Divulgation d'Information", "Contournement d'Authentification"

   f) description (STRING): Analyse DÉTAILLÉE en français (minimum 100 caractères):
      - Ce qui a été trouvé exactement
      - Pourquoi c'est une vulnérabilité (le risque technique)
      - Comment cela peut être exploité
      - Le contexte technique complet
      - Les versions/services affectés
      Les newlines doivent être échappés: \\n

   g) remediation (STRING): Plan de remédiation DÉTAILLÉ en français (minimum 80 caractères):
      - Actions immédiates à prendre (numérotées)
      - Étapes de correction détaillées
      - Configuration/patch recommandés
      - Meilleures pratiques de sécurité
      Utiliser le format: "1. Action première\\n2. Action deuxième\\n3. ..."
      Les newlines doivent être échappés: \\n

   h) business_impact (STRING): Impact métier CONCRET en français (minimum 50 caractères):
      - Conséquences directes pour l'entreprise
      - Risques financiers/réputationnels
      - Scénarios d'attaque réalistes
      - Impact opérationnel

   CHAMPS OPTIONNELS (peuvent être omis ou vides):

   d) cve_ids (ARRAY): Liste des CVE si applicable, sinon []
      Exemple: ["CVE-2023-1234", "CVE-2023-5678"]

   i) affected_assets (ARRAY): Liste des assets affectés (peut être vide)
      Inclure: IPs, hostnames, usernames découverts, noms de services, domaines
      Exemple: ["192.168.1.10", "dc01.inlanefreight.local", "sgage@inlanefreight.local", "SMB"]

   j) evidence (STRING): Preuve technique extraite des données brutes (peut être vide ou court)
      Citer le texte/ligne exact qui prouve la vulnérabilité
      Exemple: "SMB signing disabled on 192.168.1.10 port 445"

8. ÉVALUATION DE LA CRITICITÉ:
   - critical (9.0-10.0): Exploitation immédiate possible, accès root/admin, RCE, compromission totale
   - high (7.0-8.9): Accès non autorisé, exfiltration de données, mouvement latéral
   - medium (4.0-6.9): Configuration faible, information disclosure, DoS
   - low (0.1-3.9): Informations mineures, hardening recommendations

9. Si AUCUNE vulnérabilité réelle n'est trouvée, retourne: {{"vulnerabilities": []}}

EXEMPLE DE JSON CORRECT À PRODUIRE:
{{
  "vulnerabilities": [
    {{
      "title": "Signature SMB Désactivée",
      "severity": "critical",
      "cvss_score": 9.5,
      "cve_ids": [],
      "finding_type": "Mauvaise Configuration",
      "description": "Le protocole SMB n'est pas signé sur le serveur 192.168.1.10:445, ce qui permet aux attaquants de lancer des attaques de type man-in-the-middle et SMB relay. Cette vulnérabilité peut être exploitée pour accéder à des fichiers sensibles, modifier le contenu et prendre le contrôle du système. Le manque de signature SMB expose le réseau à des risques critiques d'escalade de privilèges et de mouvement latéral.",
      "remediation": "1. Activer le SMB signing sur tous les serveurs Windows\\n2. Configurer la clé de registre: HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Services\\\\LanmanServer\\\\Parameters\\\\RequireSecuritySignature = 1\\n3. Appliquer via GPO: Computer Configuration > Policies > Windows Settings > Security Settings > Local Policies > Security Options > Microsoft network server: Digitally sign communications (always)\\n4. Redémarrer les serveurs concernés\\n5. Vérifier la configuration avec: Get-SmbServerConfiguration | Select-Object RequireSecuritySignature",
      "business_impact": "Cette vulnérabilité permet aux attaquants de compromettre l'intégrité des communications réseau, d'accéder à des données confidentielles, et de prendre le contrôle des systèmes critiques. Les risques incluent l'exposition de données clients, l'arrêt des services, et des pertes financières significatives.",
      "affected_assets": ["192.168.1.10", "dc01.inlanefreight.local", "SMB"],
      "evidence": "SMB signing disabled on port 445, allowing anonymous connections and unsigned protocol exchanges"
    }}
  ]
}}

RÉPONDS MAINTENANT AVEC LE JSON COMPLET ET VALIDE (UNIQUEMENT LE JSON, PAS DE TEXTE AVANT OU APRÈS):"""

        try:
            self.log(f"Envoi à Ollama (modèle: {self.model})...", "DEBUG")
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": 0.3,  # Légèrement créatif mais cohérent
                    "num_predict": 3000,  # Augmenté pour des réponses plus complètes
                    "top_p": 0.9,
                    "top_k": 40
                }
            )

            response_text = response['response'].strip()

            # Nettoyer la réponse
            cleaned_response = self.clean_json_response(response_text)

            # Si la réponse ne commence pas par {, c'est probablement du texte
            if not cleaned_response.startswith('{'):
                self.log(f"L'IA a répondu en texte au lieu de JSON pour {filename}", "WARNING")
                self.log("Essai de récupération...", "DEBUG")
                # Chercher le JSON dans la réponse
                start = cleaned_response.find('{')
                end = cleaned_response.rfind('}') + 1
                if start != -1 and end > start:
                    cleaned_response = cleaned_response[start:end]
                else:
                    return []

            # Parse la réponse JSON
            try:
                result = json.loads(cleaned_response)
            except json.JSONDecodeError as je:
                self.log(f"Erreur parsing JSON pour {filename}: {je}", "WARNING")
                self.log("Tentative de correction...", "DEBUG")
                # Essayer de corriger les newlines mal échappées
                cleaned_response = cleaned_response.replace('\n', '\\n')
                try:
                    result = json.loads(cleaned_response)
                except:
                    self.log("Impossible de parser le JSON", "ERROR")
                    self.errors.append({"file": filename, "error": "JSON parsing failed"})
                    return []

            vulnerabilities = result.get('vulnerabilities', [])

            # Valider chaque vulnérabilité
            validated_vulns = []
            for vuln in vulnerabilities:
                if self.validate_vulnerability(vuln, filename):
                    validated_vulns.append(vuln)
                else:
                    self.log(f"Vulnérabilité rejetée pour {filename} (critères de qualité non respectés)", "WARNING")

            return validated_vulns

        except Exception as e:
            self.log(f"Erreur Ollama pour {filename}: {e}", "ERROR")
            self.errors.append({"file": filename, "error": str(e)})
            return []

    def process_all_files(self):
        """Traite tous les fichiers du dossier"""
        files = self.scan_directory()
        self.log(f"Trouvé {len(files)} fichier(s) à analyser", "INFO")
        print()

        for filepath in files:
            filename = os.path.basename(filepath)
            self.log(f"Traitement: {filename}", "INFO")

            try:
                parsed = self.parse_file(filepath)

                # Convertir en texte pour Ollama avec plus de contexte
                if parsed['type'] in ['json', 'yaml']:
                    raw_text = json.dumps(parsed['content'], indent=2)[:8000]
                else:
                    raw_text = str(parsed['content'])[:8000]

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
                            "raw_output": raw_text[:500]
                        },
                        "affected_assets": vuln.get('affected_assets', []),
                        "evidence": vuln.get('evidence'),
                        "status": "open"
                    }
                    self.findings.append(finding)
                    severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(vuln.get('severity'), "⚪")
                    self.log(f"{severity_emoji} {vuln.get('severity').upper()}: {vuln.get('title')}", "SUCCESS")
                    self.findings_counter += 1

                if not vulnerabilities:
                    self.log("Aucune vulnérabilité détectée", "INFO")
                
                self.processed_files.append(filename)

            except Exception as e:
                self.log(f"Erreur lors du traitement de {filename}: {e}", "ERROR")
                self.errors.append({"file": filename, "error": str(e)})

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
            },
            "processing_info": {
                "processed_files": self.processed_files,
                "errors": self.errors,
                "timestamp": datetime.now().isoformat()
            }
        }

        # Créer le dossier si nécessaire
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print("\n" + "="*60)
        self.log(f"Findings sauvegardés: {output_file}", "SUCCESS")
        print("="*60)
        print(f"📊 Total: {summary['total_findings']} findings")
        print(f"   🔴 Critical: {summary['critical']}")
        print(f"   🟠 High: {summary['high']}")
        print(f"   🟡 Medium: {summary['medium']}")
        print(f"   🔵 Low: {summary['low']}")
        print("="*60)
        print(f"📁 Fichiers traités: {len(self.processed_files)}")
        if self.errors:
            print(f"⚠️  Erreurs rencontrées: {len(self.errors)}")
            for error in self.errors:
                print(f"   - {error['file']}: {error['error']}")
        print("="*60)


# Utilisation
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyse intelligente de résultats de scans de sécurité avec IA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python parse_and_enrich.py
  python parse_and_enrich.py --model llama3.2
  python parse_and_enrich.py --scans-dir /path/to/scans --model qwen2.5:14b
  python parse_and_enrich.py --output custom_findings.json --quiet

Modèles IA recommandés (par ordre de qualité):
  1. qwen2.5:14b ou qwen2.5:32b - EXCELLENT pour l'analyse de sécurité (recommandé)
  2. llama3.2:latest ou llama3.1:8b - Très bon, polyvalent
  3. mistral:7b - Bon, rapide
  4. codellama:13b - Bon pour l'analyse technique
  
Pour installer un modèle: ollama pull <model-name>
        """
    )
    parser.add_argument(
        '--scans-dir',
        default='results/scans',
        help='Dossier contenant les fichiers à analyser (défaut: results/scans)'
    )
    parser.add_argument(
        '--model',
        default='llama3.2',
        help='Modèle Ollama à utiliser (défaut: llama3.2)'
    )
    parser.add_argument(
        '--output',
        default='results/findings_enrichis.json',
        help='Fichier de sortie JSON (défaut: results/findings_enrichis.json)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Mode silencieux (moins de verbosité)'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("🍔 FRICADELLE - Analyseur de Vulnérabilités avec IA")
    print("="*60)
    print(f"Modèle IA: {args.model}")
    print(f"Dossier de scans: {args.scans_dir}")
    print(f"Fichier de sortie: {args.output}")
    print("="*60)
    print()
    
    analyzer = VulnerabilityAnalyzer(
        scans_dir=args.scans_dir,
        ollama_model=args.model,
        verbose=not args.quiet
    )
    analyzer.process_all_files()
    analyzer.save_findings(args.output)
