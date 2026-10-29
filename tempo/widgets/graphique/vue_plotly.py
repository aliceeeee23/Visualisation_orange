"""Composant graphique Plotly dans un widget QWebEngineView hors-ligne.

Ce module génère le HTML et le JavaScript nécessaire pour effectuer l'affichage
interactif Plotly 100% hors-ligne via la bibliothèque plotly.min.js locale.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

from AnyQt.QtWidgets import QWidget, QVBoxLayout
from AnyQt.QtWebEngineWidgets import QWebEngineView
from AnyQt.QtCore import QUrl, pyqtSignal

from .modele import SerieGraphique, PointGraphique
from .gestionnaire_axes import ConfigurationAxe, GestionnaireAxes
from .conversions import GestionnaireConversions

logger = logging.getLogger(__name__)


class VueGraphiquePlotly(QWidget):
    """Widget de rendu Plotly hébergé dans un QWebEngineView local."""

    signal_points_masques = pyqtSignal(str, list)  # (id_serie, liste_indices)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._web_view = QWebEngineView(self)
        self._layout.addWidget(self._web_view)

        # Chemin absolu vers plotly.min.js local et mise en cache
        dir_courant = os.path.dirname(os.path.abspath(__file__))
        self._chemin_plotly_js = os.path.join(dir_courant, "plotly.min.js")
        self._cache_plotly_js: Optional[str] = None

        self.mode_representation = "Mesure / Repere"  # ou "Mesure / Mesure"
        self.afficher_points_invalides = True
        self.afficher_grille = True
        self.afficher_legende = True
        self.tolerence_alignement = 1e-5

        # Initialiser avec un graphique vide
        self.actualiser_graphique([], ConfigurationAxe(), ConfigurationAxe(), "Graphique TEMPO")

    def _generer_html_interne(
        self,
        data_traces: List[Dict[str, Any]],
        layout_dict: Dict[str, Any],
        titre: str
    ) -> str:
        """Génère la page HTML complète intégrant le fichier JS local et Plotly.newPlot."""

        # Charger la librairie Plotly JS locale depuis le cache
        if self._cache_plotly_js is None:
            if os.path.exists(self._chemin_plotly_js):
                try:
                    with open(self._chemin_plotly_js, "r", encoding="utf-8") as f:
                        self._cache_plotly_js = f.read()
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture de plotly.min.js: {e}")
                    self._cache_plotly_js = ""
            else:
                self._cache_plotly_js = ""

        content_js = self._cache_plotly_js

        json_traces = json.dumps(data_traces)
        json_layout = json.dumps(layout_dict)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{titre}</title>
    <script type="text/javascript">
    {content_js}
    </script>
    <style>
        html, body, #plotly-div {{
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: #ffffff;
        }}
    </style>
</head>
<body>
    <div id="plotly-div"></div>
    <script type="text/javascript">
        var traces = {json_traces};
        var layout = {json_layout};
        var config = {{
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['sendDataToCloud'],
            displaylogo: false
        }};

        Plotly.newPlot('plotly-div', traces, layout, config);

        // Interaction sur la sélection des points
        var plotDiv = document.getElementById('plotly-div');
        plotDiv.on('plotly_selected', function(eventData) {{
            if (eventData && eventData.points) {{
                // Des points ont été sélectionnés
            }}
        }});
    </script>
</body>
</html>
"""
        return html

    def actualiser_graphique(
        self,
        series: List[SerieGraphique],
        config_x: ConfigurationAxe,
        config_y: ConfigurationAxe,
        titre_graphique: str = "Graphique TEMPO"
    ) -> None:
        """Prépare les traces Plotly et met à jour le WebEngineView."""
        traces = []

        if self.mode_representation == "Mesure / Repere":
            for s in series:
                if not s.visible:
                    continue

                pts = s.obtenir_points_filtrés(
                    inclure_invalides=self.afficher_points_invalides,
                    inclure_masques=False
                )

                x_vals = []
                y_vals = []
                hover_texts = []

                for pt in pts:
                    # Application des conversions d'unités d'affichage
                    x_v = GestionnaireConversions.convertir_valeur(
                        pt.repere, s.unite_repere, s.unite_affichage_repere
                    )
                    y_v = GestionnaireConversions.convertir_valeur(
                        pt.valeur, s.unite_mesure, s.unite_affichage_mesure
                    )

                    # Si échelle log, filtrer valeurs non représentables
                    if config_x.type_echelle == "log" and (x_v is None or x_v <= 0):
                        continue
                    if config_y.type_echelle == "log" and (y_v is None or y_v <= 0):
                        continue

                    x_vals.append(x_v)
                    y_vals.append(y_v)

                    statut_str = "Valide" if pt.est_valide else "INVALIDE"
                    text = f"Série: {s.alias}<br>X (Repère): {x_v}<br>Y (Valeur): {y_v}<br>Statut: {statut_str}"
                    hover_texts.append(text)

                mode_plotly = s.style_ligne if s.style_ligne in ["lines", "markers", "lines+markers"] else "lines+markers"

                # Mappage du symbole Plotly (croix centree = 'x')
                symbole = s.symbole_marqueur if s.symbole_marqueur else "x"

                trace = {
                    "type": "scatter",
                    "mode": mode_plotly,
                    "name": s.alias,
                    "x": x_vals,
                    "y": y_vals,
                    "text": hover_texts,
                    "hoverinfo": "text",
                    "marker": {
                        "color": s.couleur,
                        "size": s.taille_marqueur,
                        "symbol": symbole
                    },
                    "line": {
                        "color": s.couleur
                    }
                }
                traces.append(trace)

        elif self.mode_representation == "Mesure / Mesure" and len(series) >= 2:
            s_x = series[0]
            s_y = series[1]

            pts_x = s_x.obtenir_points_filtrés(inclure_invalides=self.afficher_points_invalides)
            pts_y = s_y.obtenir_points_filtrés(inclure_invalides=self.afficher_points_invalides)

            # Alignement par repère proche (selon tolérance)
            dict_y = {pt.repere: pt for pt in pts_y if pt.repere is not None}
            x_vals = []
            y_vals = []
            hover_texts = []

            for pt_x in pts_x:
                if pt_x.repere is None:
                    continue
                # Recherche du point y correspondant
                match_y = None
                if pt_x.repere in dict_y:
                    match_y = dict_y[pt_x.repere]
                else:
                    # Recherche avec tolérance
                    for r_y, p_y in dict_y.items():
                        if abs(r_y - pt_x.repere) <= self.tolerence_alignement:
                            match_y = p_y
                            break

                if match_y is not None:
                    vx = GestionnaireConversions.convertir_valeur(
                        pt_x.valeur, s_x.unite_mesure, s_x.unite_affichage_mesure
                    )
                    vy = GestionnaireConversions.convertir_valeur(
                        match_y.valeur, s_y.unite_mesure, s_y.unite_affichage_mesure
                    )

                    if config_x.type_echelle == "log" and (vx is None or vx <= 0):
                        continue
                    if config_y.type_echelle == "log" and (vy is None or vy <= 0):
                        continue

                    x_vals.append(vx)
                    y_vals.append(vy)

                    statut = "Valide" if (pt_x.est_valide and match_y.est_valide) else "INVALIDE"
                    hover_texts.append(f"X ({s_x.alias}): {vx}<br>Y ({s_y.alias}): {vy}<br>Repère: {pt_x.repere}<br>Statut: {statut}")

            trace = {
                "type": "scatter",
                "mode": s_x.style_ligne,
                "name": f"{s_x.alias} vs {s_y.alias}",
                "x": x_vals,
                "y": y_vals,
                "text": hover_texts,
                "hoverinfo": "text",
                "marker": {
                    "color": s_x.couleur,
                    "size": s_x.taille_marqueur,
                    "symbol": s_x.symbole_marqueur
                },
                "line": {
                    "color": s_x.couleur
                }
            }
            traces.append(trace)

        # Préparation du layout
        layout_dict = {
            "title": titre_graphique,
            "showlegend": self.afficher_legende,
            "autosize": True,
            "margin": {"l": 50, "r": 50, "b": 50, "t": 50}
        }

        # Intégrer les axes
        axes_layout = GestionnaireAxes.preparer_layout_axes_plotly(config_x, config_y)
        axes_layout["xaxis"]["showgrid"] = self.afficher_grille
        axes_layout["yaxis"]["showgrid"] = self.afficher_grille
        layout_dict.update(axes_layout)

        html_content = self._generer_html_interne(traces, layout_dict, titre_graphique)
        self._web_view.setHtml(html_content, QUrl("file:///"))
