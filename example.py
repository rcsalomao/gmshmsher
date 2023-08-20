from pprint import pp
from gmshmsher import get_fem_mesh

geometry = {
    "x1": {"type": "point", "data": (0, 0, 1)},
    "x2": {"type": "point", "data": (1, 0, 0)},
    "x3": {"type": "point", "data": (1, 1, 1)},
    "x4": {"type": "point", "data": (0, 1, 0)},
    "line1": {"type": "line", "data": ("x1", "x2")},
    "line2": {"type": "line", "data": ("x2", "x3")},
    "line3": {"type": "line", "data": ("x3", "x4")},
    "line4": {"type": "line", "data": ("x4", "x1")},
    "surface1": {
        "type": "surface filling",
        "data": ("line1", "line2", "line3", "line4"),
    },
}

pp(geometry)
mesh = get_fem_mesh(geometry, "no")
pp(mesh)
