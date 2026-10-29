# TEMPO Visualisation v4 - Extension Orange Data Mining

Bibliothèque Python et catégorie de widgets de visualisation scientifique **TEMPO v4** pour **Orange Data Mining** (Orange 3.40.0, Python 3.12, PyQt6 / AnyQt, Plotly).

---

## 🚀 Présentation
TEMPO Visualisation v4 fournit une interface interactive scientifique complète, 100% hors-ligne, permettant d'afficher, manipuler et exporter des données métier complexes (Mesures, Trajectoires à 9 séries, structures ctypes) reçues depuis l'entrée Orange `Données Objet`.

---

## 📦 Structure du Projet

```
visu_orange_v4/
├── pyproject.toml              # Configuration du packaging Python & points d'entrée Orange
├── setup.cfg                   # Métadonnées et configuration d'installation
├── requirements.txt            # Dépendances requises
├── README.md                   # Documentation d'installation, d'usage et métier
├── INTEGRATION_GUIDE.md        # Guide d'intégration comme dossier dans un projet de widgets Orange
├── tempo/
│   ├── __init__.py             # Déclaration du package TEMPO
│   └── widgets/
│       ├── __init__.py         # Catégorie de widgets TEMPO
│       └── graphique/
│           ├── __init__.py
│           ├── widget_graphique.py         # Widget Orange OWVisualisationV4 ("Données Objet")
│           ├── modele.py                   # Représentation interne normalisée des séries/points
│           ├── adaptation_metier.py        # Couche d'adaptation métier (Mesure, Point, Trajectoire)
│           ├── vue_plotly.py               # Composant Plotly local hors-ligne (QWebEngineView)
│           ├── gestionnaire_graphiques.py  # Gestion des onglets de graphiques indépendants
│           ├── gestionnaire_axes.py        # Axes, échelles (lin/log), bornes et graduations
│           ├── conversions.py              # Conversions d'unités (angles deg, rad, gon)
│           ├── panneau_options.py          # Barre compacte de raccourcis
│           ├── fenetres.py                 # Fenêtres flottantes de réglages et d'échelles
│           ├── exportation.py              # Exportation PNG et PDF hors-ligne
│           ├── aide.md                     # Aide intégrée en Markdown
│           ├── plotly.min.js               # Ressource JavaScript Plotly locale embarquée
│           └── test_autonome.py            # Test autonome de démonstration Qt/Plotly
└── tests/
    ├── __init__.py
    ├── test_modele.py              # Tests de la couche d'adaptation et des collections
    ├── test_conversions.py         # Tests des conversions d'unités et de la logique log
    └── test_validite.py            # Tests de la convention de validité (1=valide, 0=invalide)
```

---

## 📚 Intégration dans un Projet de Widgets Personnalisés
Pour intégrer ce dépôt ou le dossier `tempo/` comme un nouveau dossier/sous-package dans votre projet global regroupant vos widgets Orange personnalisés, consultez le guide dédié : **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)**.

Il présente 3 méthodes d'intégration (sous-package dédié, regroupement dans votre dossier `widgets/`, ou sous-module Git) avec les exemples de configuration `pyproject.toml` / `setup.cfg`.

---

## 🔧 Installation Hors-Ligne

### 1. Installation en mode développeur
Dans l'environnement Python utilisé par Orange 3.40.0 :
```bash
python -m pip install -e .
```

### 2. Construction de la roue (Wheel) pour distribution isolée du réseau
```bash
python -m build --wheel
```
Le fichier `.whl` généré dans `dist/` peut ensuite être installé hors-ligne via :
```bash
python -m pip install dist/visu_orange_v4-4.0.0-py3-none-any.whl --no-index --find-links ./wheels/
```

---

## 🧪 Lancement des Tests

### 1. Suite de tests unitaires (Pytest)
```bash
pytest tests/
```

### 2. Test autonome de démonstration (hors Orange)
```bash
python tempo/widgets/graphique/test_autonome.py
```

---

## 🔍 Éléments Métier à Vérifier avec la DLL / Bibliothèque Native
Lors de l'intégration finale avec la DLL / bibliothèque C native :
1. **Classe `Unite`** : Vérifier le nom exact des méthodes de conversion dynamique (ex: `Unite.obtenir_coefficient(src, dst)`).
2. **Classe `Attribut`** : Confirmer la structure des clés/valeurs de métadonnées associées aux mesures.
3. **Champs ctypes `Point`** : Confirmer que les champs `repere`, `valeur` (ou `mesure`), et `validite` conservent leurs offsets actuels.
4. **Validité** : Respecter la convention impérative `validite == 1` (valide) et `validite == 0` (invalide).
