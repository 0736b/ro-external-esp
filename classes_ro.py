"""
    from 2021-11-17_Ragexe_4thjob.exe, so maybe not work with other version.
"""

from classes_math import Vector3D, Matrix
from classes_ro_structure import LinkedList


class CGameMode:

    offset_pointer_to_cworld = 0xCC
    offset_pointer_to_cview = 0xD0
    offset_map_rsw = 0x68
    offset_map_bmp = 0xA0

    def __init__(self, proc, addr):
        self.proc = proc
        self.addr = addr
        self.map_rsw = self.proc.read_string((self.addr + CGameMode.offset_map_rsw), 40)
        self.map_bmp = self.proc.read_string((self.addr + CGameMode.offset_map_bmp), 40)
        self.valid = (".rsw" in self.map_rsw) and (".bmp" in self.map_bmp)
        self.world = None
        self.view = None
        if self.valid:
            self.world = CWorld(proc, self.proc.read_int(self.addr + CGameMode.offset_pointer_to_cworld))
            self.view = CView(proc, self.proc.read_int(self.addr + CGameMode.offset_pointer_to_cview))

    def update(self):
        return CGameMode(self.proc, self.addr)


class CWorld:

    offset_pointer_to_actor_list = 0x10
    offset_len_actor_list = 0x14
    offset_pointer_to_item_list = 0x18
    offset_len_item_list = 0x1C
    offset_pointer_to_c3dattr = 0x30
    offset_pointer_to_cplayer = 0x2C

    def __init__(self, proc, addr):
        self.proc = proc
        self.addr = addr
        self.actor_list = LinkedList(self.proc, self.proc.read_int(self.addr + CWorld.offset_pointer_to_actor_list), CNpc)
        self.len_actor_list = self.proc.read_int(self.addr + CWorld.offset_len_actor_list)
        self.item_list = LinkedList(self.proc, self.proc.read_int(self.addr + CWorld.offset_pointer_to_item_list), CItem)
        self.len_item_list = self.proc.read_int(self.addr + CWorld.offset_len_item_list)
        self.c3dattr = C3dAttr(self.proc, self.proc.read_int(self.addr + CWorld.offset_pointer_to_c3dattr))
        self.player = CPlayer(self.proc, self.proc.read_int(self.addr + CWorld.offset_pointer_to_cplayer))


class CView:

    offset_matrix_viewmatrix = 0x98

    def __init__(self, proc, addr):
        self.proc = proc
        self.addr = addr
        self.viewmatrix_matrix = Matrix(
            self.proc.read_float(self.addr + (CView.offset_matrix_viewmatrix + (0 * 4))),
            self.proc.read_float(self.addr + (CView.offset_matrix_viewmatrix + (1 * 4))),
            self.proc.read_float(self.addr + (CView.offset_matrix_viewmatrix + (2 * 4))),
            self.proc.read_float(self.addr + (CView.offset_matrix_viewmatrix + (3 * 4))),
            self.proc.read_float(self.addr + (CView.offset_matrix_viewmatrix + (4 * 4))),
            self.proc.read_float(self.addr + (CView.offset_matrix_viewmatrix + (5 * 4))),
            self.proc.read_float(self.addr + (CView.offset_matrix_viewmatrix + (6 * 4))),
            self.proc.read_float(self.addr + (CView.offset_matrix_viewmatrix + (7 * 4))),
            self.proc.read_float(self.addr + (CView.offset_matrix_viewmatrix + (8 * 4))),
            self.proc.read_float(self.addr + (CView.offset_matrix_viewmatrix + (9 * 4))),
            self.proc.read_float(self.addr + (CView.offset_matrix_viewmatrix + (10 * 4))),
            self.proc.read_float(self.addr + (CView.offset_matrix_viewmatrix + (11 * 4)))
        )


class CPlayer:

    offset_vector3d_pos = 0x10
    offset_is_pc = 0xA8
    offset_job_id = 0x260

    def __init__(self, proc, addr):
        self.proc = proc
        self.addr = addr
        self.pos_vector3d = Vector3D(
            self.proc.read_float(self.addr + (CPlayer.offset_vector3d_pos + (0 * 4))),
            self.proc.read_float(self.addr + (CPlayer.offset_vector3d_pos + (1 * 4))),
            self.proc.read_float(self.addr + (CPlayer.offset_vector3d_pos + (2 * 4)))
        )
        self.job_id_int = self.proc.read_int(self.addr + CPlayer.offset_job_id)
        self.is_pc = self.proc.read_int(self.addr + CPlayer.offset_is_pc)


