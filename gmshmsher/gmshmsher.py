import gmsh


def apply_function(func, args, kwargs):
    if kwargs is None:
        return func(*args)
    else:
        return func(*args, **kwargs)


def create_points(geometry_definition, gmsh_definition):
    points = {}
    for k, v in geometry_definition["points"].items():
        points[k] = apply_function(
            gmsh.model.occ.addPoint, v["data"], v.get("extra_args")
        )
    gmsh_definition["points"] = points


def create_curves(geometry_definition, gmsh_definition):
    curves = {}
    for k, v in geometry_definition["curves"].items():
        curve_type = v["type"]
        match curve_type:
            case "line":
                geo_start_tag, geo_end_tag = v["data"]
                start_tag = gmsh_definition["points"][geo_start_tag]
                end_tag = gmsh_definition["points"][geo_end_tag]
                curves[k] = apply_function(
                    gmsh.model.occ.addLine, (start_tag, end_tag), v.get("extra_args")
                )
            case _:
                print(
                    "Wrong curve type ({curve_type}) for curve: {curve_name}".format(
                        curve_type=curve_type, curve_name=k
                    )
                )
                gmsh.finalize()
                exit()
    gmsh_definition["curves"] = curves


def create_surfaces(geometry_definition, gmsh_definition):
    surfaces = {}
    for k, v in geometry_definition["surfaces"].items():
        surface_type = v["type"]
        match surface_type:
            case "filling":
                geo_line_curves = v["data"]
                curve_loop = []
                for curve in geo_line_curves:
                    curve_loop.append(gmsh_definition["curves"][curve])
                surfaces[k] = apply_function(
                    gmsh.model.occ.addSurfaceFilling,
                    (gmsh.model.occ.addCurveLoop(curve_loop),),
                    v.get("extra_args"),
                )
            case _:
                print(
                    "Wrong surface type ({surface_type}) for surface: {surface_name}".format(
                        surface_type=surface_type, surface_name=k
                    )
                )
                gmsh.finalize()
                exit()
    gmsh_definition["surfaces"] = surfaces


def create_volumes(geometry_definition, gmsh_definition):
    volumes = {}
    for k, v in geometry_definition["volumes"].items():
        volume_type = v["type"]
        match volume_type:
            case "volume":
                geo_contour_surfaces = v["data"]["contour"]
                geo_holes_surfaces = v["data"]["holes"]
                contour_surfaces_loop = []
                for surface in geo_contour_surfaces:
                    contour_surfaces_loop.append(gmsh_definition["surfaces"][surface])
                hole_surfaces_loops = []
                for hole_surfaces in geo_holes_surfaces:
                    hole_surfaces_loop = []
                    for surface in hole_surfaces:
                        hole_surfaces_loop.append(gmsh_definition["surfaces"][surface])
                    hole_surfaces_loops.append(hole_surfaces_loop)
                surfaces_loops = [contour_surfaces_loop] + hole_surfaces_loops
                shell_tags = [
                    gmsh.model.occ.addSurfaceLoop(loop) for loop in surfaces_loops
                ]
                volumes[k] = apply_function(
                    gmsh.model.occ.addVolume,
                    (shell_tags,),
                    v.get("extra_args"),
                )
            case _:
                print(
                    "Wrong volume type ({volume_type}) for volume: {volume_name}".format(
                        volume_type=volume_type, volume_name=k
                    )
                )
                gmsh.finalize()
                exit()
    gmsh_definition["volumes"] = volumes


def get_nodes(fem_mesh):
    node_idxs, coord_array, _ = gmsh.model.mesh.getNodes(returnParametricCoord=False)
    nodes = {}
    for i, node in enumerate(node_idxs):
        nodes[node] = coord_array[3 * i : 3 * (i + 1)]
    fem_mesh["nodes"] = nodes


