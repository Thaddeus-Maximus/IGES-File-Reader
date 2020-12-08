#!/usr/bin/env python
import os
from iges.read import IGES_Object
from iges.curves_surfaces import CircArc, Line, CompCurve

import matplotlib
import matplotlib.pyplot as plt

fig = plt.figure()
ax  = fig.add_subplot(111, projection='3d')
ax.set_aspect('auto')

# Load
with open('tubes_splined.iges', 'r') as f:
    igs = IGES_Object(f)

# Work with the data
for i, entity in enumerate(igs.toplevel_entities):
    #print(i, entity.sequence_number, repr(entity))
    if type(entity) in [CircArc, Line, CompCurve]:
        lsp = entity.linspace(20)
        print(lsp)
        plt.plot(lsp[0,:], lsp[1,:], lsp[2,:], '*')
        
plt.show()