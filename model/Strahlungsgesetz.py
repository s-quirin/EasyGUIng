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
description = """
Berechnung der spektralen Strahldichte L_λ und Berechnung der Strahldichte L
in Form des Integrals über L_λ
"""
author = 'Universität des Saarlandes'
version = '0.2'

# --- Ein- und Ausgabe ---
# Name Ausgabewert(e) (y-Wert)
#   option['output'] = ('name', …)
option['output'] = ('Spektrale Strahldichte', 'Strahldichte')

# Eingabewerte mit Name, Minimum, Maximum und physik. Einheit
#   input['x'] = ('name', (min value, …, max value), 'unit')
input['λ'] = ('Wellenlänge', (1, 7.5, 14), 'µm', 'Spektrale Strahldichte')
input['F_0'] = ('Integration Start', (1, 3, 8), 'µm', 'Strahldichte')
input['F_1'] = ('Integration Ende', (3, 5, 14), 'µm', 'Strahldichte')
input['T'] = ('Temperatur', (250, 325, 400), 'K')

# Diagramm: Größe auf der x-Achse
plotX = 'λ'

# --- Modellberechnung ---
import numpy as np    # init
import model.f_helper as hp    # helper functions

def calculate(Q_, var, opt):    # init

    def Plancks_Law(var):
        # Konstanten
        #   c = Q_(value, 'unit')
        # Planck-Konstanten (Festlegung nach CODATA 2018)
        c1L = Q_(2 * 6.62607015e-34 * 299792458**2, 'W*m^2/sr')    # c1L = 2*h*c^2
        c2  = Q_(6.62607015e-34 * 299792458 / 1.380649e-23, 'm*K')    # c2 = h*c/k
        return c1L / var['λ']**5 / np.expm1(c2/var['λ']/var['T'])

    # Gleichung bzw. Algorithmus
    if opt['output'] == 'Spektrale Strahldichte':
        return Plancks_Law(var)
    else:
        return hp.integrate(Plancks_Law, var, {'λ':'m', 'T':'K'})