class CNpc:

    offset_vector3d_pos = 0x10
    offset_int_id = 0x10C
    offset_is_pc = 0xA8

    def __init__(self, proc, addr):
        self.proc = proc
        self.addr = addr
        self.pos_vector3d = Vector3D(
            self.proc.read_float(self.addr + (CNpc.offset_vector3d_pos + (0 * 4))),
            self.proc.read_float(self.addr + (CNpc.offset_vector3d_pos + (1 * 4))),
            self.proc.read_float(self.addr + (CNpc.offset_vector3d_pos + (2 * 4)))
        )
        self.id_int = self.proc.read_int(self.addr + CNpc.offset_int_id)
        self.is_pc = self.proc.read_int(self.addr + CNpc.offset_is_pc)


class CItem:

    offset_vector3d_pos = 0x10
    offset_int_id = 0x170

    def __init__(self, proc, addr):
        self.proc = proc
        self.addr = addr
        self.pos_vector3d = Vector3D(
            self.proc.read_float(self.addr + (CItem.offset_vector3d_pos + (0 * 4))),
            self.proc.read_float(self.addr + (CItem.offset_vector3d_pos + (1 * 4))),
            self.proc.read_float(self.addr + (CItem.offset_vector3d_pos + (2 * 4)))
        )
        self.id_int = self.proc.read_int(self.addr + CItem.offset_int_id)


class C3dAttr:

    offset_int_width = 0x110
    offset_int_height = 0x114
    offset_int_zoom = 0x118

    def __init__(self, proc, addr):
        self.proc = proc
        self.addr = addr
        self.width = self.proc.read_int(self.addr + C3dAttr.offset_int_width)
        self.height = self.proc.read_int(self.addr + C3dAttr.offset_int_height)
        self.zoom = self.proc.read_int(self.addr + C3dAttr.offset_int_zoom)

    def convert_world_to_cell_coord(self, wx, wz):
        try:
            cx = int(wx / self.zoom + self.width / 2)
            cy = int(wz / self.zoom + self.height / 2)
        except Exception:
            return (0, 0)
        return (cx, cy)


class CRenderer:

    offset_float_hpc = 0x0
    offset_float_vpc = 0x4
    offset_float_hratio = 0x8
    offset_float_vratio = 0xC
    offset_int_x_offset = 0x1C
    offset_int_y_offset = 0x20
    offset_int_width = 0x24
    offset_int_height = 0x28
    offset_int_rgb_bit_count = 0x38

    def __init__(self, proc, addr):
        self.proc = proc
        self.addr = addr
        self.hpc = self.proc.read_float(self.addr + CRenderer.offset_float_hpc)
        self.vpc = self.proc.read_float(self.addr + CRenderer.offset_float_vpc)
        self.hratio = self.proc.read_float(self.addr + CRenderer.offset_float_hratio)
        self.vratio = self.proc.read_float(self.addr + CRenderer.offset_float_vratio)
        self.x_offset = self.proc.read_int(self.addr + CRenderer.offset_int_x_offset)
        self.y_offset = self.proc.read_int(self.addr + CRenderer.offset_int_y_offset)
        self.width = self.proc.read_int(self.addr + CRenderer.offset_int_width)
        self.height = self.proc.read_int(self.addr + CRenderer.offset_int_height)
        self.rgb_bitcount = self.proc.read_int(self.addr + CRenderer.offset_int_rgb_bit_count)

    def update(self):
        return CRenderer(self.proc, self.addr)

    def project_vertex(self, src, vtm):
        viewvect = Vector3D()
        viewvect = viewvect.matrix_mult(src, vtm)
        w = 1.0 / viewvect.z
        x = viewvect.x * w * self.hpc + self.x_offset
        y = viewvect.y * w * self.vpc + self.y_offset
        return x, y

    def project_vertex_ex(self, src, pointvector, vtm):
        viewvect = Vector3D()
        viewvect = viewvect.matrix_mult(src, vtm)
        viewvect += pointvector
        w = 1.0 / viewvect.z
        x = viewvect.x * w * self.hpc + self.x_offset
        y = viewvect.y * w * self.vpc + self.y_offset
        return x, y