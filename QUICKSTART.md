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

# 4. Télécharger un modèle IA
ollama pull llama3.2
```

## 🚀 Utilisation en 5 Étapes

### Étape 1: Placer vos scans
```bash
cp vos_scans/* results/scans/
```

### Étape 2: Configurer le client
```bash
# Éditer config.yaml
nano config.yaml
# Modifier: client_name, audit_date, scope, testeurs
```

### Étape 3: Analyser avec l'IA
```bash
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

## 📋 Formats de Scan Supportés

| Outil | Format | Exemple |
|-------|--------|---------|
| Nmap | JSON | `nmap -sV -oJ scan.json target` |
| Kerbrute | TXT | `kerbrute > kerbrute.txt` |
| CrackMapExec | TXT | `crackmapexec smb 10.0.0.1 > cme.txt` |
| Nuclei | JSON | `nuclei -json-export nuclei.json` |
| Hashcat | TXT | `hashcat hash.txt > hashcat.txt` |
| Custom | TXT/JSON/CSV | N'importe quel outil |

## 🎨 Personnalisation Rapide

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

### Format de sortie
```bash
# Générer le rapport PDF
python generate_report.py

# Spécifier un répertoire de sortie différent
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
├── parse_and_enrich.py       # Script d'analyse IA avancée
├── generate_report.py         # Script de génération PDF
├── config.yaml                # Configuration
├── requirements.txt           # Dépendances
├── templates/
│   └── rapport.html.j2       # Template Jinja2
├── assets/
│   ├── style.css             # Styles CSS modernes
│   └── logo.png              # Logo
├── results/
│   ├── scans/                # ← VOS SCANS ICI
│   └── findings_enrichis.json
└── output/
    └── rapport.pdf           # ← RAPPORT FINAL PDF
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

- `README.md` - Documentation générale
- `ARCHITECTURE.md` - Architecture technique détaillée
- `example_usage.sh` - Script d'exemple

## 🎯 Workflow Recommandé

```bash
# 1. Effectuer les scans
nmap -sV -oJ nmap.json 192.168.1.0/24
kerbrute passwordspray -d domain.local users.txt > kerbrute.txt

# 2. Copier dans results/scans/
mv nmap.json kerbrute.txt results/scans/

# 3. Configurer
nano config.yaml

# 4. Lancer le pipeline
python parse_and_enrich.py && python generate_report.py

# 5. Vérifier les résultats
xdg-open output/rapport.pdf
```

## 💡 Astuces

- **Multi-clients**: Créer un config.yaml par client
- **Versioning**: Dater les rapports (rapport_2025-11-05.pdf)
- **Backup**: Sauvegarder findings_enrichis.json
- **Confidentialité**: Ne pas commiter results/scans/ (déjà dans .gitignore)

## 🤝 Support

Pour toute question:
1. Lire `README.md` et `ARCHITECTURE.md`
2. Vérifier les logs d'erreur
3. Tester avec les données d'exemple fournies

---

**Bon audit! 🛡️**
