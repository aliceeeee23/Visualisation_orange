"""Script de test autonome pour TEMPO Visualisation v4.

Ce script génère des données synthétiques (Mesure, Trajectoire avec 9 séries,
points valides et invalides, ctypes) et démarre une application Qt affichant
le widget sans nécessiter la DLL métier native ni l'environnement complet Orange.
"""

import sys
import math
import logging
from typing import List

from AnyQt.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from AnyQt.QtCore import Qt

import os
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

try:
    from .widget_graphique import OWVisualisationV4
except (ImportError, ValueError):
    from tempo.widgets.graphique.widget_graphique import OWVisualisationV4

logging.basicConfig(level=logging.INFO)


class PointSimule:
    """Simulation de la classe Point métier."""
    def __init__(self, repere: float, valeur: float, validite: int = 1) -> None:
        self.repere = repere
        self.valeur = valeur
        self.validite = validite  # 1 = valide, 0 = invalide


class MesureSimulee:
    """Simulation de la classe Mesure métier."""
    def __init__(self, alias: str, points: List[PointSimule], unite_repere: str = "s", unite_mesure: str = "m") -> None:
        self.alias = alias
        self.points = points
        self.unite_repere = unite_repere
        self.unite_mesure = unite_mesure


class TrajectoireSimulee:
    """Simulation de la classe Trajectoire métier (9 mesures)."""
    def __init__(self) -> None:
        noms_9 = [
            ("pos_x", "Position X (m)"), ("pos_y", "Position Y (m)"), ("pos_z", "Position Z (m)"),
            ("vit_x", "Vitesse X (m/s)"), ("vit_y", "Vitesse Y (m/s)"), ("vit_z", "Vitesse Z (m/s)"),
            ("acc_x", "Accélération X (m/s²)"), ("acc_y", "Accélération Y (m/s²)"), ("acc_z", "Accélération Z (m/s²)")
        ]
        self.mesures = []
        for attr, nom in noms_9:
            pts = []
            for i in range(20):
                t = float(i)
                # Intégrer quelques points invalides (ex: i == 5)
                val = math.sin(t * 0.5) if "pos" in attr else math.cos(t * 0.5)
                statut = 0 if i in [5, 12] else 1
                pts.append(PointSimule(t, val, statut))
            m = MesureSimulee(nom, pts)
            setattr(self, attr, m)
            self.mesures.append(m)


def executer_test_autonome() -> None:
    """Exécute l'application de démonstration autonome."""
    app = QApplication.instance() or QApplication(sys.argv)

    fenetre = QMainWindow()
    fenetre.setWindowTitle("Démonstration Autonome - TEMPO Visualisation v4")
    fenetre.resize(1000, 700)

    widget_principal = QWidget()
    layout = QVBoxLayout(widget_principal)

    widget_tempo = OWVisualisationV4()
    layout.addWidget(widget_tempo)

    # Données synthétiques
    traj = TrajectoireSimulee()

    # Charger les 9 mesures (les 6 premières seront automatiquement affichées)
    widget_tempo.definir_donnees_objet(traj)

    fenetre.setCentralWidget(widget_principal)
    fenetre.show()

    print("Test autonome démarré avec succès. Les 6 premières séries de la trajectoire sont affichées.")

    # Si exécuté en mode interactif non-headless, démarrer la boucle d'événements
    if "--no-exec" not in sys.argv and os.environ.get("QT_QPA_PLATFORM") != "offscreen":
        sys.exit(app.exec())


if __name__ == "__main__":
    import os
    executer_test_autonome()
