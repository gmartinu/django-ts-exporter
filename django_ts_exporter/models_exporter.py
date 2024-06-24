import os
import inspect
import importlib
from django.apps import apps
from django.db import models
from .utils import create_directory


class ModelsExporter:
    def __init__(self, outdir, apps, enable_logs):
        self.outdir = outdir
        self.apps = apps
        self.enable_logs = enable_logs
        self.any_fields_log = []

    def export(self):
        for app in self.apps:
            app_config = apps.get_app_config(app.split(".")[-1])
            models_module = f"{app_config.name}.models"

            if importlib.util.find_spec(models_module):
                module = importlib.import_module(models_module)
                self.export_models(module, app_config)

            models_path = os.path.join(app_config.path, "models")
            if os.path.isdir(models_path):
                for root, _, files in os.walk(models_path):
                    for file in files:
                        if file.endswith(".py") and file != "__init__.py":
                            module_name = f"{app_config.name}.models.{file[:-3]}"
                            module = importlib.import_module(module_name)
                            self.export_models(module, app_config)

        if self.enable_logs:
            self.log_any_fields()

    def export_models(self, module, app_config):
        app_outdir = os.path.join(self.outdir, app_config.name)
        create_directory(app_outdir)

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, models.Model) and obj.__module__ == module.__name__:
                ts_interface, imports = self.convert_model_to_ts_interface(
                    name, obj, app_config.name
                )
                self.write_interface(app_outdir, name, ts_interface, imports)

    def get_related_type_and_import(
        self, related_model, related_serializer, app_name, model_name
    ):
        if related_serializer != model_name:  # Avoid self-import
            related_model_name = (
                related_model
                if isinstance(related_model, str)
                else related_model.__name__
            )
            related_app_label = (
                related_model._meta.app_label
                if hasattr(related_model, "_meta")
                else app_name
            )

            if related_app_label == app_name:
                import_path = f"./{related_model_name}.ts"
            else:
                import_path = f"../{related_app_label}/{related_model_name}.ts"
            return (
                related_model_name,
                f'import {{ {related_model_name} }} from "{import_path}";',
            )
        else:
            return related_serializer, None

    def get_ts_type(self, field, field_name, app_name, model_name):
        if isinstance(field, models.CharField):
            return "string", None
        elif isinstance(field, models.IntegerField):
            return "number", None
        elif isinstance(field, models.BooleanField):
            return "boolean", None
        elif isinstance(field, models.DateTimeField):
            return "string", None  # DateTimeField can be represented as ISO 8601 string
        elif isinstance(field, models.DateField):
            return "string", None  # DateField can be represented as ISO 8601 string
        elif isinstance(field, models.DecimalField):
            return "number", None  # DecimalField can be represented as number
        elif isinstance(field, models.UUIDField):
            return "string", None  # UUIDField can be represented as string
        elif isinstance(field, models.JSONField):
            return (
                "{ [key: string]: any }",
                None,
            )  # JSONField can be represented as dictionary
        elif isinstance(field, models.ForeignKey):
            related_model = field.related_model
            related_serializer = (
                related_model
                if isinstance(related_model, str)
                else related_model.__name__
            )
            return self.get_related_type_and_import(
                related_model, related_serializer, app_name, model_name
            )
        elif isinstance(field, models.ManyToManyField):
            related_model = field.related_model
            related_serializer = (
                related_model
                if isinstance(related_model, str)
                else related_model.__name__
            )
            ts_type, import_statement = self.get_related_type_and_import(
                related_model, related_serializer, app_name, model_name
            )
            return f"{ts_type}[]", import_statement
        elif isinstance(field, models.OneToOneField):
            related_model = field.related_model
            related_serializer = (
                related_model
                if isinstance(related_model, str)
                else related_model.__name__
            )
            return self.get_related_type_and_import(
                related_model, related_serializer, app_name, model_name
            )
        elif isinstance(field, models.FileField):
            return "File", None
        return "any", None

    def handle_field_with_choices(self, field, field_name, model_name):
        enum_name = f"{model_name}{field_name.capitalize()}Enum"
        choices = field.choices
        enum_definition = f"export enum {enum_name} {{\n"
        for value, label in choices.items():
            enum_definition += (
                f"  {label.replace(' ', '_').replace('�', 'í')} = '{value}',\n"
            )
        enum_definition += "}\n"
        return enum_name, enum_definition

    def convert_model_to_ts_interface(self, name, model, app_name):
        fields = model._meta.get_fields()
        ts_fields = []
        imports = set()
        enums = set()

        for field in fields:
            if isinstance(field, models.Field):
                ts_type, enum_definition = self.get_ts_type(
                    field, field.name, app_name, name
                )
                ts_fields.append(f"{field.name}: {ts_type};")

                if ts_type == "any":
                    self.any_fields_log.append(f"{app_name}.{name}.{field.name}")
                if enum_definition:
                    if "export enum" in enum_definition:
                        enums.add(enum_definition)
                    elif enum_definition:
                        imports.add(enum_definition)

        import_statements = "\n".join(sorted(imports))
        enum_statements = "\n".join(sorted(enums))

        interface = (
            f"export interface {name} {{\n  " + "\n  ".join(ts_fields) + "\n}\n\n"
        )

        result = ""

        if import_statements:
            result = f"{import_statements}\n\n"

        if enum_statements:
            result = result + f"{enum_statements}\n\n"

        if interface:
            result = result + f"{interface}"

        return result, list(imports)

    def write_interface(self, app_outdir, name, ts_interface, imports):
        interface_path = os.path.join(app_outdir, f"{name}.ts")
        with open(interface_path, "w", encoding="utf-8") as f:
            f.write(ts_interface)

    def log_any_fields(self):
        if self.any_fields_log:
            print("\nFields with 'any' type detected:")
            for field in self.any_fields_log:
                print(field)
        else:
            print("\nNo fields with 'any' type detected.")
