#!/usr/bin/env python
# coding: utf-8

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

input, option = {}, {}    # init

# --- Modellbeschreibung ---
# Titel, Beschreibung (in Markdown), Autor/Kontakt, Version
title = 'Lambert-beersches Gesetz'
description = """
Abschätzung der Intensität transmittierter Strahlung bzw. Abschwächung der
Intensität (Extinktion) einer Strahlung in Bezug zu deren Anfangsintensität
bei Durchgang durch
* ein absorbierendes Medium (bouguer-lambertsches Gesetz)
* eine absorbierende Substanz in Abhängigkeit von der Konzentration
(lambert-beersches Gesetz)
"""
author = 'Universität des Saarlandes'
version = '0.1'

# --- Ein- und Ausgabe ---
# Name Ausgabewert(e) (y-Wert)
#   option['output'] = ('name', …)
option['output'] = ('Intensität', 'Abschwächung')

option['Medium'] = ('Allgemein', 'Feststoff', 'Flüssigkeit/Gas')

# Eingabewerte mit Name, Minimum, Maximum und physik. Einheit
#   input['x'] = ('name', (min value, …, max value), 'unit')
input['I_0'] = ('Eingestrahlte Intensität', (500, 1000, 2000), 'W/m^2')
input['d'] = ('Durchstrahlte Schichtdicke', (1, 0.01, 0.001), 'm')
input['µ'] = ('Schwächungskoeffizient', (0.02, 0.1, 20), '1/cm', 'Allgemein')

# Knochen, Acrylglas, Blei
input['µ_ρ'] = ('Massenschwächungskoeffizient', (0.19, 0.16, 5.5), 'cm^2/g', 'Feststoff')
# NIST Data: physics.nist.gov, Photonenenergie 0,1 MeV
input['ρ'] = ('Dichte', (1.16, 1.18, 11.34), 'g/cm^3', 'Feststoff')
# Knochendichte:
# H. Erik Meema & Silvia Meema (1978) Compact Bone Mineral Density of the Normal Human Radius,
# Acta Radiologica: Oncology, Radiation, Physics, Biology, 17:4, 342-352,
# DOI: 10.3109/02841867809127938

# Wasser (blaues Licht), Wasser (rotes Licht), Farbstoff in wässriger Lösung (alle frequenzabhängig)
input['ε_λ'] = ('Dekadischer Extinktionskoeffizient', (2e-3, 0.02, 100), 'l/mol/m', 'Flüssigkeit/Gas')
input['c'] = ('Stoffmengenkonzentration', (55.42, 55.42, 0.02), 'mol/l', 'Flüssigkeit/Gas')

# Diagramm: Größe auf der x-Achse
plotX = 'd'

# --- Modellberechnung ---
import numpy as np    # init

def calculate(Q_, var, opt):    # init
    # Konstanten
    #   c = Q_(value, 'unit')

    # Gleichung bzw. Algorithmus
    if opt['Medium'] == 'Allgemein':
        A = np.exp(-var['µ'] * var['d'])    # I_1/I_0
    elif opt['Medium'] == 'Feststoff':
        A = np.exp(-var['µ_ρ'] * var['ρ'] * var['d'])
    else:
        # Flüssigkeit/Gas
        E = var['ε_λ'] * var['c'] * var['d']    # Extinktion
        A = np.power(10, -E)

    if opt['output'] == 'Intensität':
        return var['I_0'].to('W/m^2') * A
    else:
        return A