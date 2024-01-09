import numpy as np


class Vector3D:

    def __init__(self, nx=0.0, ny=0.0, nz=0.0):
        self.x = nx
        self.y = ny
        self.z = nz

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def matrix_mult(self, v, m):
        x = v.x * m.v11 + v.y * m.v21 + v.z * m.v31 + m.v41
        y = v.x * m.v12 + v.y * m.v22 + v.z * m.v32 + m.v42
        z = v.x * m.v13 + v.y * m.v23 + v.z * m.v33 + m.v43
        return Vector3D(x, y, z)
    
    def get_array(self):
        return np.array([self.x, self.y, self.z])


class Matrix:

    def __init__(self, v11, v12, v13, v21, v22, v23, v31, v32, v33, v41, v42, v43):
        self.v11 = v11
        self.v12 = v12
        self.v13 = v13
        self.v21 = v21
        self.v22 = v22
        self.v23 = v23
        self.v31 = v31
        self.v32 = v32
        self.v33 = v33
        self.v41 = v41
        self.v42 = v42
        self.v43 = v43

    def get_array(self):
        return np.array([
            self.v11, self.v12, self.v13,
            self.v21, self.v22, self.v23,
            self.v31, self.v32, self.v33,
            self.v41, self.v42, self.v43
        ])