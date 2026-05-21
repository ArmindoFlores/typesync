import hashlib
import importlib.util
import pathlib
import sys
import types

from click import ParamType

from .type_translators import Translator
from .codegen import RouteTypeExtractor


class PythonModuleParamType(ParamType):
    name = "python_module"

    def convert(self, value, param, ctx) -> types.ModuleType:
        if isinstance(value, types.ModuleType):
            return value

        if not isinstance(value, str):
            return self.fail(f"{value!r} is not a valid value", param, ctx)

        path = pathlib.Path(value).resolve()

        if not path.exists():
            return self.fail(f"file {value!r} does not exist", param, ctx)

        if not path.is_file():
            return self.fail(f"{value!r} is not a file", param, ctx)

        mod_name = f"module_{hashlib.sha256(str(path).encode()).hexdigest()[:16]}"
        spec = importlib.util.spec_from_file_location(mod_name, str(path))
        if spec is None or spec.loader is None:
            return self.fail(f"{value!r} is not a valid python module", param, ctx)

        try:
            module = importlib.util.module_from_spec(spec)
        except ModuleNotFoundError:
            return self.fail(f"{value!r} is not a valid python module", param, ctx)

        sys.modules[mod_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            del sys.modules[mod_name]
            return self.fail(f"could not load module at {value!r} ({e})", param, ctx)

        return module


class TranslatorPluginParamType(ParamType):
    name = "translator_plugin"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.python_module_plugin_param_type = PythonModuleParamType()

    def convert(self, value, param, ctx) -> type[Translator]:
        if isinstance(value, str):
            translators = RouteTypeExtractor.all_translators()
            for translator in translators:
                if value == translator.ID:
                    return translator

        module = self.python_module_plugin_param_type.convert(value, param, ctx)

        translator_func = getattr(module, "translator", None)
        if translator_func is None:
            return self.fail(
                f"{value!r} must define a function 'translator() -> type[Translator]'",
                param,
                ctx,
            )
        try:
            translator = translator_func()
        except Exception as e:
            return self.fail(
                f"failed to run the 'translator()' function defined by {value!r} ({e})",
                param,
                ctx,
            )

        if not issubclass(translator, Translator):
            return self.fail(
                f"'translator()' function defined by {value!r} must return a class "
                "that inherits from typesync.type_translators.Translator",
                param,
                ctx,
            )

        return translator


class TranslatorPriorityParamType(ParamType):
    name = "translator_priority"

    def convert(self, value, param, ctx) -> tuple[str, int]:
        if isinstance(value, tuple):
            return value

        if not isinstance(value, str):
            return self.fail(f"{value!r} is not a valid value", param, ctx)

        id_and_priority = value.rsplit(":", 1)
        if len(id_and_priority) != 2:
            return self.fail(
                f"must be of the form ID:PRIORITY (was {value!r})", param, ctx
            )

        id_, priority_str = id_and_priority
        try:
            priority = int(priority_str)
        except ValueError:
            return self.fail(
                f"priority {priority_str!r} cannot be converted to an int", param, ctx
            )

        return id_, priority


PYTHON_MODULE = PythonModuleParamType()
TRANSLATOR_PLUGIN = TranslatorPluginParamType()
TRANSLATOR_PRIORITY = TranslatorPriorityParamType()
