# Guide d'Intégration dans un Projet de Widgets Orange Personnalisés

Ce guide explique pas à pas comment intégrer ce répo (ou son dossier `tempo/`) comme un nouveau dossier/sous-package dans un projet existant regroupant plusieurs widgets Orange personnalisés.

---

## 🎯 Vue d'ensemble

Le module TEMPO Visualisation v4 est conçu de manière 100% modulaire. Tous les imports internes utilisent des chemins relatifs, ce qui signifie que le dossier `tempo` ou `graphique` peut être déplacé, renommé ou hébergé à n'importe quel emplacement dans l'arborescence de votre projet.

Il existe **trois méthodes d'intégration principales** selon l'architecture de votre projet principal.

---

## 📂 Méthode 1 : Intégration en sous-package dédié (Recommandée)

Cette méthode conserve la catégorie Orange **TEMPO** séparée dans le canevas d'Orange Data Mining.

### 1. Structure des dossiers
Copiez le dossier `tempo` à la racine de votre projet ou à l'intérieur du package principal de votre projet.

**Exemple d'arborescence projet :**
```
mon_projet_orange/
├── pyproject.toml              # (ou setup.py / setup.cfg)
├── mon_package_principal/
│   ├── __init__.py
│   └── widgets/                # Vos autres widgets existants
│       ├── __init__.py
│       └── widget_perso.py
└── tempo/                       # Le dossier tempo intégré
    ├── __init__.py             # Définit la catégorie Orange TEMPO
    └── widgets/
        ├── __init__.py
        └── graphique/           # Widget et composants Plotly
            ├── __init__.py
            ├── widget_graphique.py
            ├── vue_plotly.py
            ├── plotly.min.js    # Fichier JS local hors-ligne
            ├── aide.md         # Fichier d'aide Markdown
            └── ...
```

### 2. Configuration du fichier `pyproject.toml` (ou `setup.cfg`)
Dans le fichier de configuration de votre projet principal, déclarez le point d'entrée (`entry-point`) de la catégorie TEMPO.

**Dans `pyproject.toml` :**
```toml
[project.entry-points."orange.widgets"]
"Mon Projet" = "mon_package_principal.widgets"
"TEMPO" = "tempo.widgets"

[project.entry-points."orange.widgets.help"]
"TEMPO" = "tempo.widgets:HTML_HELP_PATH"

[tool.setuptools.packages.find]
include = ["mon_package_principal*", "tempo*"]

[tool.setuptools.package-data]
"tempo.widgets.graphique" = ["*.js", "*.md", "*.html", "icons/*.png"]
```

**Ou dans `setup.cfg` :**
```ini
[options.entry_points]
orange.widgets =
    Mon Projet = mon_package_principal.widgets
    TEMPO = tempo.widgets

[options.package_data]
tempo.widgets.graphique = *.js, *.md, *.html, icons/*.png
```

---

## 📁 Méthode 2 : Regroupement dans votre dossier `widgets/` existant

Si vous souhaitez ajouter le widget **Visualisation v4** directement dans votre catégorie de widgets existante (par exemple sous la catégorie `"Mes Widgets"`).

### 1. Structure des dossiers
Copiez le dossier `graphique` (issu de `tempo/widgets/graphique/`) directement dans le dossier `widgets` de votre projet.

**Exemple d'arborescence projet :**
```
mon_projet_orange/
├── pyproject.toml
└── mon_package/
    ├── __init__.py
    └── widgets/                # Point d'entrée Orange principal
        ├── __init__.py         # Définit NAME = "Mes Widgets"
        ├── mon_widget_1.py
        └── graphique/          # Dossier graphique issu de TEMPO
            ├── __init__.py
            ├── widget_graphique.py  # Contient OWVisualisationV4
            ├── vue_plotly.py
            ├── plotly.min.js
            ├── aide.md
            └── ...
```

### 2. Adaptation de la catégorie du widget (Optionnel)
Dans `mon_package/widgets/graphique/widget_graphique.py`, vous pouvez ajuster la catégorie affichée par Orange :
```python
class OWVisualisationV4(OWWidget):
    name = "Visualisation v4"
    category = "Mes Widgets"  # Nom de votre catégorie principale
    # ...
```

### 3. Inclusion des fichiers statiques dans `pyproject.toml`
N'oubliez pas d'inclure les ressources non-Python (`plotly.min.js` et `aide.md`) :
```toml
[tool.setuptools.package-data]
"mon_package.widgets.graphique" = ["*.js", "*.md", "*.html", "icons/*.png"]
```

---

## 🔗 Méthode 3 : Intégration via Submodule Git

Si ce dépôt est maintenu dans un dépôt Git distinct, vous pouvez l'ajouter en tant que sous-module Git à la racine de votre projet :

```bash
git submodule add https://github.com/votre-orga/visu_orange_v4.git tempo_addon
```

Puis dans `pyproject.toml` de votre projet parent, vous pointez vers le package du sous-module.

---

## 📋 Dépendances requises dans le projet hôte

Assurez-vous que le fichier `pyproject.toml` ou `requirements.txt` de votre projet parent inclut l'ensemble des dépendances nécessaires :

```toml
dependencies = [
    "Orange3>=3.40.0",
    "AnyQt",
    "PyQt6",
    "PyQt6-WebEngine",
    "plotly>=5.0.0"
]
```

---

## 🧪 Validation après intégration

Une fois le dossier copié et la configuration mise à jour :

1. **Installez votre projet en mode éditable dans votre environnement Python/Orange :**
   ```bash
   pip install -e .
   ```

2. **Vérifiez que le widget apparaît bien dans Orange Canvas :**
   ```bash
   python -m Orange.canvas
   ```

3. **Exécutez la suite de tests unitaires :**
   ```bash
   pytest tests/
   ```
