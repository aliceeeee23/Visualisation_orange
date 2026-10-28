"""Couche d'adaptation métier pour la bibliothèque TEMPO.

Ce module permet de lire les objets métier (Mesure, Point, Trajectoire, Attribut, Unite, ctypes)
sans jamais les modifier et en extrayant proprement les informations requises.
"""

from typing import Any, List, Optional, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class AdaptateurMetier:
    """Adaptateur pour extraire les données et métadonnées des objets métier."""

    @staticmethod
    def _obtenir_champ(obj: Any, champs_possibles: List[str], defaut: Any = None) -> Any:
        """Extrait la valeur d'un champ parmi une liste de noms possibles."""
        if obj is None:
            return defaut

        # Recherche dans les attributs d'objet standard
        for champ in champs_possibles:
            if hasattr(obj, champ):
                try:
                    val = getattr(obj, champ)
                    return val() if callable(val) else val
                except Exception:
                    pass

        # Support spécifique pour les structures ctypes (_fields_)
        if hasattr(obj, "_fields_"):
            for field_tuple in getattr(obj, "_fields_"):
                field_name = field_tuple[0]
                if field_name in champs_possibles:
                    try:
                        return getattr(obj, field_name)
                    except Exception:
                        pass

        # Support si l'objet se comporte comme un dictionnaire
        if isinstance(obj, dict):
            for champ in champs_possibles:
                if champ in obj:
                    return obj[champ]

        return defaut

    @classmethod
    def est_point(cls, obj: Any) -> bool:
        """Vérifie si un objet possède les caractéristiques d'un Point métier."""
        if obj is None:
            return False
        valeur = cls._obtenir_champ(obj, ["valeur", "mesure", "y", "val"])
        repere = cls._obtenir_champ(obj, ["repere", "x", "index"])
        return valeur is not None or repere is not None

    @classmethod
    def extraire_point(cls, pt_obj: Any) -> Tuple[Optional[float], Optional[float], int]:
        """Extraire (repere, valeur, validite) d'un objet Point.

        Convention impérative:
        validite == 1: point valide
        validite == 0: point invalide
        """
        repere = cls._obtenir_champ(pt_obj, ["repere", "x", "position", "time", "t"], defaut=None)
        valeur = cls._obtenir_champ(pt_obj, ["valeur", "mesure", "y", "val"], defaut=None)
        validite_raw = cls._obtenir_champ(pt_obj, ["validite", "is_valid", "valid", "statut"], defaut=1)

        # Conversion numérique propre
        try:
            repere = float(repere) if repere is not None else None
        except (ValueError, TypeError):
            repere = None

        try:
            valeur = float(valeur) if valeur is not None else None
        except (ValueError, TypeError):
            valeur = None

        # Respect strict de la convention validite == 1 ou 0
        validite = 1 if bool(validite_raw) and validite_raw != 0 else 0

        return repere, valeur, validite

    @classmethod
    def est_mesure(cls, obj: Any) -> bool:
        """Vérifie si un objet possède les caractéristiques d'une Mesure métier."""
        if obj is None:
            return False
        points = cls._obtenir_champ(obj, ["points", "pts", "donnees", "data"])
        alias = cls._obtenir_champ(obj, ["alias", "nom", "name", "label"])
        return points is not None or alias is not None

    @classmethod
    def extraire_mesure(cls, mesure_obj: Any) -> Dict[str, Any]:
        """Extrait les informations d'un objet Mesure sans le modifier.

        Retourne un dictionnaire contenant:
        - alias: str
        - points: list[tuple(repere, valeur, validite)]
        - unite_repere: Any
        - unite_mesure: Any
        - attributs: dict
        """
        alias = cls._obtenir_champ(mesure_obj, ["alias", "nom", "name", "label"], defaut="Mesure")
        unite_repere = cls._obtenir_champ(mesure_obj, ["unite_repere", "unit_x", "x_unit"])
        unite_mesure = cls._obtenir_champ(mesure_obj, ["unite_mesure", "unit_y", "y_unit", "unite"])
        attributs_raw = cls._obtenir_champ(mesure_obj, ["attributs", "attributes", "metadata"], defaut={})

        pts_raw = cls._obtenir_champ(mesure_obj, ["points", "pts", "donnees", "data"], defaut=[])
        points_extraits = []

        if hasattr(pts_raw, "__iter__"):
            for idx, pt in enumerate(pts_raw):
                if cls.est_point(pt):
                    rep, val, valids = cls.extraire_point(pt)
                    if rep is None:
                        rep = float(idx)
                    points_extraits.append((rep, val, valids))
                elif isinstance(pt, (int, float)):
                    points_extraits.append((float(idx), float(pt), 1))

        return {
            "alias": str(alias),
            "points": points_extraits,
            "unite_repere": unite_repere,
            "unite_mesure": unite_mesure,
            "attributs": attributs_raw if isinstance(attributs_raw, dict) else {},
            "objet_origine": mesure_obj
        }

    @classmethod
    def est_trajectoire(cls, obj: Any) -> bool:
        """Vérifie si un objet correspond à une Trajectoire (contient les 9 mesures)."""
        if obj is None:
            return False
        mesures = cls._obtenir_champ(obj, ["mesures", "trajectoires", "series", "mesure_list"])
        if mesures is not None and len(mesures) >= 9:
            return True
        # Vérification si les 9 grandeurs sont présentées comme attributs
        champs_9 = ["pos_x", "pos_y", "pos_z", "vit_x", "vit_y", "vit_z", "acc_x", "acc_y", "acc_z"]
        return any(hasattr(obj, c) for c in champs_9)

    @classmethod
    def extraire_trajectoire(cls, traj_obj: Any) -> List[Dict[str, Any]]:
        """Extrait jusqu'à 9 mesures individuelles d'une Trajectoire."""
        mesures_extraites = []

        # Cas 1: liste de 9 mesures dans un attribut 'mesures'
        mesures_raw = cls._obtenir_champ(traj_obj, ["mesures", "trajectoires", "series", "mesure_list"])
        if mesures_raw and hasattr(mesures_raw, "__iter__"):
            for m in mesures_raw:
                if cls.est_mesure(m):
                    mesures_extraites.append(cls.extraire_mesure(m))

        # Cas 2: attributs individuels de position, vitesse, accélération
        if not mesures_extraites:
            noms_9 = [
                ("pos_x", "Position X"), ("pos_y", "Position Y"), ("pos_z", "Position Z"),
                ("vit_x", "Vitesse X"), ("vit_y", "Vitesse Y"), ("vit_z", "Vitesse Z"),
                ("acc_x", "Accélération X"), ("acc_y", "Accélération Y"), ("acc_z", "Accélération Z")
            ]
            for attr_name, nom_defaut in noms_9:
                if hasattr(traj_obj, attr_name):
                    m_obj = getattr(traj_obj, attr_name)
                    if cls.est_mesure(m_obj):
                        m_data = cls.extraire_mesure(m_obj)
                        if m_data["alias"] == "Mesure":
                            m_data["alias"] = nom_defaut
                        mesures_extraites.append(m_data)

        return mesures_extraites

    @classmethod
    def normaliser_donnees_entree(cls, donnees: Any) -> List[Dict[str, Any]]:
        """Normalise une entrée Orange 'Données Objet' sous forme d'une liste de dict de mesures."""
        if donnees is None:
            return []

        resultats = []

        if cls.est_trajectoire(donnees):
            resultats.extend(cls.extraire_trajectoire(donnees))
        elif cls.est_mesure(donnees):
            resultats.append(cls.extraire_mesure(donnees))
        elif isinstance(donnees, (list, tuple)):
            for item in donnees:
                if cls.est_trajectoire(item):
                    resultats.extend(cls.extraire_trajectoire(item))
                elif cls.est_mesure(item):
                    resultats.append(cls.extraire_mesure(item))

        return resultats
