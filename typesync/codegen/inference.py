import ast
import builtins
import inspect
import textwrap
import types
import typing

if typing.TYPE_CHECKING:
    from .extractor import Logger


def unwrap_generics(tp, generics: dict[typing.TypeVar, typing.Any]):
    if isinstance(tp, typing.TypeVar):
        return generics.get(tp, typing.Any)

    origin = typing.get_origin(tp)
    args = typing.get_args(tp)

    if origin is None or not args:
        return tp  # Not generic

    new_args = tuple(unwrap_generics(arg, generics) for arg in args)

    if isinstance(origin, type):
        return origin[new_args] if len(new_args) > 1 else origin[new_args[0]]
    else:
        return tp.copy_with(new_args)


def get_wrapped_function(function: typing.Callable) -> typing.Callable:
    if hasattr(function, "__wrapped__"):
        return get_wrapped_function(typing.cast(typing.Callable, function.__wrapped__))
    return function


def replace_self_with(cls: type, annotation: typing.Any) -> typing.Any:
    if annotation is typing.Self:
        return cls
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)
    if origin is None or len(args) == 0:
        return annotation
    return origin[*[replace_self_with(cls, arg) for arg in args]]


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
            if isinstance(constant_value, (str, float, int, bool)):
                return typing.Literal[constant_value]
            return type(constant_value)
        except Exception:
            return None

    def get_combined_type(
        self, expressions: list[ast.expr], allow_literals: bool = True
    ) -> typing.Any:
        if len(expressions) == 0:
            return None
        if len(expressions) == 1:
            return self.get_value(expressions[0])

        most_generic_type = self.get_value(expressions[0])
        for element in expressions[1:]:
            most_generic_type = closest_common_parent_type(
                self.get_value(element),
                most_generic_type,
                allow_literals=allow_literals,
            )
            if most_generic_type is None:
                break

        return most_generic_type

    def get_list(self, list_: ast.List) -> typing.Any:
        list_type = self.get_combined_type(list_.elts, False)
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
        keys_type = self.get_combined_type(keys)
        values_type = self.get_combined_type(dict_.values)

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

    def get_argument_dict(
        self, func: typing.Callable, args: list[ast.expr], keywords: list[ast.keyword]
    ) -> dict[str, typing.Any]:
        signature = inspect.signature(func)
        bound = signature.bind(
            *[self.get_value(arg) for arg in args],
            **{str(kv.arg): self.get_value(kv.value) for kv in keywords},
        )
        bound.apply_defaults()
        return bound.arguments

    def from_func_call(
        self, func: ast.Name, fargs: list[ast.expr], fkeywords: list[ast.keyword]
    ) -> typing.Any:
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
        return_type = (
            annotations["return"]
            if "return" in annotations
            else infer_return_type(called_function, self.logger, self.can_eval)
        )

        # If there are generic parameters, try to infer them from the argument values
        if len(called_function.__type_params__) > 0:
            generics = {}
            argument_dict = self.get_argument_dict(called_function, fargs, fkeywords)
            for arg, arg_type in annotations.items():
                if arg == "return":
                    continue
                # TODO: handle things like def x[T](v: type[T]): ... where
                # T is not strictly the type of v
                if isinstance(arg_type, typing.TypeVar) and arg in argument_dict:
                    generics[arg_type] = argument_dict[arg]
            return_type = unwrap_generics(return_type, generics)

        return return_type

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

        cls = value if isinstance(value, type) else type(value)
        return replace_self_with(cls, annotations["return"])

    def infer_call_type(self, call: ast.Call) -> typing.Any:
        callable_ = call.func

        match callable_:
            case ast.Name():
                return self.from_func_call(callable_, call.args, call.keywords)
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


def closest_common_parent_type(
    type1: typing.Any, type2: typing.Any, allow_literals: bool = True
) -> typing.Any:
    if type1 == type2:
        return type1

    types = [type1, type2]
    literals = True

    # 1st case: literals are an instance of their underlying type
    for i, type_ in enumerate(types):
        if typing.get_origin(type_) is typing.Literal:
            args = typing.get_args(type_)
            if len(args) < 1:
                continue
            types[i] = type(args[0])
        else:
            literals = False

    if types[0] == types[1]:
        if literals and allow_literals:
            total_args = [*typing.get_args(type1), *typing.get_args(type2)]
            args_without_duplicates = list(set(total_args))
            if len(args_without_duplicates) > 1 and types[0] is bool:
                # Special case: typing.Literal[True, False] <=> bool
                return bool
            if len(args_without_duplicates) < 10:
                # If there are less than 10 literal types, return
                # a literal with all of those options.
                # FIXME: don't use magic number
                return typing.Literal[*args_without_duplicates]
        # Return the underlying type
        return types[0]

    # 2nd case: one is a more generic version of the same type, such as
    # dict and dict[str, int]
    origins = [typing.get_origin(type_) or type_ for type_ in types]
    if origins[0] == origins[1]:
        return origins[0]

    return None


def flatten_union(type_: typing.Any) -> list:
    return flatten_unions(typing.get_args(type_))


def flatten_unions(type_list: typing.Sequence) -> list:
    result = []
    for type_ in type_list:
        origin = typing.get_origin(type_)
        if origin in {typing.Union, types.UnionType}:
            result.extend(flatten_union(type_))
        else:
            result.append(type_)
    return result


def coalesce_types(type_list: list) -> list:
    if len(type_list) <= 1:
        return type_list

    result = type_list[:]
    i = 0
    j = 1
    while i + j < len(result):
        if result[i] != result[i + j]:
            common = closest_common_parent_type(result[i], result[i + j])
            if common is not None:
                result[i] = result[i + j] = common
                i = 0
                j = 0
        j += 1
        if i + j >= len(result):
            j = 1
            i += 1

    return list(set(result))


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

    underlying_function = get_wrapped_function(function)
    visitor = ASTVisitor(underlying_function, logger, can_eval=can_eval)
    define_types_from_closure(underlying_function, visitor)
    define_types_from_signature(underlying_function, visitor)
    visitor.visit(body)
    if len(visitor.returns) == 0:
        return type(None)

    possible_return_types = flatten_unions(visitor.returns)
    coalesced_return_types = coalesce_types(possible_return_types)

    if len(coalesced_return_types) == 1:
        return coalesced_return_types[0]

    return typing.Union[*coalesced_return_types]
