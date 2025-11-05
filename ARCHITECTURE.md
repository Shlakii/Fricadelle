# Architecture et Fonctionnement de Fricadelle

## 🏗️ Vue d'Ensemble de l'Architecture

Fricadelle est un système en deux étapes qui transforme automatiquement les résultats bruts de scans de sécurité en rapports d'audit professionnels.

```
┌─────────────────────────────────────────────────────────────┐
│                    ÉTAPE 1: ENRICHISSEMENT                   │
│                   (parse_and_enrich.py)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Fichiers bruts de scan                                      │
│  - nmap JSON                                                 │
│  - kerbrute TXT                                              │
│  - crackmapexec TXT                                          │
│  - nuclei JSON                                               │
│  - etc.                                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Analyse IA (Ollama)                                         │
│  - Identifie les vraies vulnérabilités                       │
│  - Extrait les données clés                                  │
│  - Génère descriptions détaillées                            │
│  - Propose des remédiations                                  │
│  - Évalue l'impact métier                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  findings_enrichis.json                                      │
│  Structure JSON flexible avec toutes les métadonnées         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ÉTAPE 2: GÉNÉRATION                       │
│                   (generate_report.py)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Template Jinja2 + CSS                                       │
│  - Mise en forme professionnelle                             │
│  - Sections structurées                                      │
│  - Design moderne et coloré                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Rapports Finaux                                             │
│  - rapport.html (interactif)                                 │
│  - rapport.pdf (professionnel)                               │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Structure des Fichiers

### Scripts Principaux

#### parse_and_enrich.py
- **Rôle**: Analyser les scans et extraire les vulnérabilités via IA
- **Entrée**: Fichiers dans `results/scans/`
- **Sortie**: `results/findings_enrichis.json`
- **Dépendances**: Ollama (serveur IA local)

**Fonctionnalités clés**:
```python
class VulnerabilityAnalyzer:
    - scan_directory()      # Trouve tous les fichiers
    - parse_file()          # Parse JSON/CSV/TXT
    - send_to_ollama()      # Analyse IA intelligente
    - process_all_files()   # Pipeline complet
    - save_findings()       # Sauvegarde JSON
```

#### generate_report.py
- **Rôle**: Générer les rapports PDF/HTML à partir du JSON
- **Entrée**: `results/findings_enrichis.json` + `config.yaml`
- **Sortie**: `output/rapport.pdf` et/ou `output/rapport.html`
- **Dépendances**: Jinja2, WeasyPrint

**Fonctionnalités clés**:
```python
class ReportGenerator:
    - load_config()         # Charge config.yaml
    - load_findings()       # Charge findings JSON
    - generate_html()       # Génère HTML via Jinja2
    - generate_pdf()        # Convertit HTML en PDF
    - generate_reports()    # Pipeline complet
```

### Fichiers de Configuration

#### config.yaml
Configuration complète de l'audit:
- **audit**: Métadonnées client (nom, dates, périmètre, testeurs)
- **report**: Options de génération (format, sections, logo)

#### requirements.txt
Dépendances Python:
- `ollama`: Interface avec le modèle IA
- `jinja2`: Moteur de templates
- `weasyprint`: Génération PDF
- `pyyaml`: Parsing YAML
- `pillow`, `lxml`: Support images et parsing

### Ressources

#### templates/rapport.html.j2
Template Jinja2 complet avec:
- Couverture professionnelle
- Table des matières
- Résumé exécutif
- Dashboard statistique
- Détails des vulnérabilités (par sévérité)
- Plan de remédiation (roadmap)
- Annexes techniques
- Disclaimer légal

#### assets/style.css
Feuille de style CSS professionnelle:
- Design moderne et épuré
- Couleurs par sévérité (rouge=critical, orange=high, etc.)
- Cartes pour chaque finding
- Responsive et print-friendly
- Headers/footers automatiques

## 🔄 Workflow Complet

### 1. Préparation
```bash
# Structure des dossiers créée automatiquement
mkdir -p results/scans output

# Lancer Ollama
ollama serve

# Télécharger un modèle si nécessaire
ollama pull llama3.2
```

### 2. Collecte des Scans
```bash
# Copier vos fichiers de scan
cp /path/to/nmap.json results/scans/
cp /path/to/kerbrute.txt results/scans/
# etc.
```

### 3. Configuration
```yaml
# Éditer config.yaml
audit:
  client_name: "Mon Client"
  audit_date: "2025-11-05"
  # ...
```

### 4. Enrichissement IA
```bash
# L'IA analyse chaque fichier
python parse_and_enrich.py

