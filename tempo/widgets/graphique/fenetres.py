"""Fenêtres séparées et déplaçables pour les réglages du graphique et des échelles.

Ce module contient :
1. FenetreParametresGraphique : Configuration des séries, styles, visibilité et titres.
2. FenetreEchellesAxes : Configuration indépendante des axes X et Y (linéaire, log, bornes, pas).
"""

from typing import List, Optional, Callable, Dict, Any
from AnyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QTabWidget,
    QWidget, QColorDialog, QMessageBox
)
from AnyQt.QtCore import Qt, pyqtSignal

from tempo.widgets.graphique.modele import SerieGraphique
from tempo.widgets.graphique.gestionnaire_axes import ConfigurationAxe


class FenetreParametresGraphique(QDialog):
    """Fenêtre déplaçable de paramétrage général du graphique actif."""

    signal_reglages_modifies = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Paramètres du Graphique")
        self.setMinimumSize(450, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)

        self._series: List[SerieGraphique] = []
        self._titre_graphique = ""

        layout_principal = QVBoxLayout(self)

        # Formulaire général
        form_gen = QFormLayout()
        self.edit_titre = QLineEdit(self)
        form_gen.addRow("Titre du graphique:", self.edit_titre)
        layout_principal.addLayout(form_gen)

        # Liste des séries et personnalisation du style
        grp_series = QGroupBox("Séries de données (Max 6 sélectionnées)", self)
        layout_series = QHBoxLayout(grp_series)

        self.list_series = QListWidget(self)
        self.list_series.currentRowChanged.connect(self._sur_serie_selectionnee_changee)
        layout_series.addWidget(self.list_series, stretch=1)

        # Options de la série sélectionnée
        form_style = QFormLayout()

        self.edit_alias_affiche = QLineEdit(self)
        form_style.addRow("Nom affiché:", self.edit_alias_affiche)

        self.chk_visible_serie = QCheckBox("Série visible", self)
        form_style.addRow("", self.chk_visible_serie)

        self.combo_style_ligne = QComboBox(self)
        self.combo_style_ligne.addItems(["lines+markers", "lines", "markers"])
        form_style.addRow("Style de ligne:", self.combo_style_ligne)

        self.combo_marqueur = QComboBox(self)
        self.combo_marqueur.addItems(["x", "circle", "square", "diamond", "cross"])
        form_style.addRow("Marqueur:", self.combo_marqueur)

        self.spin_taille_marqueur = QSpinBox(self)
        self.spin_taille_marqueur.setRange(2, 24)
        form_style.addRow("Taille marqueur:", self.spin_taille_marqueur)

        self.btn_couleur = QPushButton("Choisir couleur...", self)
        self.btn_couleur.clicked.connect(self._choisir_couleur_serie)
        form_style.addRow("Couleur:", self.btn_couleur)

        self.edit_unite_dst = QLineEdit(self)
        self.edit_unite_dst.setPlaceholderText("ex: rad, deg, gon")
        form_style.addRow("Unite d'affichage:", self.edit_unite_dst)

        widget_style = QWidget(self)
        widget_style.setLayout(form_style)
        layout_series.addWidget(widget_style, stretch=1)

        layout_principal.addWidget(grp_series)

        # Boutons d'action
        layout_btn = QHBoxLayout()
        btn_appliquer = QPushButton("Appliquer", self)
        btn_appliquer.clicked.connect(self._appliquer_modifications)
        btn_fermer = QPushButton("Fermer", self)
        btn_fermer.clicked.connect(self.accept)

        layout_btn.addStretch()
        layout_btn.addWidget(btn_appliquer)
        layout_btn.addWidget(btn_fermer)
        layout_principal.addLayout(layout_btn)

        self._couleur_temp = "#1f77b4"

    def charger_donnees(self, titre: str, series: List[SerieGraphique]) -> None:
        """Charge les données et la liste des séries dans la fenêtre."""
        self._titre_graphique = titre
        self._series = series
        self.edit_titre.setText(titre)

        self.list_series.clear()
        for s in series:
            item = QListWidgetItem(s.alias)
            self.list_series.addItem(item)

        if series:
            self.list_series.setCurrentRow(0)

    def _sur_serie_selectionnee_changee(self, row: int) -> None:
        """Met à jour les champs de style selon la série sélectionnée."""
        if 0 <= row < len(self._series):
            s = self._series[row]
            self.edit_alias_affiche.setText(s.alias)
            self.chk_visible_serie.setChecked(s.visible)
            idx_st = self.combo_style_ligne.findText(s.style_ligne)
            if idx_st >= 0:
                self.combo_style_ligne.setCurrentIndex(idx_st)
            idx_m = self.combo_marqueur.findText(s.symbole_marqueur)
            if idx_m >= 0:
                self.combo_marqueur.setCurrentIndex(idx_m)
            self.spin_taille_marqueur.setValue(s.taille_marqueur)
            self._couleur_temp = s.couleur
            self.edit_unite_dst.setText(s.unite_affichage_mesure or "")

    def _choisir_couleur_serie(self) -> None:
        """Ouvre un sélecteur de couleur Qt."""
        col = QColorDialog.getColor(parent=self)
        if col.isValid():
            self._couleur_temp = col.name()

    def _appliquer_modifications(self) -> None:
        """Enregistre les modifications apportées aux séries et au titre."""
        row = self.list_series.currentRow()
        if 0 <= row < len(self._series):
            s = self._series[row]
            s.alias = self.edit_alias_affiche.text().strip() or s.alias
            s.visible = self.chk_visible_serie.isChecked()
            s.style_ligne = self.combo_style_ligne.currentText()
            s.symbole_marqueur = self.combo_marqueur.currentText()
            s.taille_marqueur = self.spin_taille_marqueur.value()
            s.couleur = self._couleur_temp
            s.unite_affichage_mesure = self.edit_unite_dst.text().strip() or None

        self._titre_graphique = self.edit_titre.text().strip()
        self.signal_reglages_modifies.emit()

    def obtenir_titre(self) -> str:
        return self._titre_graphique


