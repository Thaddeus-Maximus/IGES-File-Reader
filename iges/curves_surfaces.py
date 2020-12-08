#!/usr/bin/env python
from iges.entity import Entity
import os
import numpy as np
import math
from itertools import combinations

class Line(Entity):
    """Straight line segment (110)"""

    def add_parameters(self, parameters):
        p = [float(param.strip()) for param in parameters]

        self.p1 = np.array(p[1:4]).reshape(3,1)
        self.p2 = np.array(p[4:7]).reshape(3,1)

        self.e1 = None
        self.e2 = None
        self.compute_endpoints()

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

    def reverse(self):
        self.p1, self.p2 = self.p2, self.p1
        self.compute_endpoints()
        return self

    def compute_endpoints(self):
        self.e1 = self.transform(self.p1)
        self.e2 = self.transform(self.p2)
        return self.e1, self.e2

    def linspace(self, n_points, endpoint=True):
        t = np.linspace(0.0, 1.0, n_points, endpoint=endpoint)
        pts = np.outer(self.p1, 1-t) + np.outer(self.p2, t)
        return self.transform(pts)

    def length(self):
        #return math.hypot(self.p1[0]-self.p2[0], self.p1[1]-self.p2[1], self.p1[2]-self.p2[2])
        return np.linalg.norm(self.p1-self.p2, ord=2)

    def arange(self, dx, endpoint=False):
        n = math.ceil(self.length()/dx)
        return self.linspace(n, endpoint)

class CircArc(Entity):
    """
        Circular arc segment (100)
        Often paired with a Transformation Matrix because it's 2D.

        A circular arc determines unique arc endpoints and an arc center point
        (the center of the parentcircle). By considering the arc end points to
        be enumerated and listed in an ordered manner, startpoint first, foll-
        -owed by terminate point, a direction with respect to definition space
        can be associatedwith the arc.

        The ordering of the end points corresponds to the ordering necessary 
        for the arc to betraced out in a counterclockwise direction.
        """    

    def add_parameters(self, parameters):
        # The order isn't a typo.
        # z is displacement on xt,yt plane
        self.z = float(parameters[1])
        # x and y are center coordinates
        self.x = float(parameters[2])
        self.y = float(parameters[3])

        # x1,y1 are start, x2,y2 are end
        self.x1 = float(parameters[4])
        self.y1 = float(parameters[5])
        self.x2 = float(parameters[6])
        self.y2 = float(parameters[7])

        self.reversed = False

        self.e1 = None
        self.e2 = None
        self.compute_endpoints()

    def __repr__(self):
        s = 'CircArc '
        s+= "[{0}, {1} / {2}] / ".format(self.x, self.y, self.z)
        s+= "({0}, {1})--({2}, {3})".format(self.x1, self.y1, self.x2, self.y2)
        s+= "T({0})".format(repr(self.transformation))
        return s

    def radius(self):
        return math.hypot(self.x1-self.x, self.y1-self.y)

    def reverse(self):
        self.x1, self.x2 = self.x2, self.x1
        self.y1, self.y2 = self.y2, self.y1
        self.reversed = True
        self.compute_endpoints()
        return self

    def thetas(self):
        theta1 = math.atan2(self.y1-self.y, self.x1-self.x)
        theta2 = math.atan2(self.y2-self.y, self.x2-self.x)
        # because the arc is traced CCW, theta2 must be > theta1.. unless reversed
        if self.reversed:
            while theta2 > theta1:
                theta2 -= math.pi*2
        else:
            while theta2 < theta1:
                theta2 += math.pi*2
        return (theta1, theta2)

    def compute_endpoints(self):
        self.e1 = self.transform(np.array([self.x1, self.y1, self.z]).reshape(3,1))
        self.e2 = self.transform(np.array([self.x2, self.y2, self.z]).reshape(3,1))
        return self.e1, self.e2

    def length(self):
        thetas = self.thetas()
        return abs(thetas[0]-thetas[1])*self.radius()

    def linspace(self, n_points, endpoint=True):
        thetas = self.thetas()
        theta = np.linspace(thetas[0], thetas[1], n_points, endpoint=endpoint)
        r = self.radius()

        pts = np.vstack((self.x+np.cos(theta)*r, self.y+np.sin(theta)*r, np.full((1, n_points), self.z)))

        return self.transform(pts)

    def arange(self, dx, endpoint=False):
        n = math.ceil(self.length()/dx)
        return self.linspace(n, endpoint)

