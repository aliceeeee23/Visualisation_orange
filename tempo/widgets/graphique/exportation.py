"""Module d'exportation de graphiques en images PNG et PDF.

Ce module permet d'exporter le graphique actif sous forme d'image raster (PNG)
ou vectorielle / document PDF sans aucune dépendance réseau.
"""

import os
import logging
from typing import Optional
from AnyQt.QtWidgets import QFileDialog, QMessageBox, QWidget

logger = logging.getLogger(__name__)


class GestionnaireExport:
    """Exportation des graphiques Plotly / QWebEngineView en PNG ou PDF."""

    @classmethod
    def exporter_graphique(cls, parent: QWidget, vue_plotly_widget: QWidget, titre_defaut: str = "graphique_tempo") -> None:
        """Ouvre un dialogue de sélection de fichier et enregistre la vue en PNG ou PDF."""
        filtre = "Image PNG (*.png);;Fichier PDF (*.pdf)"
        chemin, filtre_choisi = QFileDialog.getSaveFileName(
            parent, "Exporter le graphique", f"{titre_defaut}.png", filtre
        )

        if not chemin:
            return

        try:
            web_view = getattr(vue_plotly_widget, "_web_view", None)
            if not web_view:
                QMessageBox.warning(parent, "Export impossible", "Composant WebEngine non disponible pour l'export.")
                return

            if chemin.lower().endswith(".pdf") or "PDF" in filtre_choisi:
                # Exportation PDF via QWebEnginePage.printToPdf
                web_view.page().printToPdf(chemin)
                QMessageBox.information(parent, "Export Réussi", f"Le graphique a été exporté en PDF :\n{chemin}")

            else:
                # Exportation PNG via grattage d'écran / grab du widget Qt
                pixmap = web_view.grab()
                pixmap.save(chemin, "PNG")
                QMessageBox.information(parent, "Export Réussi", f"Le graphique a été exporté en PNG :\n{chemin}")

        except Exception as e:
            logger.error(f"Erreur lors de l'export du graphique : {e}")
            QMessageBox.critical(parent, "Erreur d'export", f"Impossible d'exporter le graphique :\n{e}")
