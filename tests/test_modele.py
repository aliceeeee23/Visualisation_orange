"""Tests unitaires pour la couche d'adaptation métier et le modèle de données."""

import pytest
import ctypes
from tempo.widgets.graphique.adaptation_metier import AdaptateurMetier
from tempo.widgets.graphique.modele import SerieGraphique, PointGraphique, CollectionSeries


class PointSimule:
    def __init__(self, repere, valeur, validite=1):
        self.repere = repere
        self.valeur = valeur
        self.validite = validite


class MesureSimulee:
    def __init__(self, alias, points):
        self.alias = alias
        self.points = points


class TrajectoireSimulee:
    def __init__(self, mesures):
        self.mesures = mesures


class PointCtypes(ctypes.Structure):
    _fields_ = [("repere", ctypes.c_double), ("valeur", ctypes.c_double), ("validite", ctypes.c_int)]


def test_extraction_point_valide():
    pt = PointSimule(repere=1.5, valeur=25.0, validite=1)
    r, v, valids = AdaptateurMetier.extraire_point(pt)
    assert r == 1.5
    assert v == 25.0
    assert valids == 1


def test_extraction_point_invalide():
    pt = PointSimule(repere=2.0, valeur=-999.0, validite=0)
    r, v, valids = AdaptateurMetier.extraire_point(pt)
    assert r == 2.0
    assert v == -999.0
    assert valids == 0


def test_extraction_point_ctypes():
    pt = PointCtypes(repere=3.0, valeur=10.5, validite=1)
    r, v, valids = AdaptateurMetier.extraire_point(pt)
    assert r == 3.0
    assert v == 10.5
    assert valids == 1


def test_extraction_mesure_vide():
    m = MesureSimulee(alias="Vide", points=[])
    data = AdaptateurMetier.extraire_mesure(m)
    assert data["alias"] == "Vide"
    assert data["points"] == []


def test_extraction_trajectoire_9_mesures():
    mesures = [MesureSimulee(f"M{i}", [PointSimule(0, i, 1)]) for i in range(9)]
    traj = TrajectoireSimulee(mesures)
    extracted = AdaptateurMetier.extraire_trajectoire(traj)
    assert len(extracted) == 9
    assert extracted[0]["alias"] == "M0"
    assert extracted[8]["alias"] == "M8"


def test_collection_series_limite_6():
    col = CollectionSeries()
    for i in range(10):
        s = SerieGraphique(id_serie=f"s{i}", alias=f"Série {i}")
        col.ajouter_ou_mettre_a_jour(s)

    selected = col.obtenir_series_selectionnees()
    assert len(selected) == 6
    assert selected[0].id_serie == "s0"
    assert selected[5].id_serie == "s5"
