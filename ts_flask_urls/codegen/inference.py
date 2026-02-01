import ast
import inspect
import textwrap
import typing


class ASTVisitor(ast.NodeVisitor):
    def __init__(self, function: typing.Callable) -> None:
        self.function = function
        self.locals: dict[str, typing.Any] = {}
        self.returns: list = []

    def get_variable(self, name: ast.Name) -> typing.Any:
        global_var = self.function.__globals__.get(name.id, None)
        if global_var is not None:
            return global_var
        local_var = self.locals.get(name.id, None)
        return local_var

    def get_value(self, expr: ast.expr) -> typing.Any:
        match expr:
            case ast.Name():
                return self.get_variable(expr)
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

        annotations = getattr(called_function, "__annotations__", {})
        if "return" not in annotations:
            return infer_return_type(called_function)

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
            return infer_return_type(func)
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

    def resolve_return_value(self, value: ast.expr) -> typing.Any:
        match value:
            case ast.Call():
                return self.infer_call_type(value)
            case _:
                return None

    def visit_Return(self, node: ast.Return) -> None:
        if node.value is not None:
            self.returns.append(self.resolve_return_value(node.value))
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            self.locals[target.id] = self.get_value(node.value)
        self.generic_visit(node)


def infer_return_type(function: typing.Callable):
    source = inspect.getsource(function)
    source = textwrap.dedent(source)
    statements = ast.parse(source).body
    if len(statements) != 1:
        # TODO: Handle this case
        return None

    body = statements[0]
    if not isinstance(body, ast.FunctionDef):
        return None

    visitor = ASTVisitor(function)
    visitor.visit(body)
    return visitor.returns
