"""Gestionnaire d'onglets de graphiques indépendants TEMPO.

Ce module permet de créer, supprimer et basculer entre plusieurs onglets
de graphiques indépendants, chacun conservant sa propre configuration
de séries, d'axes, de mode de représentation et de style.
"""

from typing import List, Dict, Optional, Any
from AnyQt.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QToolButton, QInputDialog, QMessageBox
)
from AnyQt.QtCore import pyqtSignal

from tempo.widgets.graphique.modele import CollectionSeries, SerieGraphique
from tempo.widgets.graphique.gestionnaire_axes import ConfigurationAxe
from tempo.widgets.graphique.vue_plotly import VueGraphiquePlotly
from tempo.widgets.graphique.panneau_options import PanneauOptionsRapides
from tempo.widgets.graphique.fenetres import FenetreParametresGraphique, FenetreEchellesAxes


class GraphiqueOnglet(QWidget):
    """Représente un onglet individuel de graphique avec son modèle et sa vue."""

    def __init__(self, nom_onglet: str, collection_global: CollectionSeries, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.nom_onglet = nom_onglet
        self.collection_global = collection_global

        self.config_x = ConfigurationAxe(titre="Axe X (Repère)")
        self.config_y = ConfigurationAxe(titre="Axe Y (Valeur)")
        self.titre_graphique = nom_onglet

        self.ids_series_selectionnees: List[str] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Panneau rapide
        self.panneau = PanneauOptionsRapides(self)
        layout.addWidget(self.panneau)

        # Vue graphique Plotly QWebEngineView
        self.vue = VueGraphiquePlotly(self)
        layout.addWidget(self.vue)

        # Connexions du panneau rapide
        self.panneau.signal_mode_change.connect(self._sur_mode_change)
        self.panneau.signal_invalides_toggled.connect(self._sur_invalides_toggled)
        self.panneau.signal_grille_toggled.connect(self._sur_grille_toggled)
        self.panneau.signal_legende_toggled.connect(self._sur_legende_toggled)
        self.panneau.signal_restaurer_masques.connect(self._sur_restaurer_masques)

    def _sur_mode_change(self, mode: str) -> None:
        self.vue.mode_representation = mode
        self.actualiser()

    def _sur_invalides_toggled(self, active: bool) -> None:
        self.vue.afficher_points_invalides = active
        self.actualiser()

    def _sur_grille_toggled(self, active: bool) -> None:
        self.vue.afficher_grille = active
        self.actualiser()

    def _sur_legende_toggled(self, active: bool) -> None:
        self.vue.afficher_legende = active
        self.actualiser()

    def _sur_restaurer_masques(self) -> None:
        series = self.collection_global.obtenir_series_selectionnees(self.ids_series_selectionnees)
        for s in series:
            s.restaurer_tous_masques()
        self.actualiser()

    def actualiser(self) -> None:
        """Actualise le rendu Plotly avec les séries sélectionnées."""
        series = self.collection_global.obtenir_series_selectionnees(self.ids_series_selectionnees)
        self.vue.actualiser_graphique(
            series, self.config_x, self.config_y, self.titre_graphique
        )


class GestionnaireGraphiques(QWidget):
    """Widget principal gérant les onglets de graphiques indépendants."""

    signal_ouvrir_export = pyqtSignal(GraphiqueOnglet)
    signal_ouvrir_aide = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.collection_series = CollectionSeries()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._sur_fermer_onglet)
        layout.addWidget(self.tab_widget)

        # Bouton '+' pour ajouter un onglet
        btn_add = QToolButton(self)
        btn_add.setText("+")
        btn_add.setToolTip("Créer un nouveau graphique indépendant")
        btn_add.clicked.connect(self.creer_nouveau_graphique)
        self.tab_widget.setCornerWidget(btn_add)

        # Fenêtres modales de réglages
        self.fenetre_params = FenetreParametresGraphique(self)
        self.fenetre_params.signal_reglages_modifies.connect(self._sur_reglages_graphique_modifies)

        self.fenetre_echelles = FenetreEchellesAxes(self)
        self.fenetre_echelles.signal_echelles_modifiees.connect(self._sur_echelles_modifiees)

        # Créer le premier onglet initial
        self.creer_nouveau_graphique("Graphique 1")

    def obtenir_graphique_actif(self) -> Optional[GraphiqueOnglet]:
        """Retourne l'onglet graphique actuellement sélectionné."""
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, GraphiqueOnglet):
            return widget
        return None

    def creer_nouveau_graphique(self, nom: Optional[str] = None) -> GraphiqueOnglet:
        """Crée un nouvel onglet de graphique indépendant."""
        if not nom:
            index = self.tab_widget.count() + 1
            nom, ok = QInputDialog.getText(self, "Nouveau Graphique", "Nom du graphique:", text=f"Graphique {index}")
            if not ok or not nom.strip():
                nom = f"Graphique {index}"

        onglet = GraphiqueOnglet(nom, self.collection_series, self)

        # Connecter les boutons de fenêtres annexes
        onglet.panneau.signal_ouvrir_parametres.connect(self.ouvrir_fenetre_parametres)
        onglet.panneau.signal_ouvrir_echelles.connect(self.ouvrir_fenetre_echelles)
        onglet.panneau.signal_ouvrir_export.connect(lambda: self.signal_ouvrir_export.emit(onglet))
        onglet.panneau.signal_ouvrir_aide.connect(self.signal_ouvrir_aide.emit)

        idx = self.tab_widget.addTab(onglet, nom)
        self.tab_widget.setCurrentIndex(idx)
        onglet.actualiser()
        return onglet

    def _sur_fermer_onglet(self, index: int) -> None:
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            QMessageBox.information(self, "Information", "Au moins un graphique doit rester ouvert.")

    def ouvrir_fenetre_parametres(self) -> None:
        """Ouvre la fenêtre de réglages pour le graphique actif."""
        onglet = self.obtenir_graphique_actif()
        if onglet:
            series = self.collection_series.obtenir_series_selectionnees(onglet.ids_series_selectionnees)
            self.fenetre_params.charger_donnees(onglet.titre_graphique, series)
            self.fenetre_params.show()
            self.fenetre_params.raise_()

    def ouvrir_fenetre_echelles(self) -> None:
        """Ouvre la fenêtre dédiée aux axes et échelles pour le graphique actif."""
        onglet = self.obtenir_graphique_actif()
        if onglet:
            self.fenetre_echelles.charger_configurations(onglet.config_x, onglet.config_y)
            self.fenetre_echelles.show()
            self.fenetre_echelles.raise_()

    def _sur_reglages_graphique_modifies(self) -> None:
        onglet = self.obtenir_graphique_actif()
        if onglet:
            onglet.titre_graphique = self.fenetre_params.obtenir_titre()
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), onglet.titre_graphique)
            onglet.actualiser()

    def _sur_echelles_modifiees(self) -> None:
        onglet = self.obtenir_graphique_actif()
        if onglet:
            onglet.actualiser()

    def mettre_a_jour_donnees(self, liste_dict_mesures: List[Dict[str, Any]]) -> None:
        """Met à jour les séries globales à partir des nouvelles données récepteionnées."""
        # Conserver les réglages des graphiques existants en ne vidant pas tout
        self.collection_series.series.clear()
        self.collection_series.ordre_series.clear()

        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

        for idx, m_data in enumerate(liste_dict_mesures):
            id_s = f"s_{idx}"
            from tempo.widgets.graphique.modele import PointGraphique
            pts_obj = [
                PointGraphique(repere=p[0], valeur=p[1], validite=p[2])
                for p in m_data["points"]
            ]
            couleur = colors[idx % len(colors)]
            serie = SerieGraphique(
                id_serie=id_s,
                alias=m_data["alias"],
                points=pts_obj,
                unite_repere=m_data.get("unite_repere"),
                unite_mesure=m_data.get("unite_mesure"),
                couleur=couleur,
                objet_metier_origine=m_data.get("objet_origine")
            )
            self.collection_series.ajouter_ou_mettre_a_jour(serie)

        # Actualiser tous les onglets ouverts
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, GraphiqueOnglet):
                widget.actualiser()
