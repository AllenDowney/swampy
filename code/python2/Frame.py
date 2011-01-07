import sys
from numarray import *
from math import *

def println(s):
    print s, '\n'

class FrameError(ValueError): pass

class Vector:
    def __init__(self, array, frame=None):
        self.array = array
        self.frame = frame

    def __str__(self):
        if self.frame == None:
            return '^{O}%s' % (str(self.array), )
        else:
            return '^{%s}%s' % (str(self.frame), str(self.array))

    def __add__(self, other):
        if self.frame != other.frame: raise FrameError
        return Vector(self.array + other.array, self.frame)

    def from_list(t, frame=None):
        return Vector(array(t), frame)

    from_list = staticmethod(from_list)


class Rotation:
    def __init__(self, array):
        self.array = array
    
    def __str__(self):
        return 'Rotation\n%s' % str(self.array)

    def __neg__(self):
        return Rotation(-self.array)

    def __mul__(self, other):
        return dot(self.array, other.array)

    __call__ = __mul__
    
    def from_axis(axis, theta):
        x, y, z = ravel(axis.array)
        c = cos(theta)
        u = 1.0-c
        s = sqrt(1.0-c*c)
        xu, yu, zu = x*u, y*u, z*u
        v1 = [x*xu + c, x*yu - z*s, x*zu + y*s]
        v2 = [x*yu + z*s, y*yu + c, y*zu - x*s]
        v3 = [x*zu - y*s, y*zu + x*s, z*zu + c]
        return Rotation(array([v1, v2, v3]))

    from_axis = staticmethod(from_axis)

    def to_axis(self):
        # return the equivalent angle-axis as (khat, theta)
        pass

    def transpose(self):
        return Rotation(transpose(self.array))

    inverse = transpose
    

class Transform:
    def __init__(self, rot, org, source=None):
        self.rot = rot
        self.org = org
        self.dest = org.frame
        self.source = source
        self.source.add_transform(self)

    def __str__(self):
        if self.dest == None:
            return '%s' % self.source.name
            return '_{%s}^{O}T' % self.source.name
        else:
            return '_{%s}^{%s}T' % (self.source.name, self.dest.name)
            
    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.mul_vector(other)
        if isinstance(other, Transform):
            return self.mul_transform(other)

    __call__ = __mul__

    def mul_vector(self, p):
        if p.frame != self.source: raise FrameError
        return Vector(self.rot * p, self.dest) + self.org

    def mul_transform(self, other):
        if other.dest != self.source: raise FrameError
        rot = Rotation(self.rot * other.rot)
        t = Transform(rot, self * other.org, other.source)
        return t

    def inverse(self):
        irot = self.rot.inverse()
        iorg = Vector(-(irot * self.org), self.source)
        t = Transform(irot, iorg, self.dest)
        return t


class Frame:
    roster = []
    
    def __init__(self, name):
        self.name = name
        self.transforms = {}
        Frame.roster.append(self)

    def __str__(self): return self.name

    def add_transform(self, transform):
        if transform.source != self: raise FrameError
        if transform.dest:
            self.transforms[transform.dest] = transform

    def dests(self): return self.transforms.keys()
    

class Vertex:
    def __init__(self, frame):
        self.frame = frame
        self.dist = 1000000
        self.out = []

    def __str__(self):
        return '%s %d' % (self.frame.name, self.dist)


def shortest_path(start, frames):
    # for a given list of frames and a starting frame,
    # find the shortest path of transforms from the
    # starting frame to all other frames.
    # The 'distance' is the number of inverse transformations
    # that must be calculated.
    # The result is a dictionary of vertices, where
    # each vertex is labeled with the frame it corresponds
    # to, the distance from the starting frame, and the prev
    # frame along the path from start.
    map = dict([(f, Vertex(f)) for f in frames])
    
    length = {}
    for v in map.values():
        for dest in v.frame.transforms:
            w = map[dest]
            v.out.append(w)
            length[(v, w)] = 0

            w.out.append(v)
            length[(w, v)] = 1

    s = map[start]
    s.dist = 0
    queue = [s]

    while queue:
        v = queue.pop()
        for w in v.out:
            d = v.dist + length[(v,w)]
            if d < w.dist:
                w.dist = d
                w.prev = v
                if w not in queue: queue.append(w)

    return map

def print_shortest_path(map):
    for source, v in map.items():
        try:
            v.prev
            print source, v.dist, v.prev.frame
        except:
            print source, v.dist

def print_length(length):
    for v, w in length:
        print v.frame.name, w.frame.name, length[(v, w)]
    print ''


def main(name):

    theta = pi/2

    v_o = Vector.from_list([0, 0, 0], None)
    o = Frame('O')
    orig = Transform(None, v_o, o)

    xhat = Vector.from_list([1, 0, 0], o)
    rx = Rotation.from_axis(xhat, theta)
    a = Frame('A')
    t_ao = Transform(rx, xhat, a)

    yhat = Vector.from_list([0, 1, 0], a)
    ry = Rotation.from_axis(yhat, theta)
    b = Frame('B')
    t_ba = Transform(ry, yhat, b) 
    
    zhat = Vector.from_list([0, 0, 1], b)
    rz = Rotation.from_axis(zhat, theta)
    c = Frame('C') 
    t_cb = Transform(rz, zhat, c)

    p_c = Vector.from_list([1, 1, 1], c)
    println(p_c)

    p_b = t_cb(p_c)
    println(p_b)

    p_a = t_ba(p_b)
    println(p_a)

    p = t_ao(p_a)
    println(p)

    map = shortest_path(o, Frame.roster)
    print_shortest_path(map)
    
    cbao = t_ao(t_ba(t_cb))
    p = cbao(p_c)
    println(p)

    inv = cbao.inverse()
    p_c = inv(p)
    println(p_c)

    map = shortest_path(o, Frame.roster)
    print_shortest_path(map)

        
if __name__ == '__main__':
    main(*sys.argv)
