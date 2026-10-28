"""Modèle de données interne pour les séries de visualisation TEMPO.

Ce module définit la représentation des points, des séries et des collections
de séries utilisées pour le rendu graphique et l'export.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict


@dataclass
class PointGraphique:
    """Représentation interne d'un point de donnée pour la visualisation."""
    repere: float
    valeur: float
    validite: int = 1  # 1 = valide, 0 = invalide
    masque_visuel: bool = False  # True = masqué temporairement par l'utilisateur

    @property
    def est_valide(self) -> bool:
        """Retourne True si le point est métier-valide (validite == 1)."""
        return self.validite == 1


@dataclass
class SerieGraphique:
    """Représentation interne d'une série de mesure pour la visualisation."""
    id_serie: str
    alias: str
    points: List[PointGraphique] = field(default_factory=list)
    unite_repere: Optional[Any] = None
    unite_mesure: Optional[Any] = None
    unite_affichage_repere: Optional[str] = None
    unite_affichage_mesure: Optional[str] = None
    couleur: str = "#1f77b4"
    style_ligne: str = "lines+markers"  # "lines", "markers", "lines+markers"
    symbole_marqueur: str = "x"  # croix centrée par défaut
    taille_marqueur: int = 8
    visible: bool = True
    objet_metier_origine: Optional[Any] = None

    def obtenir_points_filtrés(self, inclure_invalides: bool = True, inclure_masques: bool = False) -> List[PointGraphique]:
        """Retourne les points en fonction des filtres de validité et de masquage temporaire."""
        pts = []
        for pt in self.points:
            if not inclure_invalides and not pt.est_valide:
                continue
            if not inclure_masques and pt.masque_visuel:
                continue
            pts.append(pt)
        return pts

    def masquer_selection(self, indices: List[int]) -> None:
        """Masque temporairement les points aux indices spécifiés."""
        for idx in indices:
            if 0 <= idx < len(self.points):
                self.points[idx].masque_visuel = True

    def restaurer_tous_masques(self) -> None:
        """Restaure tous les points masqués de la série."""
        for pt in self.points:
            pt.masque_visuel = False


class CollectionSeries:
    """Gestionnaire d'une collection de séries reçues depuis l'entrée Orange."""

    MAX_SERIES_ACTIVES = 6

    def __init__(self) -> None:
        self.series: Dict[str, SerieGraphique] = {}
        self.ordre_series: List[str] = []

    def ajouter_ou_mettre_a_jour(self, serie: SerieGraphique) -> None:
        """Ajoute ou met à jour une série dans la collection."""
        if serie.id_serie not in self.series:
            self.ordre_series.append(serie.id_serie)
        self.series[serie.id_serie] = serie

    def reinitialiser(self) -> None:
        """Vide la collection de séries."""
        self.series.clear()
        self.ordre_series.clear()

    def obtenir_series_selectionnees(self, liste_ids: Optional[List[str]] = None) -> List[SerieGraphique]:
        """Retourne la liste des séries sélectionnées (limitée à MAX_SERIES_ACTIVES = 6)."""
        if not liste_ids:
            ids = self.ordre_series[:self.MAX_SERIES_ACTIVES]
        else:
            ids = [i for i in liste_ids if i in self.series][:self.MAX_SERIES_ACTIVES]
        return [self.series[i] for i in ids]
