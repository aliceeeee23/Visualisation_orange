"""Panneau d'options rapides et commandes compactes pour TEMPO.

Ce module implémente la barre/panneau compact pour basculer rapidement entre
les modes de représentation, réinitialiser le zoom, basculer la grille et la légende,
ou accéder aux fenêtres de réglages avancés.
"""

from typing import Optional
from AnyQt.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QComboBox, QCheckBox, QLabel, QFrame
)
from AnyQt.QtCore import pyqtSignal, Qt


class PanneauOptionsRapides(QFrame):
    """Barre de commandes compacte sous/sur le graphique."""

    signal_mode_change = pyqtSignal(str)
    signal_invalides_toggled = pyqtSignal(bool)
    signal_grille_toggled = pyqtSignal(bool)
    signal_legende_toggled = pyqtSignal(bool)
    signal_ouvrir_parametres = pyqtSignal()
    signal_ouvrir_echelles = pyqtSignal()
    signal_ouvrir_export = pyqtSignal()
    signal_ouvrir_aide = pyqtSignal()
    signal_restaurer_masques = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(10)

        # Mode de représentation
        layout.addWidget(QLabel("Mode:"))
        self.combo_mode = QComboBox(self)
        self.combo_mode.addItems(["Mesure / Repere", "Mesure / Mesure"])
        self.combo_mode.currentTextChanged.connect(self.signal_mode_change.emit)
        layout.addWidget(self.combo_mode)

        # Cases à cocher rapides
        self.chk_invalides = QCheckBox("Invalides", self)
        self.chk_invalides.setChecked(True)
        self.chk_invalides.toggled.connect(self.signal_invalides_toggled.emit)
        layout.addWidget(self.chk_invalides)

        self.chk_grille = QCheckBox("Grille", self)
        self.chk_grille.setChecked(True)
        self.chk_grille.toggled.connect(self.signal_grille_toggled.emit)
        layout.addWidget(self.chk_grille)

        self.chk_legende = QCheckBox("Légende", self)
        self.chk_legende.setChecked(True)
        self.chk_legende.toggled.connect(self.signal_legende_toggled.emit)
        layout.addWidget(self.chk_legende)

        layout.addStretch()

        # Boutons d'action
        self.btn_restaurer = QPushButton("Restaure masqués", self)
        self.btn_restaurer.setToolTip("Restaure la visibilité de tous les points masqués de la sélection")
        self.btn_restaurer.clicked.connect(self.signal_restaurer_masques.emit)
        layout.addWidget(self.btn_restaurer)

        self.btn_echelles = QPushButton("Échelles...", self)
        self.btn_echelles.clicked.connect(self.signal_ouvrir_echelles.emit)
        layout.addWidget(self.btn_echelles)

        self.btn_params = QPushButton("Réglages...", self)
        self.btn_params.clicked.connect(self.signal_ouvrir_parametres.emit)
        layout.addWidget(self.btn_params)

        self.btn_export = QPushButton("Exporter...", self)
        self.btn_export.clicked.connect(self.signal_ouvrir_export.emit)
        layout.addWidget(self.btn_export)

        self.btn_aide = QPushButton("?", self)
        self.btn_aide.setFixedWidth(28)
        self.btn_aide.clicked.connect(self.signal_ouvrir_aide.emit)
        layout.addWidget(self.btn_aide)
