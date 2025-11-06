# Fricadelle - Guide de Démarrage Rapide

## ⚡ Installation Rapide

```bash
# 1. Cloner le projet
git clone https://github.com/Shlakii/Fricadelle.git
cd Fricadelle

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Installer et lancer Ollama
# Voir: https://ollama.ai/download
ollama serve

# 4. Télécharger un modèle IA (RECOMMANDÉ: qwen2.5:14b)
ollama pull qwen2.5:14b
# OU le modèle par défaut
ollama pull llama3.2
```

## 🚀 Utilisation en 5 Étapes

### Étape 1: Placer vos fichiers (N'IMPORTE QUOI!)
```bash
# Fricadelle accepte TOUT type de fichier:
# - Scans automatiques (nmap, nuclei, etc.)
# - Outputs de commandes (kerbrute, crackmapexec, etc.)
# - Notes manuelles (observations.txt)
# - Messages simples (findings.txt)
# - Tout format: JSON, XML, CSV, YAML, TXT, etc.

cp vos_scans/* results/scans/
# OU créer une note manuelle:
echo "RDP ouvert sur 192.168.1.50 sans restriction IP" > results/scans/note.txt
```

### Étape 2: Configurer le client
```bash
# Éditer config.yaml
nano config.yaml
# Modifier: client_name, audit_date, scope, testeurs
```

### Étape 3: Analyser avec l'IA
```bash
# Avec le modèle RECOMMANDÉ (meilleure qualité)
python parse_and_enrich.py --model qwen2.5:14b

# OU avec le modèle par défaut
python parse_and_enrich.py

# ✅ Résultat: results/findings_enrichis.json
```

### Étape 4: Générer le rapport
```bash
python generate_report.py
# ✅ Résultat: output/rapport.pdf
```

### Étape 5: Livrer au client
```bash
# Récupérer le fichier
ls output/
# > rapport.pdf
```

## 📋 Formats de Fichiers Supportés

| Type | Formats | Exemples |
|------|---------|----------|
| Scans Automatiques | JSON, XML | `nmap -sV -oJ scan.json target` |
| Outputs Commandes | TXT, CSV | `kerbrute > kerbrute.txt` |
| Notes Manuelles | TXT, MD | `echo "Trouvé SQLi sur /login" > note.txt` |
| Messages Simples | TXT | `echo "Admin/admin marche sur FTP" > msg.txt` |
| Données Structurées | JSON, YAML, XML, CSV | Tout format structuré |

**L'IA comprend et analyse INTELLIGEMMENT tout type de contenu!**

## 🎨 Personnalisation Rapide

### Changer le modèle IA (RECOMMANDÉ)
```bash
# Voir AI_MODELS_GUIDE.md pour tous les modèles disponibles

# Installer le meilleur modèle pour l'analyse de sécurité
ollama pull qwen2.5:14b

# Utiliser avec Fricadelle
python parse_and_enrich.py --model qwen2.5:14b

# OU éditer fricadelle_config.yaml:
# ai:
#   model: "qwen2.5:14b"
```

### Changer le logo
```bash
cp mon_logo.png assets/logo.png
# Éditer config.yaml:
# report:
#   logo_path: "assets/logo.png"
```

### Changer les couleurs
```bash
# Éditer assets/style.css
# Modifier les classes .severity-badge
```

### Options en ligne de commande
```bash
# Voir toutes les options
python parse_and_enrich.py --help

# Exemples:
python parse_and_enrich.py --model qwen2.5:14b --quiet
python parse_and_enrich.py --scans-dir /path/to/scans
python parse_and_enrich.py --output custom_findings.json
python generate_report.py --output /mon/dossier
```

## 🔧 Commandes Utiles

```bash
# Tester le template
python -c "from jinja2 import Environment, FileSystemLoader; \
env = Environment(loader=FileSystemLoader('templates')); \
template = env.get_template('rapport.html.j2'); print('✅ Template OK')"

# Vérifier Ollama
ollama list

# Voir l'aide
python generate_report.py --help
python parse_and_enrich.py --help
```

