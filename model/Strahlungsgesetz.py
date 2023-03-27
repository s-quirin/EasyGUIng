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
title = 'Plancksches Strahlungsgesetz'
description = 'Berechnung der spektralen Strahldichte'
author = 'Universität des Saarlandes'
version = '0.1'

# --- Ein- und Ausgabe ---
# Name Ausgabewert(e) (y-Wert)
#   option['output'] = ('name', …)
option['output'] = ('Spektrale Strahldichte')

# Eingabewerte mit Name, Minimum, Maximum und physik. Einheit
#   input['x'] = ('name', (min value, …, max value), 'unit')
input['lambda'] = ('Wellenlänge', (1, 7.5, 14), 'µm')
input['T'] = ('Temperatur', (250, 325, 400), 'K')

# Diagramm: Größe auf der x-Achse
plotX = 'lambda'

# --- Modellberechnung ---
import numpy as np    # init

def calculate(Q_, var, opt):    # init
    # Konstanten
    #   c = Q_(value, 'unit')
    c1L = Q_(1.191e-16, 'W*m^2/sr')
    c2  = Q_(0.014388, 'm*K')

    # Gleichung bzw. Algorithmus
    return c1L / np.power(var['lambda'], 5) / np.expm1(c2/var['lambda']/var['T'])