import ast
import builtins
import inspect
import itertools
import textwrap
import types
import typing

if typing.TYPE_CHECKING:
    from .extractor import Logger


class ASTVisitor(ast.NodeVisitor):
    def __init__(
        self, function: typing.Callable, logger: "Logger", can_eval: bool = False
    ) -> None:
        self.function: typing.Callable = function
        self.logger = logger
        self.can_eval = can_eval
        self.locals: dict[str, typing.Any] = {}
        self.returns: list = []

    def get_variable(self, name: ast.Name) -> typing.Any:
        local_var = self.locals.get(name.id, None)
        if local_var is not None:
            return local_var
        globals_dict = getattr(self.function, "__globals__", {})
        global_var = globals_dict.get(name.id, None)
        if global_var is not None:
            return global_var
        builtin = getattr(builtins, name.id, None)
        if isinstance(builtin, type):
            return builtin
        return None

    def get_constant(self, constant: ast.Constant) -> typing.Any:
        try:
            constant_value = ast.literal_eval(constant)
            return type(constant_value)
        except Exception:
            return None

    def get_type_if_all_equal(self, expressions: list[ast.expr]) -> typing.Any:
        if len(expressions) == 0:
            return None
        if len(expressions) == 1:
            return self.get_value(expressions[0])

        el_types: dict[ast.expr, typing.Any] = {}
        for el1, el2 in itertools.pairwise(expressions):
            el1_type = el_types[el1] if el1 in el_types else self.get_value(el1)
            el_types.setdefault(el1, el1_type)

            el2_type = el_types[el2] if el2 in el_types else self.get_value(el2)
            el_types.setdefault(el2, el2_type)
            if el1_type != el2_type:
                return None

        return el_types[el1]

    def get_list(self, list_: ast.List) -> typing.Any:
        list_type = self.get_type_if_all_equal(list_.elts)
        return list if list_type is None else list[list_type]

    def get_tuple(self, tuple_: ast.Tuple) -> typing.Any:
        types = tuple(self.get_value(el) for el in tuple_.elts)
        if len([t for t in types if t is None]) != 0:
            return tuple
        return tuple[types]

    def get_dict(self, dict_: ast.Dict) -> typing.Any:
        if None in dict_.keys:
            # TODO: support unpacking
            return dict
        keys = typing.cast(list[ast.expr], dict_.keys)
        keys_type = self.get_type_if_all_equal(keys)
        values_type = self.get_type_if_all_equal(dict_.values)

        if keys_type is None and values_type is None:
            return dict

        return dict[
            typing.Any if keys_type is None else keys_type,
            typing.Any if values_type is None else values_type,
        ]

    def get_value(self, expr: ast.expr) -> typing.Any:
        match expr:
            case ast.Name():
                return self.get_variable(expr)
            case ast.Constant():
                return self.get_constant(expr)
            case ast.List():
                return self.get_list(expr)
            case ast.Tuple():
                return self.get_tuple(expr)
            case ast.Dict():
                return self.get_dict(expr)
            case ast.Call():
                return self.infer_call_type(expr)
            case _:
                return None

    def from_func_call(self, func: ast.Name) -> typing.Any:
        called_function = self.get_variable(func)
        if called_function is None:
            return None

        if isinstance(called_function, type):
            # This is a class
            return called_function

        origin = typing.get_origin(called_function) or called_function
        if isinstance(origin, type):
            # This is of the form type[T], so we should return T
            args = typing.get_args(called_function)
            if len(args) != 1:
                return None
            return args[0]

        annotations = getattr(called_function, "__annotations__", {})
        if "return" not in annotations:
            return infer_return_type(called_function, self.logger, self.can_eval)

        return annotations["return"]

    def from_method_call(self, method: ast.Attribute) -> typing.Any:
        value = self.get_value(method.value)
        if value is None:
            return None

        func = getattr(value, method.attr, None)
        if func is None or not callable(func):
            return None
        annotations = getattr(func, "__annotations__", {})
        if "return" not in annotations:
            return infer_return_type(func, self.logger, self.can_eval)
        return annotations["return"]

    def infer_call_type(self, call: ast.Call) -> typing.Any:
        callable_ = call.func

        match callable_:
            case ast.Name():
                return self.from_func_call(callable_)
            case ast.Attribute():
                return self.from_method_call(callable_)
            case _:
                return None

    def visit_Return(self, node: ast.Return) -> None:
        if node.value is not None:
            self.returns.append(self.get_value(node.value))
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        target = node.target
        if not isinstance(target, ast.Name):
            # TODO
            return
        annotation = self.get_value(node.annotation)
        if annotation is None and self.can_eval:
            annotation_string = ast.unparse(node.annotation)
            annotation_code = compile(
                annotation_string,
                "<annotation>",
                "eval",
                0,
            )
            try:
                function_globals = getattr(self.function, "__globals__", {})
                annotation = eval(annotation_code, function_globals, {})  # noqa: S307
            except Exception as e:
                self.logger.warning(
                    f"failed to parse annotation {annotation_string!r}: {e!s}"
                )
                annotation = None
        if annotation is not None:
            self.locals[target.id] = annotation
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            self.locals[target.id] = self.get_value(node.value)
        self.generic_visit(node)


def smart_type(type_: typing.Any) -> typing.Any:
    if isinstance(type_, type):
        return type[type_]
    return type_


def define_types_from_closure(function: typing.Callable, visitor: ASTVisitor) -> None:
    closure: tuple[types.CellType, ...] | None = getattr(function, "__closure__", None)
    code: types.CodeType | None = getattr(function, "__code__", None)
    if code is None or closure is None:
        return

    visitor.locals.update(
        zip(
            code.co_freevars,
            (smart_type(cell.cell_contents) for cell in closure),
            strict=True,
        )
    )


def define_types_from_signature(function: typing.Callable, visitor: ASTVisitor) -> None:
    try:
        signature = inspect.signature(function)
        visitor.locals.update(
            {param: value.annotation for param, value in signature.parameters.items()}
        )
    except ValueError:
        pass


def infer_return_type(
    function: typing.Callable, logger: "Logger", can_eval: bool
) -> typing.Any:
    try:
        source = inspect.getsource(function)
    except (TypeError, OSError):
        return None
    source = textwrap.dedent(source)
    statements = ast.parse(source).body
    if len(statements) != 1:
        # TODO: Handle this case
        return None

    body = statements[0]
    if not isinstance(body, ast.FunctionDef):
        return None

    visitor = ASTVisitor(function, logger, can_eval=can_eval)
    define_types_from_closure(function, visitor)
    define_types_from_signature(function, visitor)
    visitor.visit(body)
    if len(visitor.returns) == 0:
        return type(None)

    for rt1, rt2 in itertools.pairwise(visitor.returns):
        if rt1 != rt2:
            return typing.Any

    return visitor.returns[0]
