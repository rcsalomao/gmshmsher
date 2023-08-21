import gmsh
from .smol_graph import Graph
from .kahn_algorithm import kahn_algorithm


def apply_function(func, args, kwargs):
    if kwargs is None:
        return func(*args)
    else:
        return func(*args, **kwargs)


def get_geometry_graph(geometry: dict):
    g = Graph()
    for key, value in geometry.items():
        match value["type"]:
            case "point":
                g.add_vertex(key)
            case "line":
                for u in value["data"]:
                    g.add_edge(u, key)
            case "surface-filling":
                for u in value["data"]:
                    g.add_edge(u, key)
            case "volume":
                for u in value["data"]["contour"]:
                    g.add_edge(u, key)
                for surfaces in value["data"]["holes"]:
                    for u in surfaces:
                        g.add_edge(u, key)
            case _:
                raise Exception("Geometry type not supported")
    return g


def get_nodes(fem_mesh):
    node_idxs, coord_array, _ = gmsh.model.mesh.getNodes(returnParametricCoord=False)
    nodes = {}
    for i, node in enumerate(node_idxs):
        nodes[node] = coord_array[3 * i : 3 * (i + 1)]
    fem_mesh["nodes"] = nodes


def get_fem_elements(
    gmsh_definition,
    fem_mesh,
    geo_key,
    dim_tag,
    element_type_n_nodes_map: dict,
):
    dim, tag = dim_tag
    element_type = gmsh.model.mesh.getElementTypes(dim, tag)[0]
    elements, nodes = gmsh.model.mesh.getElementsByType(element_type, tag)
    n_nodes = element_type_n_nodes_map.get(element_type)
    if n_nodes:
        elements_data = []
        for i, elem in enumerate(elements):
            elements_data.append(
                {
                    "type": element_type,
                    "id": elem,
                    "nodes": nodes[n_nodes * i : n_nodes * (i + 1)],
                }
            )
        fem_mesh[geo_key] = elements_data
    else:
        print(
            "Unsupported element type ({elem_type}) for geometry: {geo_key}".format(
                elem_type=element_type, geo_key=geo_key
            )
        )
        gmsh.finalize()
        exit()


def get_fem_mesh(geometry_definition, open_gui="no", gmsh_hook=None):
    assert open_gui in ["geometry", "mesh", "both", "no"]

    geometry_graph = get_geometry_graph(geometry_definition)
    sorted_geometry_order = kahn_algorithm(geometry_graph)

    gmsh.initialize()

    if gmsh_hook is not None:
        gmsh_hook(gmsh)

    gmsh_definition = {}
    for geo_key in sorted_geometry_order:
        geometry = geometry_definition[geo_key]
        match geometry["type"]:
            case "point":
                gmsh_definition[geo_key] = (
                    0,
                    apply_function(
                        gmsh.model.occ.addPoint,
                        geometry["data"],
                        geometry.get("extra_args"),
                    ),
                )
            case "line":
                geo_start_key, geo_end_key = geometry["data"]
                _, gmsh_start_tag = gmsh_definition[geo_start_key]
                _, gmsh_end_tag = gmsh_definition[geo_end_key]
                gmsh_definition[geo_key] = (
                    1,
                    apply_function(
                        gmsh.model.occ.addLine,
                        (gmsh_start_tag, gmsh_end_tag),
                        geometry.get("extra_args"),
                    ),
                )
            case "surface-filling":
                geo_curves = geometry["data"]
                curve_loop = []
                for curve in geo_curves:
                    _, gmsh_curve_tag = gmsh_definition[curve]
                    curve_loop.append(gmsh_curve_tag)
                gmsh_definition[geo_key] = (
                    2,
                    apply_function(
                        gmsh.model.occ.addSurfaceFilling,
                        (gmsh.model.occ.addCurveLoop(curve_loop),),
                        geometry.get("extra_args"),
                    ),
                )
            case "volume":
                geo_contour_surfaces = geometry["data"]["contour"]
                contour_surfaces_loop = []
                for surface in geo_contour_surfaces:
                    _, gmsh_surface_tag = gmsh_definition[surface]
                    contour_surfaces_loop.append(gmsh_surface_tag)
                hole_surfaces_loops = []
                geo_holes_surfaces = geometry["data"].get("holes")
                if geo_holes_surfaces:
                    for hole_surfaces in geo_holes_surfaces:
                        hole_surfaces_loop = []
                        for surface in hole_surfaces:
                            _, gmsh_surface_tag = gmsh_definition[surface]
                            hole_surfaces_loop.append(gmsh_surface_tag)
                        hole_surfaces_loops.append(hole_surfaces_loop)
                surfaces_loops = [contour_surfaces_loop] + hole_surfaces_loops
                shell_tags = [
                    gmsh.model.occ.addSurfaceLoop(loop) for loop in surfaces_loops
                ]
                gmsh_definition[geo_key] = (
                    3,
                    apply_function(
                        gmsh.model.occ.addVolume,
                        (shell_tags,),
                        geometry.get("extra_args"),
                    ),
                )
            case _:
                print(
                    "Unsupported geometry type ({geo_type}) for geometry: {geo_key}".format(
                        geo_type=geometry["type"], geo_key=geo_key
                    )
                )
                gmsh.finalize()
                exit()

    gmsh.model.occ.synchronize()

    if open_gui in ["geometry", "both"]:
        gmsh.fltk.initialize()
        while gmsh.fltk.isAvailable():
            gmsh.fltk.wait()

    gmsh.model.mesh.generate()

    if open_gui in ["mesh", "both"]:
        gmsh.fltk.initialize()
        while gmsh.fltk.isAvailable():
            gmsh.fltk.wait()

    element_type_n_nodes_map = {1: 2, 2: 3, 4: 4, 15: 1}
    fem_mesh = {}
    get_nodes(fem_mesh)
    for geo_key, dim_tag in gmsh_definition.items():
        get_fem_elements(
            gmsh_definition,
            fem_mesh,
            geo_key,
            dim_tag,
            element_type_n_nodes_map,
        )

    gmsh.finalize()

    return fem_mesh
