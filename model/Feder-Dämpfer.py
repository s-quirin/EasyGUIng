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
title = 'Feder-Dämpfersystem'
description = """
Berechnung der freien Schwingung eines Masse-Feder-Dämpfersystem  
Mögliche Fälle:
* Schwingfall (Abklingkonstante < ungedämpfte Kreisfrequenz)
* Aperiodischer Grenzfall (Abklingkonstante = ungedämpfte Kreisfrequenz)
* Kriechfall (Abklingkonstante > ungedämpfte Kreisfrequenz)
"""
author = 'Universität des Saarlandes'
version = '0.1'

# --- Ein- und Ausgabe ---
# Name Ausgabewert(e) (y-Wert)
#   option['output'] = ('name', …)
option['output'] = ('Auslenkung')

option['Feder-Dämpfer'] = ('Relative Größen', 'Absolute Größen')

# Eingabewerte mit Name, Minimum, Maximum und physik. Einheit
#   input['x'] = ('name', (min value, …, max value), 'unit')
input['t'] = ('Zeit', (0, 10), 's')
input['w0'] = ('Ungedämpfte Kreisfrequenz', (0.6, 0.9, 1.1, 0.9), '1/s', 'Relative Größen')    # omega_0
input['D'] = ('Abklingkonstante', (0, 0.4, 1.1, 1.5), '1/s', 'Relative Größen')    # delta

input['k'] = ('Federkonstante', (0, 1.0, 10, 100), 'N/m', 'Absolute Größen')
input['d'] = ('Dämpfungskonstante', (0.9, 0.4, 1.0, 1.5), 'kg/s', 'Absolute Größen')
input['m'] = ('Masse', (0.4, 0.7, 1.0, 1.3), 'kg', 'Absolute Größen')

input['x0'] = ('Initiale Auslenkung', (0.5, 1, 1, 0), 'cm')
input['v0'] = ('Initiale Geschwindigkeit', (0, 1, 1, 2), 'cm/s')

# Diagramm: Größe auf der x-Achse
plotX = 't'

# --- Modellberechnung ---
import numpy as np    # init
import model.f_helper as hp    # helper functions

def calculate(Q_, var, opt):    # init
    # Konstanten
    #   c = Q_(value, 'unit')

    # Gleichung bzw. Algorithmus
    if opt['Feder-Dämpfer'] == 'Absolute Größen':
        var['w0'] = np.sqrt(var['k'] / var['m'])
        var['D'] = var['d'] / var['m'] / 2
    # Abschnittsweise definierte Variablen sind einzeln zu iterieren (piecewise)
    return hp.piecewise(pieces, var, ('D', 'w0'))

def pieces(var, D, w0):
    if D < w0:
        # Schwingfall
        wd = np.sqrt(np.square(w0) - np.square(D))
        tmp = var['v0'] + D * var['x0']
        tmp *= 1.0/wd * np.sin(wd * var['t'])
        tmp += var['x0'] * np.cos(wd * var['t'])
    elif D == w0:
        # Aperiodischer Grenzfall
        tmp = var['v0'] + D * var['x0']
        tmp = var['x0'] + tmp * var['t']
    else:
        # Kriechfall
        alpha = np.sqrt(np.square(D) - np.square(w0))
        c1 = (var['v0'] + var['x0']*alpha + var['x0']*D) / (2*alpha)
        c2 = var['x0'] - c1
        tmp = c1 * np.exp(alpha*var['t']) + c2 * np.exp(-alpha*var['t'])
    return np.exp(-D*var['t']) * tmp
