#!/usr/bin/env python
from .entity import Entity
import os
import numpy as np

class Line(Entity):
    """Straight line segment (110)"""

    def add_parameters(self, parameters):
        self.p1 = np.array(parameters[1:4])
        self.p2 = np.array(parameters[4:7])

    def __str__(self):
        s = '--- Line ---' + os.linesep
        s += Entity.__str__(self) + os.linesep
        s += "From point {0}, {1}, {2} {3}".format(self.p1[0], self.p1[1], self.p1[2], os.linesep)
        s += "To point {0}, {1}, {2}".format(self.p2[0], self.p2[1], self.p2[2])
        return s

    def __repr__(self):
        s = 'Line'
        s += " ({0}, {1}, {2}) -- ".format(self.p1[0], self.p1[1], self.p1[2])
        s += "({0}, {1}, {2})".format(self.p2[0], self.p2[1], self.p2[2])
        return s

class CircArc(Entity):
    """Circular arc segment (100).. often paired with a Transformation Matrix because it's 2D."""    

    def add_parameters(self, parameters):
        # The order isn't a typo. z is displacement on xt,yt plane
        self.z = float(parameters[1])
        self.x = float(parameters[2])
        self.y = float(parameters[3])

        self.x1 = float(parameters[4])
        self.y1 = float(parameters[5])
        self.x2 = float(parameters[6])
        self.y2 = float(parameters[7])

    def __repr__(self):
        s = 'CircArc '
        s+= "[{0}, {1} / {2}] / ".format(self.x, self.y, self.z)
        s+= "({0}, {1})--({2}, {3})".format(self.x1, self.y1, self.x2, self.y2)
        s+= "T({0})".format(repr(self.transform))
        return s

class TransformationMatrix(Entity):
    """Transformation Matrix (124)"""

    def add_parameters(self, p):
        self.R = np.array([[p[1], p[2], p[3]], [p[5], p[6], p[7]], [p[9], p[10], p[11]]])
        self.T = np.array([p[4], p[8], p[12]])
        # E_T = R*E + T

    def __repr__(self):
        s = 'TransformationMatrix '
        s += 'R = ' + repr(self.R)
        s += 'T = ' + repr(self.T)
        return s

class RationalBSplineCurve(Entity):
    """Rational B-Spline Curve
    IGES Spec v5.3 p. 123 Section 4.23
    See also Appendix B, p. 545
    """

    def add_parameters(self, parameters):
        self.K = int(parameters[1])
        self.M = int(parameters[2])
        self.prop1 = int(parameters[3])
        self.prop2 = int(parameters[4])
        self.prop3 = int(parameters[5])
        self.prop4 = int(parameters[6])
        
        self.N = 1 + self.K - self.M
        self.A = self.N + 2 * self.M

        # Knot sequence
        self.T = []
        for i in range(7, 7 + self.A + 1):
            self.T.append(float(parameters[i]))

        # Weights
        self.W = []
        for i in range(self.A + 8, self.A + self.K + 8):
            self.W.append(float(parameters[i]))

        # Control points
        self.control_points = []
        for i in range(9 + self.A + self.K, 9 + self.A + 4*self.K + 1, 3):
            point = (float(parameters[i]), float(parameters[i+1]), float(parameters[i+2]))
            self.control_points.append(point)

        # Parameter values
        self.V0 = float(parameters[12 + self.A + 4 * self.K])
        self.V1 = float(parameters[13 + self.A + 4 * self.K])

        # Unit normal (only for planar curves)
        if len(parameters) > 14 + self.A + 4 * self.K + 1:
            self.planar_curve = True
            self.XNORM = float(parameters[14 + self.A + 4 * self.K])
            self.YNORM = float(parameters[15 + self.A + 4 * self.K])
            self.ZNORM = float(parameters[16 + self.A + 4 * self.K])
        else:
            self.planar_curve = False

    def __str__(self):
        s = '--- Rational B-Spline Curve ---' + os.linesep
        s += Entity.__str__(self) + os.linesep
        s += str(self.T) + os.linesep
        s += str(self.W) + os.linesep
        s += str(self.control_points) + os.linesep
        s += "Parameter: v(0) = {0}    v(1) = {1}".format(self.V0, self.V1) + os.linesep
        if self.planar_curve:
            s += "Unit normal: {0} {1} {2}".format(self.XNORM, self.YNORM, self.ZNORM)
        return s

