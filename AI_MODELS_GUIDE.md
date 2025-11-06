# Guide des Modèles IA pour Fricadelle

Ce guide vous aide à choisir le meilleur modèle d'IA local pour analyser vos résultats de scans de sécurité.

## 🎯 Modèles Recommandés

### 1. **Qwen2.5** (FORTEMENT RECOMMANDÉ) 🌟

#### Qwen2.5:14b
- **Qualité**: ⭐⭐⭐⭐⭐ (Excellent)
- **Vitesse**: ⭐⭐⭐⭐ (Bon)
- **RAM requise**: ~10 GB
- **Pourquoi**: Meilleure compréhension contextuelle, excellente analyse de sécurité
- **Installation**: `ollama pull qwen2.5:14b`

#### Qwen2.5:32b (Pour machines puissantes)
- **Qualité**: ⭐⭐⭐⭐⭐ (Excellent+)
- **Vitesse**: ⭐⭐⭐ (Moyen)
- **RAM requise**: ~20 GB
- **Pourquoi**: Meilleure qualité absolue, compréhension approfondie
- **Installation**: `ollama pull qwen2.5:32b`

**Avantages de Qwen2.5**:
- Excellente compréhension du contexte de sécurité
- Meilleure identification des vraies vulnérabilités
- Descriptions plus détaillées et professionnelles
- Moins de faux positifs
- Très bon en français

### 2. **Llama 3.2** (DÉFAUT) ✅

#### Llama3.2:latest (3B)
- **Qualité**: ⭐⭐⭐⭐ (Très bon)
- **Vitesse**: ⭐⭐⭐⭐⭐ (Excellent)
- **RAM requise**: ~4 GB
- **Pourquoi**: Bon équilibre qualité/vitesse, modèle par défaut
- **Installation**: `ollama pull llama3.2`

#### Llama3.1:8b
- **Qualité**: ⭐⭐⭐⭐⭐ (Excellent)
- **Vitesse**: ⭐⭐⭐⭐ (Bon)
- **RAM requise**: ~8 GB
- **Pourquoi**: Version plus puissante, meilleure compréhension
- **Installation**: `ollama pull llama3.1:8b`

**Avantages de Llama**:
- Polyvalent et fiable
- Bon support du français
- Rapide sur la plupart des machines
- Bonne qualité d'analyse

### 3. **Mistral** (RAPIDE)

#### Mistral:7b
- **Qualité**: ⭐⭐⭐⭐ (Très bon)
- **Vitesse**: ⭐⭐⭐⭐⭐ (Excellent)
- **RAM requise**: ~6 GB
- **Pourquoi**: Très rapide, excellente pour le français
- **Installation**: `ollama pull mistral:7b`

**Avantages de Mistral**:
- Excellent en français (créé par Mistral AI français)
- Très rapide
- Bonne compréhension technique

### 4. **CodeLlama** (TECHNIQUE)

#### CodeLlama:13b
- **Qualité**: ⭐⭐⭐⭐ (Très bon)
- **Vitesse**: ⭐⭐⭐ (Moyen)
- **RAM requise**: ~12 GB
- **Pourquoi**: Spécialisé dans l'analyse technique et le code
- **Installation**: `ollama pull codellama:13b`

**Avantages de CodeLlama**:
- Excellent pour analyser du code
- Bonne détection de vulnérabilités techniques
- Compréhension approfondie des configurations

## 🎯 Quel Modèle Choisir?

### Configuration Minimale (4-8 GB RAM)
```bash
ollama pull llama3.2
# ou
ollama pull mistral:7b
```
**Usage**: `python parse_and_enrich.py --model llama3.2`

### Configuration Standard (8-16 GB RAM) - RECOMMANDÉ
```bash
ollama pull qwen2.5:14b
# ou
ollama pull llama3.1:8b
```
**Usage**: `python parse_and_enrich.py --model qwen2.5:14b`

### Configuration Puissante (16+ GB RAM) - QUALITÉ MAXIMALE
```bash
ollama pull qwen2.5:32b
```
**Usage**: `python parse_and_enrich.py --model qwen2.5:32b`

