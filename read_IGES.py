#!/usr/bin/env python
import os
from iges.read import IGES_Object
from iges.curves_surfaces import CircArc, Line, CompCurve, AssociativityInstance

import matplotlib
import matplotlib.pyplot as plt

fig = plt.figure()
ax  = fig.add_subplot(111, projection='3d')
ax.set_aspect('auto')

# Load
with open('chassis_007_simp.IGS', 'r') as f:
    igs = IGES_Object(f)

# Do whatever you want with the data. Go wild.
# igs.toplevel_entities contains the highest-level topological data.
# e.g., all entities have been 'absorbed' into a parent
# (entities can be accessed as part of CompCurves and AssociativityInstances, if they aren't barren)
# The goal is to provide a uniform interface for all entities, though, so that it doesn't matter.
# 
# This will plot each topology in a unique (ish) color so you can see that entities have been grouped appropriately.
for i, entity in enumerate(igs.toplevel_entities):
    if type(entity) in [CircArc, Line, CompCurve, AssociativityInstance]:
        lsp = entity.linspace(10, endpoint=True)
        plt.plot(lsp[0,:], lsp[1,:], lsp[2,:], '-*')
        
plt.show()