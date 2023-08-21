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
title = 'Biegebalken'
description = """
Berechnung der elastischen Durchbiegung eines Balkens und der Biegespannung
in der Randfaser des Balkens nach der Bernoulli-Balkentheorie  
Voraussetzungen (Bernoullische Annahmen): schubstarrer, schlanker Balken
* Die Länge ist wesentlich größer als die Querschnittsabmessungen.
* Die Biegeverformungen sind klein im Vergleich zur Länge des Balkens.
* Näherungsweise Schubstarrheit ist gegeben (Material mit hohem Schubmodul).
"""
author = 'Universität des Saarlandes'
version = '0.3'

# --- Ein- und Ausgabe ---
# Name Ausgabewert(e) (y-Wert)
#   option['output'] = ('name', …)
option['output'] = ('−Durchbiegung', 'Max. Biegespannung')

option['Last'] = ('Gleichlast', 'Einzellast', 'Dreieckslast')

# Eingabewerte mit Name, Minimum, Maximum und physik. Einheit
#   input['x'] = ('name', (min value, …, max value), 'unit')
input['l'] = ('Länge',                  (1, 2, 3), 'm')
input['x'] = ('Position',               (0, 0.5, 1), '')
input['q'] = ('Belastung (Max.)',       (2000, 1500, 1000), 'N/m', ('Gleichlast', 'Dreieckslast'))
input['F'] = ('Einzellast',             (2000, 1500, 1000), 'N', 'Einzellast')
input['a'] = ('Position der Last',      (0.25, 0.5, 0.75), '', ('Einzellast', 'Dreieckslast'))
input['I'] = ('Flächenträgheitsmoment', (108), 'cm^4')
input['E'] = ('Elastizitätsmodul',      (70, 140, 210), 'GPa', option['output'][0])
input['z'] = ('Halbe Balkendicke',      (3), 'cm', option['output'][1])

# Diagramm: Größe auf der x-Achse
plotX = 'x'

# --- Modellberechnung ---
import model.f_helper as hp    # helper functions

def calculate(Q_, var, opt):    # init
    # Konstanten
    #   c = Q_(value, 'unit')

    # Gleichung bzw. Algorithmus
    if opt['output'] == '−Durchbiegung':
        EI = var['E'] * var['I']    # Biegesteifigkeit
    else:
        W = var['I'] / var['z']    # Widerstandsmoment (z= Abstand Randfaser zu neutraler Faser)
    
    if opt['Last'] == 'Gleichlast':
        if opt['output'] == '−Durchbiegung':
            k = var['q'] * var['l']**4 / EI / 24
            return -k * (var['x'] - 2*var['x']**3 + var['x']**4)
        else:
            # Maximale Biegespannung (in der Randfaser)
            My = var['q'] / 2 * var['l']**2 * (var['x'] - var['x']**2)
            return My / W
    elif opt['Last'] == 'Einzellast':
        if opt['output'] == '−Durchbiegung':
            k = var['F'] * var['l']**3 * var['a'] * (1-var['a']) / EI / 6
            return -k * hp.piecewise(f1_Einzellast, var, ('a', 'x'))
        else:
            # Maximale Biegespannung (in der Randfaser)
            My = var['F'] * var['l'] * hp.piecewise(f2_Einzellast, var, ('a', 'x'))
            return My / W
    elif opt['Last'] == 'Dreieckslast':
        if opt['output'] == '−Durchbiegung':
            return 1/EI * hp.piecewise(f1_Dreieckslast, var, ('a', 'x'))
        else:
            # Maximale Biegespannung (in der Randfaser)
            My = hp.piecewise(f2_Dreieckslast, var, ('a', 'x'))
            return My / W

def f1_Einzellast(_, a, x):
    if a < x <= 1:
        a = 1 - a
        x = 1 - x
    return (2-a)*x - x**3 /a

def f2_Einzellast(_, a, x):
    if a < x <= 1:
        a = 1 - a
        x = 1 - x
    return (1-a) * x

def f1_Dreieckslast(var, a, x):
    """Durchbiegung w einer Dreieckslast"""
    R = var['q'] * var['l'] / 2    # Resultierende Last
    if a == 1 - a:
        L = R / 2    # Last je Auflager bei a = 1/2
        c1 = (1/192 * R/a - 1/8 * L)    # Randbedingung w(a)=w(b) und w'(a)=0
        if x > a:
            x = 1 - x
    else:
        b = 1 - a    # a + b == 1
        B = R * (2/3 * a + 1/3 * b)    # Auflager B
        A = R - B    # Auflager A

        # Randbedingung w(a)=w(b) und w'(a)=-w'(b) wg. Koordinatensystem
        c1 = -1/2*(A*a**2+B*b**2)*b + 1/12*R*(a**3+b**3)*b - 1/6*(A*a**3-B*b**3) + 1/60*R*(a**4-b**4)
        c1 = c1 / (a + b)
        c3 = -1/2 * (A*a**2 + B*b**2) + 1/12 * R * (a**3 + b**3) - c1

        if x <= a:
            L = A
        else:
            L = B
            c1 = c3
            x = 1 - x
            a = 1 - a    # a + b == 1
    return (1/6 * L * x**3 - 1/60 * R/a * x**5 + c1 * x) * var['l']**3

def f2_Dreieckslast(var, a, x):
    """Biegemoment My einer Dreieckslast"""
    R = var['q'] * var['l'] / 2    # Resultierende Last
    if x <= a:
        L = R * (2/3 - 1/3 * a)    # Auflager A
    else:
        L = R * (1/3 + 1/3 * a)    # Auflager B
        x = 1 - x
        a = 1 - a    # a + b == 1
    return L*x*var['l'] - 1/3 * R/a * x**3 * var['l']