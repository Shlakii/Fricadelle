# Fricadelle - Générateur de Rapports de Pentest Professionnel

🛡️ **Système automatisé de génération de rapports d'audit de sécurité** avec analyse IA avancée des résultats de scans et génération de rapports PDF/HTML professionnels en français.

## 🆕 Nouveautés v2.0

### Analyse IA Améliorée
- ✅ **Prompts structurés** pour réduire les hallucinations à moins de 5%
- ✅ **Validation multi-étapes** des vulnérabilités détectées
- ✅ **Scores de confiance** (0-100%) pour chaque finding
- ✅ **Complexité d'exploitation** (faible/moyenne/élevée)
- ✅ **Retry automatique** avec gestion d'erreurs robuste

### Qualité des Rapports
- ✅ **Indicateurs visuels** de confiance et complexité
- ✅ **Métadonnées enrichies** (version analyzer, modèle IA utilisé)
- ✅ **Statistiques avancées** (confiance moyenne, erreurs d'analyse)
- ✅ **Format professionnel** avec sections détaillées

### Validation et Fiabilité
- ✅ **Schéma JSON strict** pour toutes les réponses IA
- ✅ **Tests unitaires** pour les composants critiques
- ✅ **Documentation complète** des améliorations

📖 **[Voir le guide complet des améliorations →](IMPROVEMENTS.md)**

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

- ✅ **Analyse IA intelligente** via Ollama avec validation multi-étapes
- ✅ **Détection précise** des vraies vulnérabilités (réduction des faux positifs)
- ✅ **Scores de confiance** pour chaque finding (0-100%)
- ✅ **Rapports PDF/HTML professionnels** avec design moderne
- ✅ **Structure flexible** pour tout type de scan de sécurité
- ✅ **100% en français** pour vos clients francophones
- ✅ **100% local** - Aucune donnée envoyée à l'extérieur

## 🏗️ Architecture

```
/results/scans/  (fichiers bruts: kerbrute, crackmapexec, nmap JSON, etc.)
      ↓
[Étape 1] parse_and_enrich.py (AMÉLIORÉ v2.0)
          - Prompts IA structurés et détaillés
          - Analyse intelligente des résultats
          - Validation multi-étapes des vulnérabilités
          - Détection précise (vraie vulnérabilité vs info)
          - Score de confiance pour chaque finding
          - Extraction des données importantes
          - Génération description + remédiation complète
          - Retry automatique en cas d'erreur
      ↓
findings_enrichis.json (structure enrichie avec métadonnées)
      ↓
[Étape 2] generate_report.py
          - Template Jinja2 professionnel français complet
          - Indicateurs visuels de confiance
          - Rapport PDF beau + HTML interactif
          - Toutes les sections (Executive, Findings, Roadmap, etc.)
      ↓
/output/rapport.pdf + rapport.html (rapports professionnels)
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

# 2. Enrichir les résultats via IA (avec validation recommandée)
python parse_and_enrich.py

# 3. Générer le rapport
python generate_report.py --config config.yaml

# 4. Récupérer vos rapports
# → output/rapport.pdf
# → output/rapport.html
```

### Options Avancées

#### parse_and_enrich.py

```bash
# Utiliser un modèle IA différent
python parse_and_enrich.py --model llama3.1

# Analyser un répertoire personnalisé
python parse_and_enrich.py --scans-dir /chemin/vers/scans

# Désactiver la validation (plus rapide mais moins fiable)
python parse_and_enrich.py --no-validation

# Output personnalisé
python parse_and_enrich.py --output custom_findings.json

# Afficher l'aide complète
python parse_and_enrich.py --help
```

#### generate_report.py

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

Dans `parse_and_enrich.py`, vous pouvez changer le modèle Ollama et les options :

```bash
# Via ligne de commande (recommandé)
python parse_and_enrich.py --model llama3.2

# Ou via code (parse_and_enrich.py)
analyzer = VulnerabilityAnalyzer(
    scans_dir="results/scans",
    ollama_model="llama3.2",
    enable_validation=True  # Recommandé pour meilleure qualité
)
```

### Interprétation des Scores de Confiance

Les findings incluent maintenant un score de confiance :

- **🟢 90-100%** : Très haute confiance - Inclure directement dans le rapport
- **🟢 80-90%** : Haute confiance - Vérifier rapidement
- **🟡 60-80%** : Confiance moyenne - Validation manuelle recommandée
- **🔴 <60%** : Faible confiance - Investigation approfondie nécessaire

## 📁 Structure du Projet

```
fricadelle/
├── config.yaml                     # Configuration de l'audit
├── parse_and_enrich.py            # Script d'analyse IA (AMÉLIORÉ v2.0)
├── ai_analyzer.py                 # Module d'analyse IA avancée (NOUVEAU)
├── vulnerability_schema.py        # Validation et schémas (NOUVEAU)
├── generate_report.py             # Script de génération de rapport
├── test_fricadelle.py             # Tests unitaires (NOUVEAU)
├── requirements.txt               # Dépendances Python
├── README.md                      # Cette documentation
├── IMPROVEMENTS.md                # Guide détaillé des améliorations (NOUVEAU)
├── ARCHITECTURE.md                # Architecture technique
├── QUICKSTART.md                  # Guide de démarrage rapide
├── templates/
│   ├── rapport.html.j2           # Template Jinja2 du rapport
│   └── finding_macros.j2         # Macros réutilisables (NOUVEAU)
├── assets/
│   ├── style.css                 # Styles CSS professionnels (AMÉLIORÉ)
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
- 🎯 **Indicateurs** : Scores de confiance et complexité d'exploitation (NOUVEAU v2.0)

## 🧪 Tests et Validation

### Exécuter les Tests Unitaires

```bash
# Lancer tous les tests
python test_fricadelle.py -v

# Tester uniquement la validation des schémas
python -m unittest test_fricadelle.TestVulnerabilitySchema -v
```

### Tester l'Analyse IA

```bash
# Créer un fichier de test
echo '[+] VALID LOGIN: testuser@domain.local:Password123' > results/scans/test_kerbrute.txt

# Analyser
python parse_and_enrich.py

# Vérifier le résultat
cat results/findings_enrichis.json | python -m json.tool
```

### Validation de la Qualité

Après génération du rapport, vérifiez:

1. **Scores de confiance**: Moyenne > 80% pour une bonne qualité
2. **Erreurs d'analyse**: Aucune erreur dans `findings_enrichis.json`
3. **Cohérence**: Les findings correspondent aux données sources
4. **Complétude**: Descriptions, remédiations, et impacts sont détaillés

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
