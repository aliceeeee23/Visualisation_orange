"""Gestionnaire d'axes, d'échelles et de graduations pour TEMPO.

Ce module gère la configuration des axes X et Y (échelles linéaire et logarithmique,
limites manuelles ou automatiques, pas de graduation, repères temporels/orthonormés).
Il garantit qu'une échelle logarithmique ne provoque aucun crash en présence
de valeurs nulles, négatives ou non finies.
"""

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Any, Dict


@dataclass
class ConfigurationAxe:
    """Configuration paramétrable pour un axe de graphique (X ou Y)."""
    titre: str = ""
    type_echelle: str = "linear"  # "linear" ou "log"
    mode_automatique: bool = True
    valeur_min: Optional[float] = None
    valeur_max: Optional[float] = None
    pas_graduation: Optional[float] = None
    visible: bool = True
    est_temporel: bool = False
    est_orthonorme: bool = False

    def fixer_limites_manuelles(self, v_min: float, v_max: float) -> None:
        """Définit des limites manuelles explicites."""
        if v_min < v_max:
            self.valeur_min = v_min
            self.valeur_max = v_max
            self.mode_automatique = False

    def reinitialiser_automatique(self) -> None:
        """Repasse l'axe en mode limites automatiques."""
        self.mode_automatique = True
        self.valeur_min = None
        self.valeur_max = None


class GestionnaireAxes:
    """Calculs et ajustements des bornes, graduations et échelles pour les graphiques."""

    @staticmethod
    def filtrer_valeurs_pour_echelle_log(valeurs: List[float]) -> List[float]:
        """Filtre les valeurs <= 0 ou non finies pour éviter tout crash en échelle logarithmique."""
        return [v for v in valeurs if v is not None and math.isfinite(v) and v > 0]

    @classmethod
    def calculer_bornes_automatiques(cls, valeurs: List[float], type_echelle: str = "linear") -> Tuple[Optional[float], Optional[float]]:
        """Calcule les bornes min/max automatiques adaptées aux données."""
        if not valeurs:
            return None, None

        if type_echelle == "log":
            valeurs_valides = cls.filtrer_valeurs_pour_echelle_log(valeurs)
            if not valeurs_valides:
                return 0.1, 10.0  # Plage par défaut sécurisée
            v_min = min(valeurs_valides)
            v_max = max(valeurs_valides)
            if v_min == v_max:
                v_min = v_min * 0.1
                v_max = v_max * 10.0
            return v_min, v_max
        else:
            valeurs_valides = [v for v in valeurs if v is not None and math.isfinite(v)]
            if not valeurs_valides:
                return 0.0, 1.0
            v_min = min(valeurs_valides)
            v_max = max(valeurs_valides)
            if v_min == v_max:
                delta = abs(v_min) * 0.1 if v_min != 0 else 1.0
                v_min -= delta
                v_max += delta
            else:
                marge = (v_max - v_min) * 0.05
                v_min -= marge
                v_max += marge
            return v_min, v_max

    @classmethod
    def preparer_layout_axes_plotly(cls, config_x: ConfigurationAxe, config_y: ConfigurationAxe) -> Dict[str, Any]:
        """Génère la structure de configuration du dictionnaire xaxis et yaxis pour Plotly."""
        layout_xaxis: Dict[str, Any] = {
            "title": config_x.titre,
            "visible": config_x.visible,
            "type": config_x.type_echelle if config_x.type_echelle in ["linear", "log"] else "linear"
        }

        if not config_x.mode_automatique and config_x.valeur_min is not None and config_x.valeur_max is not None:
            if config_x.type_echelle == "log":
                v_min = max(1e-9, config_x.valeur_min)
                v_max = max(v_min * 10, config_x.valeur_max)
                layout_xaxis["range"] = [math.log10(v_min), math.log10(v_max)]
            else:
                layout_xaxis["range"] = [config_x.valeur_min, config_x.valeur_max]

        if config_x.pas_graduation and config_x.pas_graduation > 0 and config_x.type_echelle == "linear":
            layout_xaxis["dtick"] = config_x.pas_graduation

        layout_yaxis: Dict[str, Any] = {
            "title": config_y.titre,
            "visible": config_y.visible,
            "type": config_y.type_echelle if config_y.type_echelle in ["linear", "log"] else "linear"
        }

        if not config_y.mode_automatique and config_y.valeur_min is not None and config_y.valeur_max is not None:
            if config_y.type_echelle == "log":
                v_min = max(1e-9, config_y.valeur_min)
                v_max = max(v_min * 10, config_y.valeur_max)
                layout_yaxis["range"] = [math.log10(v_min), math.log10(v_max)]
            else:
                layout_yaxis["range"] = [config_y.valeur_min, config_y.valeur_max]

        if config_y.pas_graduation and config_y.pas_graduation > 0 and config_y.type_echelle == "linear":
            layout_yaxis["dtick"] = config_y.pas_graduation

        # Si repère orthonormé requis
        if config_x.est_orthonorme or config_y.est_orthonorme:
            layout_yaxis["scaleanchor"] = "x"
            layout_yaxis["scaleratio"] = 1.0

        return {"xaxis": layout_xaxis, "yaxis": layout_yaxis}
