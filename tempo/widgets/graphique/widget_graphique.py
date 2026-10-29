"""Widget Orange Data Mining TEMPO Visualisation v4.

Déclaration du widget Orange principal avec l'entrée "Données Objet",
l'affichage automatique, la gestion des onglets, l'aide et l'exportation.
"""

import os
import logging
from typing import Any, Optional

from AnyQt.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout, QWidget
from AnyQt.QtCore import Qt

from Orange.widgets.widget import OWWidget, Input, Msg
from Orange.widgets import settings

from .adaptation_metier import AdaptateurMetier
from .gestionnaire_graphiques import GestionnaireGraphiques, GraphiqueOnglet
from .exportation import GestionnaireExport

logger = logging.getLogger(__name__)


class FenetreAideIntegrée(QDialog):
    """Fenêtre d'affichage de la documentation d'aide intégrée (Markdown/Texte)."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Aide - TEMPO Visualisation v4")
        self.setMinimumSize(550, 450)

        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        # Charger le fichier aide.md
        dir_courant = os.path.dirname(os.path.abspath(__file__))
        chemin_aide = os.path.join(dir_courant, "aide.md")
        if os.path.exists(chemin_aide):
            try:
                with open(chemin_aide, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text_edit.setMarkdown(content)
            except Exception:
                self.text_edit.setPlainText("Documentation d'aide non disponible.")
        else:
            self.text_edit.setPlainText("Fichier aide.md non trouvé.")

        btn_fermer = QPushButton("Fermer", self)
        btn_fermer.clicked.connect(self.accept)
        layout.addWidget(btn_fermer, alignment=Qt.AlignmentFlag.AlignRight)


class OWVisualisationV4(OWWidget):
    """Widget Orange TEMPO Visualisation v4."""

    # Informations d'identification du widget dans Orange
    name = "Visualisation v4"
    description = "Visualisation scientifique interactive TEMPO v4 avec Plotly"
    icon = "icon.png"
    priority = 10
    category = "Visualisation"
    keywords = ["tempo", "visualisation", "plotly", "mesure", "trajectoire"]

    want_main_area = True
    resizing_enabled = True

    # Déclaration explicite de l'entrée Orange exigée
    class Inputs:
        donnees_objet = Input("Données Objet", Any, auto_summary=False)

    # Messages d'information / avertissement pour l'utilisateur
    class Information(OWWidget.Information):
        donnees_recues = Msg("Données reçues: {} mesure(s) extraite(s).")

    class Warning(OWWidget.Warning):
        limite_series = Msg("Plus de 6 séries reçues. Seules les 6 premières sont affichées.")
        aucune_mesure = Msg("Aucune mesure exploitable n'a été trouvée dans l'objet transmis.")

    class Error(OWWidget.Error):
        erreur_donnees = Msg("Erreur lors du traitement des données entrantes: {}")

    def __init__(self) -> None:
        super().__init__()

        self.donnees_entree: Any = None

        # Zone principale occupant le maximum d'espace
        layout_principal = QVBoxLayout(self.mainArea)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        self.gestionnaire_graphiques = GestionnaireGraphiques(self.mainArea)
        layout_principal.addWidget(self.gestionnaire_graphiques)

        # Connecter l'export et l'aide depuis le gestionnaire
        self.gestionnaire_graphiques.signal_ouvrir_export.connect(self._exporter_graphique)
        self.gestionnaire_graphiques.signal_ouvrir_aide.connect(self._ouvrir_aide)

        self.fenetre_aide: Optional[FenetreAideIntegrée] = None

    @Inputs.donnees_objet
    def definir_donnees_objet(self, donnees: Any) -> None:
        """Méthode appelée automatiquement lors de la réception de données sur l'entrée 'Données Objet'."""
        self.clear_messages()
        self.donnees_entree = donnees

        if donnees is None:
            self.gestionnaire_graphiques.mettre_a_jour_donnees([])
            return

        try:
            mesures_normalisees = AdaptateurMetier.normaliser_donnees_entree(donnees)

            if not mesures_normalisees:
                self.Warning.aucune_mesure()
                self.gestionnaire_graphiques.mettre_a_jour_donnees([])
                return

            num_mesures = len(mesures_normalisees)
            self.Information.donnees_recues(num_mesures)

            if num_mesures > 6:
                self.Warning.limite_series()

            # Mettre à jour et afficher automatiquement
            self.gestionnaire_graphiques.mettre_a_jour_donnees(mesures_normalisees)

        except Exception as e:
            logger.error(f"Erreur traitement entree OWVisualisationV4: {e}")
            self.Error.erreur_donnees(str(e))

    def _exporter_graphique(self, onglet: GraphiqueOnglet) -> None:
        """Déclenche l'export du graphique de l'onglet actif."""
        GestionnaireExport.exporter_graphique(
            self, onglet.vue, titre_defaut=onglet.titre_graphique
        )

    def _ouvrir_aide(self) -> None:
        """Ouvre la fenêtre d'aide intégrée."""
        if not self.fenetre_aide:
            self.fenetre_aide = FenetreAideIntegrée(self)
        self.fenetre_aide.show()
        self.fenetre_aide.raise_()