# Résultat: results/findings_enrichis.json
```

### 5. Génération du Rapport
```bash
# Générer PDF + HTML
python generate_report.py

# OU seulement HTML
python generate_report.py --format html

# OU seulement PDF
python generate_report.py --format pdf
```

### 6. Livraison
```bash
# Rapports disponibles dans output/
ls output/
# > rapport.html
# > rapport.pdf
```

## 🤖 Analyse IA avec Ollama

### Prompt Structure

Le système envoie à Ollama un prompt structuré qui:
1. **Identifie** si le contenu contient une vulnérabilité
2. **Extrait** les informations techniques
3. **Génère** une description en français
4. **Propose** une remédiation détaillée
5. **Évalue** l'impact métier

### Réponse JSON Attendue

```json
{
  "vulnerabilities": [
    {
      "title": "Titre clair",
      "severity": "critical|high|medium|low",
      "cvss_score": 7.5,
      "finding_type": "Type de vulnérabilité",
      "description": "Description détaillée...",
      "remediation": "Étapes de correction...",
      "business_impact": "Impact pour l'entreprise...",
      "affected_assets": ["asset1", "asset2"],
      "evidence": "Preuve technique"
    }
  ]
}
```

### Filtrage Intelligent

L'IA **ne remonte PAS**:
- Les ports ouverts sans vulnérabilité
- Les informations techniques banales
- Les services standards sans risque

L'IA **remonte**:
- Credentials valides
- Mots de passe faibles
- Services vulnérables (CVE)
- Configurations dangereuses
- Expositions non autorisées

## 📊 Structure JSON des Findings

### Format Complet

```json
{
  "audit_metadata": {
    "client_name": "string",
    "audit_date": "YYYY-MM-DD",
    "audit_end_date": "YYYY-MM-DD",
    "audit_type": "string",
    "scope": ["array"],
    "testeurs": ["array"],
    "contact_client": "email"
  },
  "findings": [
    {
      "id": "VULN-XXX",
      "title": "string",
      "severity": "critical|high|medium|low",
      "cvss_score": float,
      "cve_ids": ["array"],
      "finding_type": "string",
      "description": "string (long)",
      "remediation": "string (long)",
      "business_impact": "string",
      "source_data": {
        "tool": "string",
        "command": "string (optional)",
        "raw_output": "string"
      },
      "affected_assets": ["array"],
      "evidence": "string",
      "status": "open|closed"
    }
  ],
  "summary": {
    "total_findings": int,
    "critical": int,
    "high": int,
    "medium": int,
    "low": int
  },
  "statistics": {
    "findings_by_tool": {"tool": count},
    "findings_by_type": {"type": count}
  }
}
```

## 🎨 Personnalisation

### Modifier le Design

**Couleurs** (dans `assets/style.css`):
```css
.severity-badge.critical {
    background: #dc3545;  /* Rouge */
}
.severity-badge.high {
    background: #fd7e14;  /* Orange */
}
/* etc. */
```

**Logo** (dans `config.yaml`):
```yaml
report:
  logo_path: "assets/mon_logo.png"
```

### Ajouter des Sections au Template

Éditer `templates/rapport.html.j2`:
```html
<!-- Nouvelle section -->
<div id="ma-section" class="section page-break">
    <h1>Ma Nouvelle Section</h1>
    <p>{{ ma_variable }}</p>
</div>
```

### Modifier l'Analyse IA

Éditer le prompt dans `parse_and_enrich.py`:
```python
prompt = f"""Tu es un expert...
[Ajoutez vos instructions spécifiques]
"""
```

## 🔧 Dépannage

### Ollama ne répond pas
```bash
# Vérifier qu'Ollama tourne
ollama list

# Relancer Ollama
ollama serve
```

### PDF ne se génère pas
```bash
# Installer les dépendances système pour WeasyPrint
# Ubuntu/Debian:
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0

# macOS:
brew install pango
```

### Template errors
```bash
# Tester le template
python -c "from jinja2 import Environment, FileSystemLoader; \
env = Environment(loader=FileSystemLoader('templates')); \
env.get_template('rapport.html.j2')"
```

## 📈 Évolutions Futures

- [ ] Support de graphiques (charts.js) dans le dashboard
- [ ] Export Excel des findings
- [ ] API REST pour génération automatique
- [ ] Interface web pour configuration
- [ ] Multi-langues (EN, ES, etc.)
- [ ] Intégration CI/CD
- [ ] Génération de métriques KPI

## 🤝 Contribution

Pour contribuer:
1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push et créer une Pull Request

## 📝 License

Projet professionnel pour audits de sécurité autorisés.
