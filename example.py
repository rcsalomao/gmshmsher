from pprint import pp
from gmshmsher import get_fem_mesh

geometry_1 = {
    "x1": {"type": "point", "data": (0, 0, 1)},
    "x2": {"type": "point", "data": (1, 0, 0)},
    "x3": {"type": "point", "data": (1, 1, 1)},
    "x4": {"type": "point", "data": (0, 1, 0)},
    "line1": {"type": "line", "data": ("x1", "x2")},
    "line2": {"type": "line", "data": ("x2", "x3")},
    "line3": {"type": "line", "data": ("x3", "x4")},
    "line4": {"type": "line", "data": ("x4", "x1")},
    "surface1": {
        "type": "surface-filling",
        "data": ("line1", "line2", "line3", "line4"),
    },
}
geometry_2 = {
    "x1": {"type": "point", "data": (0, 0, 0)},
    "x2": {"type": "point", "data": (1, 0, 0)},
    "x3": {"type": "point", "data": (1, 1, 0)},
    "x4": {"type": "point", "data": (0, 1, 0)},
    "line1": {"type": "line", "data": ("x1", "x2")},
    "line2": {"type": "line", "data": ("x2", "x3")},
    "line3": {"type": "line", "data": ("x3", "x4")},
    "line4": {"type": "line", "data": ("x4", "x1")},
    "circle1": {
        "type": "circle",
        "data": {
            "coords": (0.3, 0.3, 0),
            "radius": 0.05,
            # "extra_args": {
            #     "start_angle": 0,
            #     "end_angle": 2*math.pi,
            #     "z_axis": (0, 0, 1),
            # },
        },
    },
    "surface1": {
        "type": "plane-surface",
        "data": {
            "contour": ("line1", "line2", "line3", "line4"),
            "holes": [["circle1"], ["circle2"]],
        },
    },
    "circle2": {
        "type": "circle",
        "data": {
            "coords": (0.7, 0.7, 0),
            "radius": 0.05,
            # "extra_args": {
            #     "start_angle": 0,
            #     "end_angle": 2*math.pi,
            #     "z_axis": (0, 0, 1),
            # },
        },
    },
}

pp(geometry_2)
mesh = get_fem_mesh(geometry_2, "both")
pp(mesh)
