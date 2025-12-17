import manim
import numpy as np
import ast

class EmptyVMobject(VMobject): pass

NAMES = {
    "UP": manim.UP,
    "DOWN": manim.DOWN,
    "LEFT": manim.LEFT,
    "RIGHT": manim.RIGHT,
    "IN": manim.IN,
    "OUT": manim.OUT,
    "UL": manim.UL,
    "UR": manim.UR,
    "DL": manim.DL,
    "DR": manim.DR,
    "PI": manim.PI,
    "TAU": manim.TAU,

    #functions:
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
    "len": len,
    "sorted": sorted,
    "all": all,
    "any": any,
    "equals": (lambda a, b: a == b),
    "min": min,
    "max": max,
    "abs": abs,
    "pow": pow,
    "floor": int,
    "ceil": np.ceil,
    "round": round,
    "trunc": np.trunc,
    "sqrt": np.sqrt,
    "cbrt": np.cbrt,
    "log": np.log,
    "log10": np.log10,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "asin": np.asin,
    "acos": np.acos,
    "atan": np.atan,
    "atan2": np.atan2,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    "asinh": np.asinh,
    "acosh": np.acosh,
    "atanh": np.atanh,
    "array": np.array,
    "norm": np.linalg.norm,
    "EmptyVMobject": EmptyVMobject
}

def get_all_subclasses(cls):
    sc = cls.__subclasses__()
    return set(sc).union(s for c in sc for s in get_all_subclasses(c))

for cls in get_all_subclasses(manim.VMobject):
    NAMES[cls.__name__] = cls

ATTRIBUTES = {
    list: frozenset(["index", "count"]),
    manim.VMobject: frozenset([
        "add", "align_to", "append_points", "apply_function", "apply_matrix",
        "arrange", "arrange_in_grid", "arrange_submobjects", "become", "center",
        "clear_points", "color", "copy", "depth", "fade", "fade_to", "fill_color",
        "flip", "force_direction", "get_all_points", "get_arc_length", "get_bottom",
        "get_boundary_point", "get_center", "get_center_of_mass", "get_color",
        "get_coord", "get_corner", "get_curve_functions", "get_curve_functions_with_lengths",
        "get_direction", "get_edge_center", "get_end", "get_fill_color",
        "get_fill_colors", "get_fill_opacities", "get_fill_opacity", "get_fill_rgbas",
        "get_gradient_start_and_end_points", "get_last_point", "get_left", "get_midpoint",
        "get_nth_curve_function", "get_nth_curve_function_with_length","get_nth_curve_length",
        "get_nth_curve_length_pieces", "get_nth_curve_points","get_num_curves",
        "get_num_points", "get_pieces", "get_point_mobject", "get_points_defining_boundary",
        "get_right", "get_sheen_direction", "get_sheen_factor", "get_start", "get_start_and_end",
        "get_stroke_color", "get_stroke_colors", "get_stroke_opacities", "get_stroke_opacity",
        "get_stroke_rgbas", "get_stroke_width", "get_style", "get_subcurve", "get_subpaths",
        "get_subpaths_from_points", "get_top", "get_x", "get_y", "get_z",
        "get_z_index_reference_point", "has_no_points", "has_points", "height", "init_colors",
        "interpolate", "interpolate_color", "invert", "is_closed", "is_off_screen", "length_over_dim",
        "move_to", "n_points_per_curve", "next_to", "nonempty_submobjects", "null_point_align",
        "point_from_proportion", "pose_at_angle", "proportion_from_point", "put_start_and_end_on",
        "remove", "replace", "rescale_to_fit", "reset_points", "resize_points", "reverse_direction",
        "reverse_points", "rotate", "rotate_about_origin", "rotate_sheen_direction", "scale",
        "scale_to_fit_height", "scale_to_fit_width", "set_color", "set_color_by_gradient",
        "set_colors_by_radial_gradient", "set_coord", "set_fill", "set_opacity", "set_points",
        "set_points_as_corners", "set_points_smoothly", "set_shade_in_3d", "set_sheen",
        "set_sheen_direction", "set_stroke", "set_style", "set_submobject_colors_by_gradient",
        "set_submobject_colors_by_radial_gradient", "set_x", "set_y", "set_z", "set_z_index",
        "set_z_index_by_z_Point3D", "sheen_factor", "shift", "shift_onto_screen", "show",
        "space_out_submobjects", "split", "stretch", "stretch_about_point",
        "stretch_to_fit_height", "stretch_to_fit_width", "stroke_color",
        "surround", "to_corner", "to_edge", "width"]),
    }

class PNodeVisitor(ast.NodeVisitor):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene

    def visit_Call(self, node):
        args = [self.visit(arg) for arg in node.args]
        kwargs = dict([(kw.arg, self.visit(kw.value)) for kw in node.keywords])
        return self.visit(node.func)(*args, **kwargs)
    
    def visit_Attribute(self, node):
        obj = self.visit(node.value)
        attr_name = node.attr
        allowed_cls = next((cls for cls in type(obj).__mro__[::-1] if cls in ATTRIBUTES), None)
        if allowed_cls == None or node.attr not in ATTRIBUTES[allowed_cls]:
            raise ValueError(f"Attribute '{type(node.value).__name__}.{node.attr}' not recognized")
        return getattr(obj, attr_name)

    def visit_Name(self, node):
        if node.id == "PMOBS":
            return self.scene.pmobs
        if node.id not in NAMES:
            raise ValueError(f"Name '{node.id}' not recognized")
        return NAMES[node.id]
    
    def visit_List(self, node):
        return [self.visit(item) for item in node.elts]

    def visit_Constant(self, node):
        return ast.literal_eval(node)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.FloorDiv):
            return left // right
        if isinstance(node.op, ast.Mod):
            return left % right
        if isinstance(node.op, ast.Pow):
            return pow(left, right)
        if isinstance(node.op, ast.MatMult):
            return left @ right
        raise ValueError("Operator not recognized")
    
    def visit_UnaryOp(self, node):
        if isinstance(node.op, ast.UAdd):
            return +self.visit(node.operand)
        if isinstance(node.op, ast.USub):
            return -self.visit(node.operand)
        if isinstance(node.op, ast.Invert):
            return ~self.visit(node.operand)
        if isinstance(node.op, ast.Not):
            return not self.visit(node.operand)
        raise ValueError("Operator not recognized")
    
    def visit_Subscript(self, node):
        return self.visit(node.value)[self.visit(node.slice)]

    def visit_Slice(self, node):
        return slice(
            self.visit(node.lower),
            self.visit(node.upper),
            self.visit(node.step)
            )
    
    def visit_Lambda(self, node):
        raise NotImplementedError("I have no idea how to implement that")

    def generic_visit(self, node):
        raise ValueError(f"Unsupported syntax: {type(node).__name__}")

def create_node_visitor(scene: manim.Scene):
    return PNodeVisitor(scene)

def pasos_eval(expr, node_visitor):
    return node_visitor.visit(ast.parse(expr, mode="eval").body)

if __name__ == "__main__":
    NAMES["quit"] = quit
    nv = create_node_visitor(manim.Scene())
    while True:
        try:
            #for node in ast.walk(ast.parse(input(">>> "), mode="eval")):
            #    print(node)
            #    print(node.__dict__)
            #    print(" ")
            print(pasos_eval(input(">>> "), nv))
        except Exception as e:
            print(e)