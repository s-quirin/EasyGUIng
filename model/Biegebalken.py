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

c, input = {}, {}    # init

# Modellbeschreibung:
# Titel, Beschreibung (in Markdown), Autor/Kontakt, Version
title = 'Biegebalken'
description = """
Berechnung der elastischen Durchbiegung eines Balkens nach der Balkentheorie  
Voraussetzungen (Bernoullische Annahmen):
* schubstarrer, schlanker Balken (Die Länge ist wesentlich größer als die Querschnittsabmessungen)
"""
author = 'Universität des Saarlandes'
version = '0.1'

# Ein- und Ausgabe:
# Eingabewerte mit Name, Minimum, Maximum und physik. Einheit
#   input['x'] = ('name', (min value, …, max value), 'unit')
input['l'] = ('Länge',                  (1, 2, 3), 'm')
input['x'] = ('Position',               (0, 0.5, 1), '')
input['q'] = ('Gleichlast',             (2000, 1500, 1000), 'N/m')
input['E'] = ('Elastizitätsmodul',      (70, 140, 210), 'GPa')
input['I'] = ('Flächenträgheitsmoment', (108), 'cm^4')
input['z'] = ('Halbe Balkendicke',      (3), 'cm')

# Name Ausgabewert(e) (y-Wert)
#   output = ('name', …)
output = ('Durchbiegung', 'Max. Biegespannung')

# Diagramm: Größe auf der x-Achse
plotX = 'x'

# Konstanten
#   c['x'] = (value, 'unit')

# Modellberechnung:
import numpy as np    # init

def calculate(c, var, out):    # init
    if out == output[0]:
        # Durchbiegung
        EI = var['E'] * var['I']    # Biegesteifigkeit
        k = var['q'] * np.power(var['l'], 4) / EI / 24
        return -k * (var['x'] - 2*np.power(var['x'],3) + np.power(var['x'],4))
    else:
        # Maximale Biegespannung (in der Randfaser)
        My = var['q'] / 2 * np.power(var['l'],2) * (var['x'] - np.power(var['x'],2))
        return My / var['I'] * var['z']