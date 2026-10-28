"""Module de conversion d'unités pour la bibliothèque TEMPO.

Ce module gère les conversions d'unités (notamment les conversions angulaires
radians, degrès, grades) en s'appuyant sur la classe Unite métier lorsqu'elle est disponible
ou sur des facteurs de conversion standards.
"""

import math
from typing import Any, Optional, Tuple, List, Dict
import logging

logger = logging.getLogger(__name__)


class GestionnaireConversions:
    """Gestionnaire de conversion d'unités métier."""

    # Unités angulaires supportées
    RADIAN = "rad"
    DEGRE = "deg"
    GRADE = "gon"  # ou grade

    UNITES_ANGULAIRES = {
        "rad": ["rad", "radian", "radians"],
        "deg": ["deg", "degré", "degres", "degree", "degrees", "°"],
        "gon": ["gon", "grade", "grades"]
    }

    @classmethod
    def normaliser_nom_unite(cls, unite: Any) -> str:
        """Normalise un nom ou objet unité en une chaîne standard."""
        if unite is None:
            return ""

        # Si l'objet possède un attribut 'nom', 'code' ou 'symbole' (classe Unite)
        for attr in ["symbole", "code", "nom", "name"]:
            if hasattr(unite, attr):
                val = getattr(unite, attr)
                if isinstance(val, str) and val.strip():
                    return val.strip().lower()

        nom_str = str(unite).strip().lower()
        return nom_str

    @classmethod
    def est_unite_angulaire(cls, unite: Any) -> bool:
        """Détermine si l'unité est une unité d'angle."""
        nom = cls.normaliser_nom_unite(unite)
        for cat, variantes in cls.UNITES_ANGULAIRES.items():
            if nom in variantes:
                return True
        return False

    @classmethod
    def determiner_type_angle(cls, unite: Any) -> Optional[str]:
        """Retourne le type d'angle ('rad', 'deg', 'gon') ou None."""
        nom = cls.normaliser_nom_unite(unite)
        for cat, variantes in cls.UNITES_ANGULAIRES.items():
            if nom in variantes:
                return cat
        return None

    @classmethod
    def obtenir_facteur_unite_metier(cls, unite_source: Any, unite_cible: Any) -> Optional[float]:
        """Essaie de récupérer un coefficient directement depuis la classe Unite métier si présente.

        À vérifier / valider selon les méthodes réelles de la DLL métier :
        - Unite.obtenir_coefficient(src, dst)
        - Unite.convertir(1.0, src, dst)
        """
        # tentative d'interrogation dynamique
        for obj in [unite_source, unite_cible]:
            if hasattr(obj, "obtenir_coefficient"):
                try:
                    return float(obj.obtenir_coefficient(unite_source, unite_cible))
                except Exception:
                    pass
            if hasattr(obj, "facteur_conversion"):
                try:
                    return float(obj.facteur_conversion)
                except Exception:
                    pass
        return None

    @classmethod
    def convertir_valeur(cls, valeur: float, unite_source: Any, unite_cible: Any) -> float:
        """Convertit une valeur numérique d'une unité source vers une unité cible.

        Ne modifie pas les données si les unités sont identiques ou incompatibles.
        Gère sans planter les erreurs de conversion.
        """
        if valeur is None or math.isnan(valeur) or math.isinf(valeur):
            return valeur

        if unite_source is None or unite_cible is None:
            return valeur

        type_src = cls.determiner_type_angle(unite_source)
        type_dst = cls.determiner_type_angle(unite_cible)

        # Si les deux unités sont angulaires
        if type_src and type_dst:
            if type_src == type_dst:
                return valeur

            # Convertir d'abord vers radians
            val_rad = valeur
            if type_src == "deg":
                val_rad = math.radians(valeur)
            elif type_src == "gon":
                val_rad = valeur * (math.pi / 200.0)

            # Convertir de radians vers destination
            if type_dst == "deg":
                return math.degrees(val_rad)
            elif type_dst == "gon":
                return val_rad * (200.0 / math.pi)
            elif type_dst == "rad":
                return val_rad

        # Essai via coefficients métier
        coeff = cls.obtenir_facteur_unite_metier(unite_source, unite_cible)
        if coeff is not None and coeff != 0:
            return valeur * coeff

        # En l'absence de règle explicite, retourner la valeur originale inchangée
        return valeur

    @classmethod
    def convertir_liste_valeurs(cls, valeurs: List[float], unite_source: Any, unite_cible: Any) -> List[float]:
        """Convertit toute une liste de valeurs de manière sécurisée."""
        if not valeurs or unite_source == unite_cible:
            return valeurs
        return [cls.convertir_valeur(v, unite_source, unite_cible) for v in valeurs]
