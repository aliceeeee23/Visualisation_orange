# Aide - Visualisation TEMPO v4

Bienvenue dans le widget **TEMPO Visualisation v4** pour Orange Data Mining.

---

## 1. Entrée du Widget
- **Entrée exigée** : `Données Objet` (Single / Non-blocking).
- **Objets supportés** :
  - **Mesure** : série individuelle de points.
  - **Trajectoire** : ensemble de 9 mesures (Position X, Y, Z, Vitesse X, Y, Z, Accélération X, Y, Z).
  - **Collection de Mesures** : listes ou tuples d'objets métier compatibles.

---

## 2. Affichage Automatique et Onglets
- Les données reçues sont **automatiquement affichées** sans nécessiter de clic sur un bouton *Tracer*.
- L'interface supporte la création de **plusieurs graphiques indépendants** organisés par onglets.
- Chaque onglet conserve sa propre configuration d'axes, d'échelles, de sélection de séries (jusqu'à 6 séries actives) et de styles.

---

## 3. Modes de Représentation
1. **Mesure / Repère** :
   - L'axe X représente la coordonnée `repere` (temps, distance, index).
   - L'axe Y représente la `valeur` mesurée.
2. **Mesure / Mesure** :
   - L'axe X correspond à une première mesure sélectionnée.
   - L'axe Y correspond à une seconde mesure sélectionnée.
   - Les points sont automatiquement alignés selon leur `repere` avec une tolérance paramétrable.

---

## 4. Gestion de la Validité des Points
- **Convention** :
  - `validite == 1` : point valide.
  - `validite == 0` : point invalide.
- Les points invalides peuvent être masqués ou affichés à l'écran via la case à cocher **Invalides**.
- **Important** : Le masquage visuel ne modifie **jamais** les données métier d'origine.

---

## 5. Échelles et Axes
- Accès via le bouton **Échelles...**.
- Support des échelles **linéaires** et **logarithmiques**.
- Sécurisation contre le crash en échelle logarithmique (filtrage des valeurs nulles ou négatives).
- Configuration automatique ou manuelle des bornes min/max et du pas de graduation.
- Support du mode **repère orthonormé**.

---

## 6. Exportations
- Accès via le bouton **Exporter...**.
- Formats pris en charge : **PNG** et **PDF**.
- Le rendu exporté conserve fidèlement les couleurs, le titre, les unités, et la sélection visuelle sans nécessiter de connexion Internet.
