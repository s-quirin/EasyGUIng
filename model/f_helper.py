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

import numpy as np

def piecewise(function, var, keys):
    """Iteriere 'function' über abschnittsweise definierte Variablen namens 'keys'"""
    import itertools
    ndvars = [np.atleast_1d(var[k_]) for k_ in keys]    # make iterable objects
    length = max(len(n_) for n_ in ndvars)    # max. number of values
    ndvars = [np.resize(n_, length) for n_ in ndvars]    # fill up small array with repeated copies
    array = np.array([])
    for v_ in itertools.zip_longest(*ndvars):
        array = np.append(array, function(var, *v_))
    return array