## 📁 Structure du Projet

```
Fricadelle/
├── parse_and_enrich.py         # Script d'analyse IA (AMÉLIORÉ)
├── generate_report.py          # Script de génération PDF
├── config.yaml                 # Configuration audit/rapport
├── fricadelle_config.yaml      # Configuration IA (NOUVEAU)
├── requirements.txt            # Dépendances
├── AI_MODELS_GUIDE.md          # Guide modèles IA (NOUVEAU)
├── README.md                   # Documentation complète
├── QUICKSTART.md               # Ce fichier
├── ARCHITECTURE.md             # Architecture technique
├── templates/
│   └── rapport.html.j2        # Template Jinja2
├── assets/
│   ├── style.css              # Styles CSS modernes
│   └── logo.png               # Logo
├── results/
│   ├── scans/                 # ← TOUT TYPE DE FICHIER
│   └── findings_enrichis.json
└── output/
    └── rapport.pdf            # ← RAPPORT FINAL PDF
```

## ❓ Problèmes Fréquents

### "ModuleNotFoundError: No module named 'ollama'"
```bash
pip install -r requirements.txt
```

### "Connection refused" (Ollama)
```bash
# Dans un terminal séparé:
ollama serve
```

### "WeasyPrint error"
```bash
# Ubuntu/Debian:
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0

# macOS:
brew install pango
```

### Le PDF est vide
```bash
# Vérifier que findings_enrichis.json existe et contient des données
cat results/findings_enrichis.json | jq '.findings | length'
```

## 📖 Documentation Complète

- `README.md` - Documentation générale et vue d'ensemble
- `AI_MODELS_GUIDE.md` - **Guide complet des modèles IA** (NOUVEAU - À LIRE!)
- `ARCHITECTURE.md` - Architecture technique détaillée
- `fricadelle_config.yaml` - Configuration avancée de l'IA
- `example_usage.sh` - Script d'exemple

## 🎯 Workflow Recommandé

```bash
# 1. Effectuer les scans OU écrire des notes
nmap -sV -oJ nmap.json 192.168.1.0/24
kerbrute passwordspray -d domain.local users.txt > kerbrute.txt

# OU créer une note manuelle:
cat > results/scans/observations.txt << EOF
Le serveur DC01 (192.168.1.10) a SMB signing désactivé.
Admin/admin fonctionne sur le FTP de 192.168.1.50.
RDP ouvert sur Internet sans restriction IP (port 3389).
EOF

# 2. Installer le meilleur modèle IA
ollama pull qwen2.5:14b

# 3. Configurer
nano config.yaml

# 4. Lancer le pipeline avec le meilleur modèle
python parse_and_enrich.py --model qwen2.5:14b && python generate_report.py

# 5. Vérifier les résultats
xdg-open output/rapport.pdf
```

## 💡 Astuces

- **Multi-clients**: Créer un config.yaml par client
- **Versioning**: Dater les rapports (rapport_2025-11-05.pdf)
- **Backup**: Sauvegarder findings_enrichis.json
- **Confidentialité**: Ne pas commiter results/scans/ (déjà dans .gitignore)
- **Meilleure qualité**: Utiliser `qwen2.5:14b` ou `qwen2.5:32b` (voir AI_MODELS_GUIDE.md)
- **Notes manuelles**: Créer des fichiers TXT avec vos observations, l'IA les comprendra!
- **Fichiers mixtes**: Mélanger scans automatiques et notes manuelles, tout fonctionne!
- **Encodage**: Fricadelle détecte automatiquement l'encodage (UTF-8, Latin-1, etc.)

## 🤝 Support

Pour toute question:
1. Lire `README.md` et `ARCHITECTURE.md`
2. Vérifier les logs d'erreur
3. Tester avec les données d'exemple fournies

---

**Bon audit! 🛡️**