class FenetreEchellesAxes(QDialog):
    """Fenêtre indépendante de configuration détaillée des axes X et Y."""

    signal_echelles_modifiees = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Échelles et Bornes des Axes")
        self.setMinimumSize(420, 350)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)

        layout_principal = QVBoxLayout(self)
        self.tabs_axes = QTabWidget(self)

        # Tab Axe X
        self.tab_x = QWidget(self)
        self.form_x = self._creer_formulaire_axe(self.tab_x)
        self.tabs_axes.addTab(self.tab_x, "Axe X")

        # Tab Axe Y
        self.tab_y = QWidget(self)
        self.form_y = self._creer_formulaire_axe(self.tab_y)
        self.tabs_axes.addTab(self.tab_y, "Axe Y")

        layout_principal.addWidget(self.tabs_axes)

        # Boutons d'action
        layout_btn = QHBoxLayout()
        btn_appliquer = QPushButton("Appliquer", self)
        btn_appliquer.clicked.connect(self._appliquer_modifications)
        btn_fermer = QPushButton("Fermer", self)
        btn_fermer.clicked.connect(self.accept)

        layout_btn.addStretch()
        layout_btn.addWidget(btn_appliquer)
        layout_btn.addWidget(btn_fermer)
        layout_principal.addLayout(layout_btn)

        self._config_x: Optional[ConfigurationAxe] = None
        self._config_y: Optional[ConfigurationAxe] = None

    def _creer_formulaire_axe(self, parent: QWidget) -> Dict[str, Any]:
        layout = QVBoxLayout(parent)
        form = QFormLayout()

        edit_titre = QLineEdit(parent)
        form.addRow("Titre de l'axe:", edit_titre)

        combo_echelle = QComboBox(parent)
        combo_echelle.addItems(["linear", "log"])
        form.addRow("Type d'échelle:", combo_echelle)

        chk_auto = QCheckBox("Mode automatique (limites calculées)", parent)
        form.addRow("", chk_auto)

        spin_min = QDoubleSpinBox(parent)
        spin_min.setRange(-1e9, 1e9)
        form.addRow("Valeur min:", spin_min)

        spin_max = QDoubleSpinBox(parent)
        spin_max.setRange(-1e9, 1e9)
        form.addRow("Valeur max:", spin_max)

        spin_pas = QDoubleSpinBox(parent)
        spin_pas.setRange(0, 1e9)
        form.addRow("Pas des graduations:", spin_pas)

        chk_visible = QCheckBox("Axe visible", parent)
        chk_visible.setChecked(True)
        form.addRow("", chk_visible)

        chk_ortho = QCheckBox("Repère orthonormé", parent)
        form.addRow("", chk_ortho)

        layout.addLayout(form)
        return {
            "edit_titre": edit_titre,
            "combo_echelle": combo_echelle,
            "chk_auto": chk_auto,
            "spin_min": spin_min,
            "spin_max": spin_max,
            "spin_pas": spin_pas,
            "chk_visible": chk_visible,
            "chk_ortho": chk_ortho
        }

    def charger_configurations(self, config_x: ConfigurationAxe, config_y: ConfigurationAxe) -> None:
        """Remplit le formulaire avec les configurations actuelles."""
        self._config_x = config_x
        self._config_y = config_y

        self._remplir_form(self.form_x, config_x)
        self._remplir_form(self.form_y, config_y)

    def _remplir_form(self, form: Dict[str, Any], cfg: ConfigurationAxe) -> None:
        form["edit_titre"].setText(cfg.titre)
        idx = form["combo_echelle"].findText(cfg.type_echelle)
        if idx >= 0:
            form["combo_echelle"].setCurrentIndex(idx)
        form["chk_auto"].setChecked(cfg.mode_automatique)
        form["spin_min"].setValue(cfg.valeur_min if cfg.valeur_min is not None else 0.0)
        form["spin_max"].setValue(cfg.valeur_max if cfg.valeur_max is not None else 100.0)
        form["spin_pas"].setValue(cfg.pas_graduation if cfg.pas_graduation is not None else 0.0)
        form["chk_visible"].setChecked(cfg.visible)
        form["chk_ortho"].setChecked(cfg.est_orthonorme)

    def _sauvegarder_form(self, form: Dict[str, Any], cfg: ConfigurationAxe) -> None:
        cfg.titre = form["edit_titre"].text().strip()
        cfg.type_echelle = form["combo_echelle"].currentText()
        cfg.mode_automatique = form["chk_auto"].isChecked()
        if not cfg.mode_automatique:
            v_min = form["spin_min"].value()
            v_max = form["spin_max"].value()
            if cfg.type_echelle == "log" and v_min <= 0:
                QMessageBox.warning(self, "Attention", "Pour une échelle log, la valeur min doit être strictement positive (> 0). Ajustement automatique à 0.1.")
                v_min = 0.1
            cfg.valeur_min = v_min
            cfg.valeur_max = v_max
        pas = form["spin_pas"].value()
        cfg.pas_graduation = pas if pas > 0 else None
        cfg.visible = form["chk_visible"].isChecked()
        cfg.est_orthonorme = form["chk_ortho"].isChecked()

    def _appliquer_modifications(self) -> None:
        if self._config_x and self._config_y:
            self._sauvegarder_form(self.form_x, self._config_x)
            self._sauvegarder_form(self.form_y, self._config_y)
            self.signal_echelles_modifiees.emit()