def get_point_elements(gmsh_definition, fem_mesh):
    points = {}
    for geo_element, tag in gmsh_definition["points"].items():
        element_type = gmsh.model.mesh.getElementTypes(0, tag)[0]
        elements, nodes = gmsh.model.mesh.getElementsByType(element_type, tag)
        elements_data = []
        for i, elem in enumerate(elements):
            match element_type:
                case 15:
                    n_nodes = 1
                case _:
                    print(
                        "Wrong element type ({element_type}) for point: {point_name}".format(
                            element_type=element_type, point_name=geo_element
                        )
                    )
                    gmsh.finalize()
                    exit()
            elements_data.append(
                {
                    "type": element_type,
                    "id": elem,
                    "nodes": nodes[n_nodes * i : n_nodes * (i + 1)],
                }
            )
        points[geo_element] = elements_data
    fem_mesh["points"] = points


def get_curve_elements(gmsh_definition, fem_mesh):
    curves = {}
    for geo_element, tag in gmsh_definition["curves"].items():
        element_type = gmsh.model.mesh.getElementTypes(1, tag)[0]
        elements, nodes = gmsh.model.mesh.getElementsByType(element_type, tag)
        elements_data = []
        for i, elem in enumerate(elements):
            match element_type:
                case 1:
                    n_nodes = 2
                case _:
                    print(
                        "Wrong element type ({element_type}) for curve: {curve_name}".format(
                            element_type=element_type, curve_name=geo_element
                        )
                    )
                    gmsh.finalize()
                    exit()
            elements_data.append(
                {
                    "type": element_type,
                    "id": elem,
                    "nodes": nodes[n_nodes * i : n_nodes * (i + 1)],
                }
            )
        curves[geo_element] = elements_data
    fem_mesh["curves"] = curves


def get_surface_elements(gmsh_definition, fem_mesh):
    surfaces = {}
    for geo_element, tag in gmsh_definition["surfaces"].items():
        element_type = gmsh.model.mesh.getElementTypes(2, tag)[0]
        elements, nodes = gmsh.model.mesh.getElementsByType(element_type, tag)
        elements_data = []
        for i, elem in enumerate(elements):
            match element_type:
                case 2:
                    n_nodes = 3
                case _:
                    print(
                        "Wrong element type ({element_type}) for surface: {surface_name}".format(
                            element_type=element_type, surface_name=geo_element
                        )
                    )
                    gmsh.finalize()
                    exit()
            elements_data.append(
                {
                    "type": element_type,
                    "id": elem,
                    "nodes": nodes[n_nodes * i : n_nodes * (i + 1)],
                }
            )
        surfaces[geo_element] = elements_data
    fem_mesh["surfaces"] = surfaces


def get_volume_elements(gmsh_definition, fem_mesh):
    volumes = {}
    for geo_element, tag in gmsh_definition["volumes"].items():
        element_type = gmsh.model.mesh.getElementTypes(3, tag)[0]
        elements, nodes = gmsh.model.mesh.getElementsByType(element_type, tag)
        elements_data = []
        for i, elem in enumerate(elements):
            match element_type:
                case 4:
                    n_nodes = 4
                case _:
                    print(
                        "Wrong element type ({element_type}) for volume: {volume_name}".format(
                            element_type=element_type, volume_name=geo_element
                        )
                    )
                    gmsh.finalize()
                    exit()
            elements_data.append(
                {
                    "type": element_type,
                    "id": elem,
                    "nodes": nodes[n_nodes * i : n_nodes * (i + 1)],
                }
            )
        volumes[geo_element] = elements_data
    fem_mesh["volumes"] = volumes


def get_fem_mesh(geometry_definition, open_gui="no", gmsh_hook=None):
    assert open_gui in ["geometry", "mesh", "both", "no"]

    gmsh.initialize()

    if gmsh_hook is not None:
        gmsh_hook(gmsh)

    gmsh_definition = {}
    create_points(geometry_definition, gmsh_definition)
    create_curves(geometry_definition, gmsh_definition)
    create_surfaces(geometry_definition, gmsh_definition)
    create_volumes(geometry_definition, gmsh_definition)
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

    fem_mesh = {}
    get_nodes(fem_mesh)
    get_point_elements(gmsh_definition, fem_mesh)
    get_curve_elements(gmsh_definition, fem_mesh)
    get_surface_elements(gmsh_definition, fem_mesh)
    get_volume_elements(gmsh_definition, fem_mesh)

    gmsh.finalize()

    return fem_mesh
