from pprint import pp
from gmshmsher import get_fem_mesh

geometry = {
    "points": {
        "x1": {"data": (0, 0, 0)},
        "x2": {"data": (1, 0, 0)},
        "x3": {"data": (1, 1, 0)},
        "x4": {"data": (0, 1, 0)},
    },
    "curves": {
        "line1": {"type": "line", "data": ("x1", "x2")},
        "line2": {"type": "line", "data": ("x2", "x3")},
        "line3": {"type": "line", "data": ("x3", "x4")},
        "line4": {"type": "line", "data": ("x4", "x1")},
    },
    "surfaces": {
        "surface1": {
            "type": "filling",
            "data": ("line1", "line2", "line3", "line4"),
        },
    },
    "volumes": {},
}

pp(geometry)
mesh = get_fem_mesh(geometry, 'no')
pp(mesh)
