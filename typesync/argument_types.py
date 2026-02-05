import hashlib
import importlib.util
import pathlib
import sys
import types

from click import ParamType

from .type_translators import Translator


class PythonModuleParamType(ParamType):
    name = "python_module"

    def convert(self, value, param, ctx) -> types.ModuleType:
        if isinstance(value, types.ModuleType):
            return value

        if not isinstance(value, str):
            self.fail(f"{value!r} is not a valid value", param, ctx)

        path = pathlib.Path(value).resolve()

        if not path.exists:
            self.fail(f"file {value!r} does not exist", param, ctx)

        if not path.is_file():
            self.fail(f"{value!r} is not a file", param, ctx)

        mod_name = f"module_{hashlib.sha256(str(path).encode()).hexdigest()[:16]}"
        spec = importlib.util.spec_from_file_location(mod_name, str(path))
        if spec is None or spec.loader is None:
            self.fail(f"{value!r} is not a valid python module", param, ctx)

        try:
            module = importlib.util.module_from_spec(spec)
        except ModuleNotFoundError:
            self.fail(f"{value!r} is not a valid python module", param, ctx)

        sys.modules[mod_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            del sys.modules[mod_name]
            self.fail(f"could not load module at {value!r} ({e})", param, ctx)

        return module


class TranslatorPluginParamType(PythonModuleParamType):
    def convert(self, value, param, ctx) -> type[Translator]:
        module = super().convert(value, param, ctx)

        translator_func = getattr(module, "translator", None)
        if translator_func is None:
            self.fail(
                f"{value!r} must define a function 'translator() -> type[Translator]'",
                param,
                ctx,
            )
        try:
            translator = translator_func()
        except Exception as e:
            self.fail(
                f"failed to run the 'translator()' function defined by {value!r} ({e})",
                param,
                ctx,
            )

        if not issubclass(translator, Translator):
            self.fail(
                f"'translator()' function defined by {value!r} must return a class "
                "that inherits from typesync.type_translators.Translator",
                param,
                ctx,
            )

        return translator


class TranslatorPriorityParamType(ParamType):
    def convert(self, value, param, ctx) -> tuple[str, int]:
        if isinstance(value, tuple):
            return value

        if not isinstance(value, str):
            self.fail(f"{value!r} is not a valid value", param, ctx)

        id_and_priority = value.rsplit(":", 1)
        if len(id_and_priority) != 2:
            self.fail(f"must be of the form ID:PRIORITY (was {value!r})", param, ctx)

        id_, priority_str = id_and_priority
        try:
            priority = int(priority_str)
        except ValueError:
            self.fail(
                f"priority {priority_str!r} cannot be converted to an int", param, ctx
            )

        return id_, priority


PYTHON_MODULE = PythonModuleParamType()
TRANSLATOR_PLUGIN = TranslatorPluginParamType()
TRANSLATOR_PRIORITY = TranslatorPriorityParamType()
