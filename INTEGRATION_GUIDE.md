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

## 📁 Méthode 2 : Remplissage direct du dossier `Visualisation/` de votre projet (Recommandé pour votre structure)

Si votre projet possède une arborescence avec un dossier `Visualisation/` sous `Widgets/` :

```
Mon-projet/
├── __init__.py
└── Dossier_projet/
    ├── __init__.py
    └── Widgets/
        ├── __init__.py
        ├── Categorie1/
        │   └── Widget1.py
        └── Visualisation/      <-- Dossier à remplir avec le contenu enrichi
            ├── __init__.py
            ├── widget_graphique.py
            ├── adaptation_metier.py
            ├── conversions.py
            ├── exportation.py
            ├── fenetres.py
            ├── gestionnaire_axes.py
            ├── gestionnaire_graphiques.py
            ├── modele.py
            ├── panneau_options.py
            ├── plotly.min.js
            ├── test_autonome.py
            ├── vue_plotly.py
            └── aide.md
```

### 1. Remplissage du dossier `Visualisation/`
Copiez tous les fichiers situés dans `tempo/widgets/graphique/` directement dans le dossier `Mon-projet/Dossier_projet/Widgets/Visualisation/`.

### 2. Contenu du fichier `Visualisation/__init__.py`
Afin qu'Orange Canvas découvre correctement le widget tout en exposant sa classe, assurez-vous que `Visualisation/__init__.py` contient :

```python
from .widget_graphique import OWVisualisationV4

__all__ = ["OWVisualisationV4"]
```

### 3. Connexion d'entrée et compatibilité avec vos objets métiers
Le widget possède une entrée unique déclarant :
```python
class Inputs:
    donnees_objet = Input("Données Objet", Any, auto_summary=False)
```
Grâce au composant `AdaptateurMetier`, le widget accepte directement vos instances d'objets métiers (Mesure, Trajectoire, Point, structures CTypes, etc.).
Aucun autre widget ne peut s'interposer si ses types de sortie ne sont pas compatibles : l'entrée gère l'extraction directe et sécurisée des données sans jamais modifier vos objets originaux.

### 4. Configuration des Entry Points dans `setup.cfg` ou `pyproject.toml`
Pour que la catégorie `Visualisation` apparaisse dans Orange Canvas :

**Dans `setup.cfg` :**
```ini
[options.entry_points]
orange.widgets =
    Mes Widgets = Dossier_projet.Widgets
```

**Ou dans `pyproject.toml` :**
```toml
[project.entry-points."orange.widgets"]
"Mes Widgets" = "Dossier_projet.Widgets"

[tool.setuptools.package-data]
"Dossier_projet.Widgets.Visualisation" = ["*.js", "*.md", "*.html"]
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
