# Fricadelle - Générateur de Rapports de Pentest Professionnel

🛡️ **Système automatisé de génération de rapports d'audit de sécurité** avec analyse IA des résultats de scans et génération de rapports PDF/HTML professionnels en français.

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Configuration](#configuration)
- [Structure du Projet](#structure-du-projet)
- [Exemples](#exemples)

## 🎯 Vue d'ensemble

Fricadelle transforme automatiquement vos résultats de scans de sécurité (Nmap, Kerbrute, CrackMapExec, Nuclei, etc.) en rapports d'audit professionnels avec :

- ✅ **Analyse IA intelligente** via Ollama pour identifier les vraies vulnérabilités
- ✅ **Rapports PDF/HTML professionnels** avec design moderne
- ✅ **Structure flexible** pour tout type de scan de sécurité
- ✅ **100% en français** pour vos clients francophones

## 🏗️ Architecture

```
/results/scans/  (fichiers bruts: kerbrute, crackmapexec, nmap JSON, etc.)
      ↓
[Étape 1] parse_and_enrich.py
          - IA (Ollama) analyse VRAIMENT les résultats
          - Détecte si c'est UNE VULNÉRABILITÉ ou juste une info
          - Extrait les données importantes
          - Génère description + remédiation complète
      ↓
findings_enrichis.json (structure flexible)
      ↓
[Étape 2] generate_report.py
          - Template Jinja2 professionnel français complet
          - Rapport PDF beau + HTML interactif
          - Toutes les sections (Executive, Findings, Roadmap, etc.)
      ↓
/output/rapport.pdf + rapport.html
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

# 4. Récupérer vos rapports
# → output/rapport.pdf
# → output/rapport.html
```

### Options Avancées

```bash
# Générer seulement le PDF
python generate_report.py --format pdf

# Générer seulement le HTML
python generate_report.py --format html

# Utiliser un fichier de findings personnalisé
python generate_report.py --findings mon_fichier.json

# Spécifier un répertoire de sortie différent
python generate_report.py --output /tmp/rapports
```

## ⚙️ Configuration

### config.yaml

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
  format: "both"  # pdf, html, ou both
  include_appendix: true
  include_roadmap: true
  logo_path: "assets/logo.png"
  output_dir: "output"
```

### Personnalisation du Modèle IA

Dans `parse_and_enrich.py`, vous pouvez changer le modèle Ollama :

```python
analyzer = VulnerabilityAnalyzer(
    scans_dir="results/scans",
    ollama_model="llama3.2"  # Changez ici
)
```

## 📁 Structure du Projet

```
pentest-report-generator/
├── config.yaml                     # Configuration de l'audit
├── parse_and_enrich.py            # Script d'analyse IA
├── generate_report.py             # Script de génération de rapport
├── requirements.txt               # Dépendances Python
├── README.md                      # Documentation
├── templates/
│   └── rapport.html.j2           # Template Jinja2 du rapport
├── assets/
│   ├── style.css                 # Styles CSS professionnels
│   └── logo.png                  # Logo (placeholder)
├── results/
│   ├── scans/                    # ← Vos fichiers bruts
│   └── findings_enrichis.json    # Output de parse_and_enrich.py
└── output/
    ├── rapport.pdf               # Rapport final PDF
    └── rapport.html              # Rapport final HTML
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

### Design

- 🎨 **Couleurs** : Cartes colorées par sévérité (rouge/orange/jaune/bleu)
- 📄 **Pagination** : Numéros de page automatiques
- 🔒 **Confidentialité** : En-têtes/pieds de page professionnels
- 📱 **Responsive** : Adapté à l'impression et la lecture écran

## 💡 Exemples d'Utilisation

### Exemple 1 : Scan Nmap

```bash
# Scanner le réseau
nmap -sV -sC -oJ results/scans/nmap_scan.json 192.168.1.0/24

# Analyser et générer le rapport
python parse_and_enrich.py
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

### Exemple 3 : Multiple Tools

```bash
# Copier tous vos résultats
cp nmap.json results/scans/
cp kerbrute.txt results/scans/
cp crackmapexec.txt results/scans/
cp nuclei.json results/scans/

# L'IA analysera tous les fichiers
python parse_and_enrich.py

# Générer le rapport complet
python generate_report.py
```

## 🔧 Personnalisation

### Modifier le Template

Le template `templates/rapport.html.j2` utilise Jinja2. Vous pouvez :

- Ajouter/supprimer des sections
- Modifier le design
- Ajouter votre logo
- Personnaliser les couleurs dans `assets/style.css`

### Modifier l'Analyse IA

Dans `parse_and_enrich.py`, vous pouvez :

- Ajuster le prompt pour l'IA
- Modifier la taille du contexte (actuellement 2000 caractères)
- Ajouter des règles de parsing spécifiques
- Personnaliser la structure des findings

## 📝 License

Ce projet est fourni tel quel pour usage professionnel dans le cadre d'audits de sécurité.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir des issues ou des pull requests.

## ⚠️ Avertissement

Ce système est conçu pour être utilisé dans le cadre légal d'audits de sécurité autorisés. L'utilisateur est responsable de l'utilisation éthique et légale de cet outil.