class CompCurve(Entity):
    """ Composite curve (102) """
    def add_parameters(self, parameters):
        self.n_curves = int(parameters[1].strip())
        self.pointers = []
        for i in range(2, self.n_curves+2):
            self.pointers.append(int(parameters[i].strip()))

    def add_children(self, children, EPSILON = 1e-5):
        """ This algorithm isn't the greatest. It's at least O(n^2) """
        self.children = []
        
        comb = combinations(range(len(children)), 2)
        dists = {}
        for c in list(comb):
            a = c[0]
            b = c[1]
            # check a.e1 to b.e1 and b.e2
            # check a.e2 to b.e1 and b.e2

            for x in [(b,1),(b,2),(a,1),(a,2)]:
                if not x in dists:
                    dists[x] = {}

            dists[(b, 1)][(a, 1)] = dists[(a, 1)][(b, 1)] = np.linalg.norm(children[a].e1-children[b].e1)
            dists[(b, 2)][(a, 1)] = dists[(a, 1)][(b, 2)] = np.linalg.norm(children[a].e1-children[b].e2)
            dists[(b, 1)][(a, 2)] = dists[(a, 2)][(b, 1)] = np.linalg.norm(children[a].e2-children[b].e1)
            dists[(b, 2)][(a, 2)] = dists[(a, 2)][(b, 2)] = np.linalg.norm(children[a].e2-children[b].e2)

        # at this point we know all the distances from every node.

        # pick a point to be the "starter". If we find an open node we'll change this later.
        step = (0,1)
        connections = {}

        for point in dists:            
            bestpt = min(dists[point], key=dists[point].get)
            a = children[point[0]].e1 if point[1]==1 else children[point[0]].e2
            b = children[bestpt[0]].e1 if bestpt[1]==1 else children[bestpt[0]].e2
            if dists[point][bestpt] > 1e-5:
                step = point
                connections[point] = None
            else:
                connections[point] = bestpt

        original = step

        while True:
            if step[1] == 2:
                children[step[0]].reverse()
            self.children.append(children[step[0]])

            step = (step[0], 1 if step[1]==2 else 2)
            step = connections[step]

            if step is None or step[0] is original[0]:
                break

    def __repr__(self):
        s = 'CompCurve ('
        s+=', '.join([repr(child) for child in self.children])
        s+=')'
        return s

    def length(self):
        return sum([child.length() for child in self.children])

    def linspace(self, n_points, endpoint=True):
        return np.hstack([child.linspace(n_points) for child in self.children])

    def arange(self, dx, endpoint=False):
        stack = []
        for i, child in enumerate(self.children):
            if i == len(self.children)-1:
                stack.append(child.arange(dx, endpoint=endpoint))
            else:
                stack.append(child.arange(dx, endpoint=False))
        return np.hstack(stack)

class AssociativityInstance(Entity):
    """
    Associativity Instance Entity (Type 402)
    To be honest, I don't fully grok this, but SW seems to use it rather than composite curves.

    Index Name Type Description
    1 N Integer Number of entries
    2 DE(1) Pointer Pointer to the DE of the first entity
    .. .. . .
    1+N DE(N) Pointer Pointer to the DE of the last entity

    """

    def add_parameters(self, parameters):
        if self.d['form_number'] == 15: # Ordered Group, no Back Pointers Associativity
            self.n_curves = int(parameters[1].strip())
            self.pointers = []
            for i in range(2, self.n_curves+2):
                self.pointers.append(int(parameters[i].strip()))

    def add_children(self, children, EPSILON = 1e-5):
        """ This algorithm isn't the greatest. It's at least O(n^2) """
        self.children = []
        
        comb = combinations(range(len(children)), 2)
        dists = {}
        for c in list(comb):
            a = c[0]
            b = c[1]
            # check a.e1 to b.e1 and b.e2
            # check a.e2 to b.e1 and b.e2

            for x in [(b,1),(b,2),(a,1),(a,2)]:
                if not x in dists:
                    dists[x] = {}

            dists[(b, 1)][(a, 1)] = dists[(a, 1)][(b, 1)] = np.linalg.norm(children[a].e1-children[b].e1)
            dists[(b, 2)][(a, 1)] = dists[(a, 1)][(b, 2)] = np.linalg.norm(children[a].e1-children[b].e2)
            dists[(b, 1)][(a, 2)] = dists[(a, 2)][(b, 1)] = np.linalg.norm(children[a].e2-children[b].e1)
            dists[(b, 2)][(a, 2)] = dists[(a, 2)][(b, 2)] = np.linalg.norm(children[a].e2-children[b].e2)

        # at this point we know all the distances from every node.

        # pick a point to be the "starter". If we find an open node we'll change this later.
        step = (0,1)
        connections = {}

        for point in dists:
            bestpt = min(dists[point], key=dists[point].get)
            a = children[point[0]].e1 if point[1]==1 else children[point[0]].e2
            b = children[bestpt[0]].e1 if bestpt[1]==1 else children[bestpt[0]].e2
            if dists[point][bestpt] > 1e-5:
                step = point
                connections[point] = None
            else:
                connections[point] = bestpt

        original = step

        while True:
            if step[1] == 2:
                children[step[0]].reverse()
            self.children.append(children[step[0]])

            step = (step[0], 1 if step[1]==2 else 2)
            step = connections[step]

            if step is None or step[0] is original[0]:
                break

    def __repr__(self):
        s = 'CompCurve ('
        s+=', '.join([repr(child) for child in self.children])
        s+=')'
        return s

    def length(self):
        return sum([child.length() for child in self.children])

    def linspace(self, n_points, endpoint=True):
        return np.hstack([child.linspace(n_points) for child in self.children])

    def arange(self, dx, endpoint=False):
        stack = []
        for i, child in enumerate(self.children):
            if i == len(self.children)-1:
                stack.append(child.arange(dx, endpoint=endpoint))
            else:
                stack.append(child.arange(dx, endpoint=False))
        return np.hstack(stack)

class ColorDefinition(Entity):
    """
    Color Definition Entity Type (Type 314)
    """

    pass

class TransformationMatrix(Entity):
    """Transformation Matrix (124)"""

    def add_parameters(self, parameters):
        p = [float(param.strip()) for param in parameters]
        self.R = np.array([[p[1], p[2], p[3]], [p[5], p[6], p[7]], [p[9], p[10], p[11]]])
        self.T = np.array([p[4], p[8], p[12]]).reshape(3,1)
        # E_T = R*E + T

    def transform(self, pt):
        out = np.matmul(self.R, pt) + np.broadcast_to(self.T, pt.shape)
        return out

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