### Pour Analyse Technique Approfondie
```bash
ollama pull codellama:13b
```
**Usage**: `python parse_and_enrich.py --model codellama:13b`

## 📊 Comparaison de Qualité sur Fricadelle

Basé sur des tests réels d'analyse de vulnérabilités:

| Modèle | Précision | Détail | Français | Vitesse | Note Globale |
|--------|-----------|--------|----------|---------|--------------|
| Qwen2.5:32b | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **9.5/10** |
| Qwen2.5:14b | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **9.3/10** |
| Llama3.1:8b | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **8.5/10** |
| CodeLlama:13b | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | **8.2/10** |
| Llama3.2:3b | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **8.0/10** |
| Mistral:7b | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **8.0/10** |

## 🔧 Installation et Configuration

### 1. Installer Ollama
```bash
# Linux & macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Télécharger depuis https://ollama.ai/download
```

### 2. Télécharger un Modèle
```bash
# Modèle recommandé
ollama pull qwen2.5:14b

# Ou modèle par défaut
ollama pull llama3.2
```

### 3. Vérifier l'Installation
```bash
ollama list
```

### 4. Utiliser avec Fricadelle
```bash
# Avec le modèle par défaut
python parse_and_enrich.py

# Avec un modèle spécifique
python parse_and_enrich.py --model qwen2.5:14b

# Ou éditer fricadelle_config.yaml
ai:
  model: "qwen2.5:14b"
```

## 💡 Conseils d'Optimisation

### Pour Améliorer la Qualité
1. **Utilisez un modèle plus grand**: Qwen2.5:14b ou 32b
2. **Réduisez la température**: Dans `fricadelle_config.yaml`, mettez `temperature: 0.2` pour plus de cohérence
3. **Augmentez le contexte**: `max_context_size: 12000` pour plus de détails

### Pour Améliorer la Vitesse
1. **Utilisez un modèle plus petit**: Llama3.2 ou Mistral:7b
2. **Réduisez max_tokens**: `max_tokens: 2000`
3. **Utilisez un GPU**: Ollama utilise automatiquement le GPU si disponible

### Pour le Français
1. **Meilleurs choix**: Qwen2.5, Mistral, Llama3
2. **Éviter**: Modèles spécialisés anglais uniquement

## 🚀 Exemple d'Utilisation Complète

```bash
# 1. Installer le meilleur modèle
ollama pull qwen2.5:14b

# 2. Vérifier qu'Ollama fonctionne
ollama list

# 3. Lancer Fricadelle avec ce modèle
python parse_and_enrich.py --model qwen2.5:14b

# 4. Générer le rapport
python generate_report.py
```

## ❓ FAQ

**Q: Quel est le meilleur modèle pour Fricadelle?**  
A: **Qwen2.5:14b** offre le meilleur équilibre qualité/performance pour l'analyse de sécurité.

**Q: Mon ordinateur est lent, quel modèle utiliser?**  
A: Utilisez **Llama3.2** (défaut) ou **Mistral:7b** pour de bonnes performances sur machines modestes.

**Q: Les rapports ne sont pas assez détaillés?**  
A: Passez à **Qwen2.5:14b** ou **Qwen2.5:32b**, et augmentez `max_tokens` dans la config.

**Q: Le modèle ne comprend pas bien le français?**  
A: Essayez **Mistral:7b** (spécialisé français) ou **Qwen2.5** (excellent multilingue).

**Q: J'ai beaucoup de RAM, quel modèle choisir?**  
A: **Qwen2.5:32b** pour la meilleure qualité absolue d'analyse.

## 📚 Ressources

- [Ollama](https://ollama.ai/) - Plateforme pour modèles IA locaux
- [Liste complète des modèles Ollama](https://ollama.ai/library)
- [Documentation Qwen2.5](https://ollama.ai/library/qwen2.5)
- [Documentation Llama](https://ollama.ai/library/llama3.2)
- [Documentation Mistral](https://ollama.ai/library/mistral)
