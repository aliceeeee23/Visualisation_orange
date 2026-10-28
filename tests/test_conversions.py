"""Tests unitaires pour les conversions d'unités et la gestion des échelles d'axes."""

import pytest
import math
from tempo.widgets.graphique.conversions import GestionnaireConversions
from tempo.widgets.graphique.gestionnaire_axes import GestionnaireAxes, ConfigurationAxe


def test_conversion_angles():
    # Degrés vers Radians
    val_rad = GestionnaireConversions.convertir_valeur(180.0, "deg", "rad")
    assert pytest.approx(val_rad, 1e-6) == math.pi

    # Radians vers Grades
    val_gon = GestionnaireConversions.convertir_valeur(math.pi, "rad", "gon")
    assert pytest.approx(val_gon, 1e-6) == 200.0

    # Grades vers Degrés
    val_deg = GestionnaireConversions.convertir_valeur(200.0, "gon", "deg")
    assert pytest.approx(val_deg, 1e-6) == 180.0


def test_conversion_valeur_nulle_ou_nan():
    assert math.isnan(GestionnaireConversions.convertir_valeur(float("nan"), "deg", "rad"))
    assert GestionnaireConversions.convertir_valeur(None, "deg", "rad") is None


def test_filtrage_echelle_logarithmique():
    valeurs = [-10.0, -0.5, 0.0, 0.001, 10.0, 100.0, float("nan"), float("inf")]
    valeurs_log = GestionnaireAxes.filtrer_valeurs_pour_echelle_log(valeurs)
    assert valeurs_log == [0.001, 10.0, 100.0]


def test_bornes_automatiques_lin_et_log():
    # Linéaire
    b_min, b_max = GestionnaireAxes.calculer_bornes_automatiques([10, 20, 30], type_echelle="linear")
    assert b_min < 10
    assert b_max > 30

    # Logarithmique avec valeurs négatives présentes
    b_min_log, b_max_log = GestionnaireAxes.calculer_bornes_automatiques([-100, 0, 1, 100], type_echelle="log")
    assert b_min_log == 1
    assert b_max_log == 100
