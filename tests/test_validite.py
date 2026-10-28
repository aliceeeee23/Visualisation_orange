"""Tests unitaires pour la gestion de la validité et des filtres de masque."""

import pytest
from tempo.widgets.graphique.modele import PointGraphique, SerieGraphique


def test_point_validite_convention():
    p_valide = PointGraphique(repere=0.0, valeur=10.0, validite=1)
    p_invalide = PointGraphique(repere=1.0, valeur=20.0, validite=0)

    assert p_valide.est_valide is True
    assert p_invalide.est_valide is False


def test_filtrage_invalides_serie():
    pts = [
        PointGraphique(0, 10, validite=1),
        PointGraphique(1, -99, validite=0),
        PointGraphique(2, 20, validite=1)
    ]
    serie = SerieGraphique(id_serie="s1", alias="Test", points=pts)

    # Avec invalides
    pts_tous = serie.obtenir_points_filtrés(inclure_invalides=True)
    assert len(pts_tous) == 3

    # Sans invalides
    pts_valides = serie.obtenir_points_filtrés(inclure_invalides=False)
    assert len(pts_valides) == 2
    assert pts_valides[0].repere == 0
    assert pts_valides[1].repere == 2


def test_masquage_et_restauration_selection():
    pts = [
        PointGraphique(0, 10),
        PointGraphique(1, 20),
        PointGraphique(2, 30)
    ]
    serie = SerieGraphique(id_serie="s1", alias="Test", points=pts)

    # Masquer le second point (index 1)
    serie.masquer_selection([1])
    assert serie.points[1].masque_visuel is True

    # Le filtre exclut les masqués
    pts_visibles = serie.obtenir_points_filtrés(inclure_masques=False)
    assert len(pts_visibles) == 2

    # Restauration
    serie.restaurer_tous_masques()
    assert serie.points[1].masque_visuel is False
    assert len(serie.obtenir_points_filtrés(inclure_masques=False)) == 3
