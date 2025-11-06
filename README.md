# Fricadelle - Générateur de Rapports de Pentest Professionnel

🛡️ **Système automatisé de génération de rapports d'audit de sécurité** avec analyse IA avancée des résultats de scans et génération de rapports PDF professionnels en français.

## ✨ Nouveautés et Améliorations

- ✅ **Analyse universelle**: Accepte N'IMPORTE quel type de fichier (JSON, XML, CSV, YAML, TXT, etc.)
- ✅ **Intelligence contextuelle**: L'IA comprend les notes manuelles, commandes, et messages simples
- ✅ **Détection automatique d'encodage**: Support de tous les encodages de fichiers
- ✅ **Configuration flexible**: Fichier de configuration pour personnaliser l'IA et les paramètres
- ✅ **Modèles IA recommandés**: Guide complet des meilleurs modèles (Qwen2.5, Llama3, Mistral)
- ✅ **Gestion d'erreurs robuste**: Traitement résilient avec logs détaillés
- ✅ **Mode verbeux**: Suivi en temps réel du traitement avec emojis
- ✅ **Arguments en ligne de commande**: Configuration facile via CLI

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Configuration](#configuration)
- [Structure du Projet](#structure-du-projet)
- [Exemples](#exemples)

## 🎯 Vue d'ensemble

Fricadelle transforme **N'IMPORTE QUEL type de données de sécurité** en rapports d'audit professionnels avec :

- ✅ **Analyse IA universelle** - Accepte tout type de fichier: scans automatiques, commandes manuelles, notes textuelles, ou même de simples messages
- ✅ **Intelligence contextuelle avancée** via Ollama pour comprendre et analyser n'importe quel format
- ✅ **Détection automatique d'encodage** pour supporter tous les fichiers (UTF-8, Latin-1, etc.)
- ✅ **Validation automatique de qualité** pour garantir des descriptions détaillées et pertinentes
- ✅ **Modèles IA optimisés** - Guide complet pour choisir le meilleur modèle (Qwen2.5, Llama3, Mistral)
- ✅ **Rapport PDF professionnel** avec design moderne et épuré
- ✅ **Catégorisation intelligente** des vulnérabilités avec évaluation CVSS précise
- ✅ **Structure flexible** pour tout type de scan de sécurité ou observation manuelle
- ✅ **100% en français** pour vos clients francophones
- ✅ **Configuration YAML** pour personnaliser tous les aspects de l'analyse

## 🏗️ Architecture

```
/results/scans/  (N'IMPORTE QUEL fichier: scans, commandes, notes, messages, etc.)
      ↓
[Étape 1] parse_and_enrich.py
          - Détection automatique d'encodage (UTF-8, Latin-1, etc.)
          - Support universel: JSON, XML, CSV, YAML, TXT, et plus
          - IA (Ollama) analyse INTELLIGEMMENT tout type de contenu
          - Détecte si c'est UNE VULNÉRABILITÉ ou juste une info
          - Comprend les notes manuelles et observations du pentester
          - Valide la qualité des descriptions (minimum 100 caractères)
          - Extrait les données importantes avec contexte complet
          - Génère description + remédiation + impact métier détaillés
          - Catégorisation intelligente et score CVSS précis
          - Gestion d'erreurs robuste avec logs détaillés
      ↓
findings_enrichis.json (structure flexible validée)
      ↓
[Étape 2] generate_report.py
          - Template Jinja2 professionnel français complet
          - Rapport PDF avec design moderne et épuré
          - Toutes les sections (Executive, Findings, Roadmap, etc.)
      ↓
/output/rapport.pdf
```

## 📦 Installation

### Prérequis

- Python 3.8+
- Ollama installé et en cours d'exécution
- Un modèle Ollama français (ex: llama3.2)

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Configuration d'Ollama

```bash
# Installer Ollama si nécessaire
curl -fsSL https://ollama.ai/install.sh | sh

# Télécharger un modèle (exemple: llama3.2)
ollama pull llama3.2

# Vérifier qu'Ollama fonctionne
ollama list
```

## 🚀 Utilisation

### Pipeline Complet

```bash
# 1. Placer vos fichiers de scan dans results/scans/
cp mon_scan_nmap.json results/scans/
cp kerbrute_results.txt results/scans/
cp crackmapexec_output.txt results/scans/

# 2. Enrichir les résultats via IA
python parse_and_enrich.py

# 3. Générer le rapport
python generate_report.py --config config.yaml

# 4. Récupérer votre rapport
# → output/rapport.pdf
```

### Options Avancées

```bash
# Utiliser un modèle IA spécifique (RECOMMANDÉ: qwen2.5:14b)
python parse_and_enrich.py --model qwen2.5:14b

# Mode silencieux
python parse_and_enrich.py --quiet

# Dossier de scans personnalisé
python parse_and_enrich.py --scans-dir /path/to/scans

# Fichier de sortie personnalisé
python parse_and_enrich.py --output custom_findings.json

# Générer le rapport avec un fichier de findings personnalisé
python generate_report.py --findings mon_fichier.json

# Spécifier un répertoire de sortie différent
python generate_report.py --output /tmp/rapports

# Afficher l'aide et voir tous les modèles recommandés
python parse_and_enrich.py --help
```

## ⚙️ Configuration

### config.yaml (Configuration du Rapport)

```yaml
audit:
  client_name: "ACME Corp"
  audit_date: "2025-11-05"
  audit_end_date: "2025-11-06"
  audit_type: "Pentest Externe + Interne"
  scope:
    - "192.168.1.0/24"
    - "172.16.5.0/24"
    - "example.com"
  testeurs:
    - "Alice Dupont"
    - "Bob Martin"
  contact_client: "ciso@acme.com"

report:
  language: "fr"
  include_appendix: true
  include_roadmap: true
  logo_path: "assets/logo.png"
  output_dir: "output"
```

### fricadelle_config.yaml (Configuration de l'Analyse IA)

```yaml
# Configuration de l'IA
ai:
  model: "qwen2.5:14b"  # Modèle recommandé (voir AI_MODELS_GUIDE.md)
  temperature: 0.3
  max_tokens: 3000

# Configuration des chemins
paths:
  scans_directory: "results/scans"
  output_file: "results/findings_enrichis.json"

# Configuration de l'analyse
analysis:
  max_context_size: 8000
  validation:
    min_description_length: 100
    min_remediation_length: 80
    min_business_impact_length: 50
```

### Personnalisation du Modèle IA

Fricadelle supporte maintenant de **nombreux modèles IA** via Ollama. Consultez le [Guide des Modèles IA](AI_MODELS_GUIDE.md) pour choisir le meilleur modèle selon vos besoins.

**Modèles recommandés** (par ordre de qualité):
1. **qwen2.5:14b** - EXCELLENT pour l'analyse de sécurité ⭐⭐⭐⭐⭐
2. **llama3.2** - Très bon, équilibré (défaut) ⭐⭐⭐⭐
3. **mistral:7b** - Bon, rapide, excellent en français ⭐⭐⭐⭐
4. **codellama:13b** - Spécialisé analyse technique ⭐⭐⭐⭐

```bash
# Installer un modèle recommandé
ollama pull qwen2.5:14b

# Utiliser avec Fricadelle
python parse_and_enrich.py --model qwen2.5:14b
```

Voir [AI_MODELS_GUIDE.md](AI_MODELS_GUIDE.md) pour le guide complet.

## 📁 Structure du Projet

```
fricadelle/
├── config.yaml                     # Configuration de l'audit et du rapport
├── fricadelle_config.yaml          # Configuration de l'analyse IA (NOUVEAU)
├── parse_and_enrich.py             # Script d'analyse IA avancée et flexible
├── generate_report.py              # Script de génération de rapport PDF
├── requirements.txt                # Dépendances Python
├── README.md                       # Documentation principale
├── AI_MODELS_GUIDE.md              # Guide des modèles IA (NOUVEAU)
├── QUICKSTART.md                   # Guide de démarrage rapide
├── ARCHITECTURE.md                 # Documentation architecture
├── templates/
│   └── rapport.html.j2            # Template Jinja2 du rapport
├── assets/
│   ├── style.css                  # Styles CSS modernes
│   └── logo.png                   # Logo (placeholder)
├── results/
│   ├── scans/                     # ← TOUT TYPE DE FICHIER accepté
│   │   ├── nmap.json              # Scans automatiques
│   │   ├── kerbrute.txt           # Outputs de commandes
│   │   ├── notes.txt              # Notes manuelles
│   │   └── message.txt            # Messages simples
│   └── findings_enrichis.json     # Output de parse_and_enrich.py
└── output/
    └── rapport.pdf                # Rapport final PDF professionnel
```

## 📊 Structure JSON des Findings

```json
{
  "audit_metadata": {
    "client_name": "ACME Corp",
    "audit_date": "2025-11-05",
    "audit_end_date": "2025-11-06",
    "audit_type": "Pentest Externe + Interne",
    "scope": ["192.168.1.0/24", "example.com"],
    "testeurs": ["Alice", "Bob"],
    "contact_client": "ciso@acme.com"
  },
  "findings": [
    {
      "id": "VULN-001",
      "title": "Identification de Credentials Valides via Kerbrute",
      "severity": "critical",
      "cvss_score": 9.1,
      "cve_ids": [],
      "finding_type": "Configuration Error - Weak Password",
      "description": "Description détaillée générée par l'IA...",
      "remediation": "Étapes de remédiation générées par l'IA...",
      "business_impact": "Impact métier analysé par l'IA...",
      "source_data": {
        "tool": "kerbrute",
        "raw_output": "..."
      },
      "affected_assets": ["sgage@inlanefreight.local"],
      "evidence": "Preuve technique extraite",
      "status": "open"
    }
  ],
  "summary": {
    "total_findings": 45,
    "critical": 5,
    "high": 12,
    "medium": 18,
    "low": 10
  },
  "statistics": {
    "findings_by_tool": {
      "kerbrute": 3,
      "crackmapexec": 7,
      "nmap": 18
    },
    "findings_by_type": {
      "Weak Credentials": 5,
      "Configuration Error": 12
    }
  }
}
```

## 🎨 Fonctionnalités du Rapport

### Sections Incluses

1. **Couverture** - Design professionnel avec métadonnées
2. **Table des matières** - Navigation facilitée
3. **Résumé Exécutif** - Pour les décideurs (1-2 pages)
4. **Tableau de Bord** - Statistiques visuelles
   - Répartition par sévérité (Critical/High/Medium/Low)
   - Répartition par outil
   - Répartition par type de vulnérabilité
5. **Détails des Vulnérabilités** - Organisés par sévérité
   - Description complète
   - Impact métier
   - Actifs affectés
   - Remédiation détaillée
   - Preuves techniques
6. **Plan de Remédiation** - Timeline et priorités
7. **Annexes Techniques** - Glossaire, échelle CVSS, outils utilisés
8. **Disclaimer Légal** - Mentions de confidentialité

### Design Moderne

- 🎨 **Couleurs** : Dégradés modernes et cartes colorées par sévérité (gradients rouge/orange/jaune/bleu)
- 📄 **Pagination** : Numéros de page automatiques et professionnels
- 🔒 **Confidentialité** : En-têtes/pieds de page professionnels
- 💎 **Visuel** : Ombres portées, bordures arrondies, design épuré
- 📊 **Lisibilité** : Typographie optimisée et hiérarchie visuelle claire

## 💡 Exemples d'Utilisation

### Exemple 1 : Scan Nmap
```bash
# Scanner le réseau
nmap -sV -sC -oJ results/scans/nmap_scan.json 192.168.1.0/24

# Analyser et générer le rapport
python parse_and_enrich.py --model qwen2.5:14b
python generate_report.py
```

### Exemple 2 : Kerbrute Password Spray
```bash
# Utiliser Kerbrute
kerbrute passwordspray -d domain.local users.txt Password123 > results/scans/kerbrute.txt

# Analyser et générer le rapport
python parse_and_enrich.py
python generate_report.py
```

### Exemple 3 : Notes Manuelles (NOUVEAU!)
```bash
# Créer une note manuelle
echo "Le serveur 192.168.1.50 a RDP ouvert sur Internet sans restriction. 
Admin/admin fonctionne sur le FTP.
SMB signing désactivé sur le DC." > results/scans/observations.txt

# L'IA comprendra et analysera ces observations!
python parse_and_enrich.py --model qwen2.5:14b
python generate_report.py
```

### Exemple 4 : Multiple Tools et Formats
```bash
# Copier tous vos résultats (TOUS FORMATS supportés)
cp nmap.json results/scans/
cp kerbrute.txt results/scans/
cp crackmapexec.txt results/scans/
cp nuclei.json results/scans/
cp mes_notes.txt results/scans/
cp scan_custom.xml results/scans/

# L'IA analysera TOUS les fichiers intelligemment
python parse_and_enrich.py --model qwen2.5:14b

# Générer le rapport complet
python generate_report.py
```

### Exemple 5 : Configuration Avancée
```bash
# Éditer la configuration
nano fricadelle_config.yaml

# Lancer avec paramètres personnalisés
python parse_and_enrich.py \
  --scans-dir /path/to/scans \
  --model qwen2.5:14b \
  --output custom_findings.json

# Générer le rapport
python generate_report.py --findings custom_findings.json
```

## 🔧 Personnalisation

### Modifier le Template

Le template `templates/rapport.html.j2` utilise Jinja2. Vous pouvez :

- Ajouter/supprimer des sections
- Modifier le design
- Ajouter votre logo
- Personnaliser les couleurs dans `assets/style.css`

### Modifier l'Analyse IA

**Fricadelle supporte maintenant une configuration complète via `fricadelle_config.yaml`** :

```yaml
ai:
  model: "qwen2.5:14b"     # Changer le modèle IA
  temperature: 0.2         # Plus bas = plus cohérent
  max_tokens: 4000         # Plus haut = plus détaillé

analysis:
  max_context_size: 10000  # Plus de contexte pour l'IA
  validation:
    min_description_length: 150  # Descriptions plus longues
```

**Arguments en ligne de commande** (overrides la config):
```bash
python parse_and_enrich.py --model qwen2.5:14b --quiet
```

**Personnaliser les critères de validation** :
- Description minimum 100 caractères (configurable)
- Remédiation minimum 80 caractères (configurable)
- Impact métier minimum 50 caractères (configurable)
- Sévérité valide (critical, high, medium, low)
- Score CVSS entre 0.0 et 10.0
- Au moins un actif affecté (flexible)

**Voir aussi**: [AI_MODELS_GUIDE.md](AI_MODELS_GUIDE.md) pour choisir le meilleur modèle

## 📝 License

Ce projet est fourni tel quel pour usage professionnel dans le cadre d'audits de sécurité.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir des issues ou des pull requests.

## ⚠️ Avertissement

Ce système est conçu pour être utilisé dans le cadre légal d'audits de sécurité autorisés. L'utilisateur est responsable de l'utilisation éthique et légale de cet outil.
