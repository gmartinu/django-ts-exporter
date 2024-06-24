import os
import inspect
import importlib
from django.apps import apps
from rest_framework import serializers
from .utils import create_directory


class SerializersExporter:
    def __init__(self, outdir, apps, enable_logs):
        self.outdir = outdir
        self.apps = apps
        self.enable_logs = enable_logs
        self.any_fields_log = []

    def export(self):
        for app in self.apps:
            app_config = apps.get_app_config(app.split(".")[-1])
            serializers_module = f"{app_config.name}.serializers"

            if importlib.util.find_spec(serializers_module):
                module = importlib.import_module(serializers_module)
                self.export_serializers(module, app_config)

            serializers_path = os.path.join(app_config.path, "serializers")
            if os.path.isdir(serializers_path):
                for root, _, files in os.walk(serializers_path):
                    for file in files:
                        if file.endswith(".py") and file != "__init__.py":
                            module_name = f"{app_config.name}.serializers.{file[:-3]}"
                            module = importlib.import_module(module_name)
                            self.export_serializers(module, app_config)

        if self.enable_logs:
            self.log_any_fields()

    def export_serializers(self, module, app_config):
        app_outdir = os.path.join(self.outdir, app_config.name)
        create_directory(app_outdir)

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, serializers.ModelSerializer)
                and obj.__module__ == module.__name__
            ):
                ts_interface, imports = self.convert_serializer_to_ts_interface(
                    name, obj, app_config.name
                )
                self.write_interface(app_outdir, name, ts_interface, imports)

    def get_related_type_and_import(
        self, related_model, related_serializer, app_name, serializer_name
    ):
        if related_serializer != serializer_name:  # Avoid self-import
            if related_model._meta.app_label == app_name:
                import_path = f"./{related_serializer}.ts"
            else:
                import_path = (
                    f"../{related_model._meta.app_label}/{related_serializer}.ts"
                )
            return (
                related_serializer,
                f'import {{ {related_serializer} }} from "{import_path}";',
            )
        else:
            return related_serializer, None

    def infer_serializer_method_field_type(self, field, serializer, field_name):
        method_name = field.method_name or f"get_{field_name}"
        method = getattr(serializer, method_name, None)
        if method is None:
            return "any"  # Unable to determine type if the method is not found

        method_source = inspect.getsource(method)

        signature = inspect.signature(method)
        return_annotation = signature.return_annotation

        if return_annotation is inspect.Signature.empty:
            if "return" in method_source:
                return_statements = [
                    line.strip()
                    for line in method_source.split("\n")
                    if line.strip().startswith("return")
                ]
                if return_statements:
                    return_statement = return_statements[-1]
                    if "{" in return_statement and "}" in return_statement:
                        return "{ [key: string]: any }"  # Infer as dictionary
                    elif "[" in return_statement and "]" in return_statement:
                        return "any[]"  # Infer as list
                    elif '"' in return_statement or "'" in return_statement:
                        return "string"
                    elif return_statement.replace("return", "").strip().isdigit():
                        return "number"
                    elif "True" in return_statement or "False" in return_statement:
                        return "boolean"
                    else:
                        return "any"
            return "any"  # Default to 'any' if no type hint is provided

        if return_annotation is int:
            return "number"
        elif return_annotation is str:
            return "string"
        elif return_annotation is bool:
            return "boolean"
        elif return_annotation is float:
            return "number"
        elif return_annotation is list:
            return (
                "any[]"  # More specific type inference for lists can be added if needed
            )
        elif return_annotation is dict:
            return "{ [key: string]: any }"  # More specific type inference for dicts can be added if needed

        if isinstance(return_annotation, type):
            return return_annotation.__name__

        return "any"

    def get_ts_type(
        self, field, field_name, app_name, serializer_name, original_serializer=None
    ):
        if isinstance(field, serializers.CharField):
            return "string", None
        elif isinstance(field, serializers.IntegerField):
            return "number", None
        elif isinstance(field, serializers.BooleanField):
            return "boolean", None
        elif isinstance(field, serializers.DateTimeField):
            return "string", None  # DateTimeField can be represented as ISO 8601 string
        elif isinstance(field, serializers.DateField):
            return "string", None  # DateField can be represented as ISO 8601 string
        elif isinstance(field, serializers.DecimalField):
            return "number", None  # DecimalField can be represented as number
        elif isinstance(field, serializers.ChoiceField):
            ts_type, enum_definition = self.handle_field_with_choices(
                field, field_name, serializer_name
            )
            return ts_type, enum_definition
        elif isinstance(field, serializers.PrimaryKeyRelatedField):
            related_model = field.queryset.model
            related_serializer = related_model.__name__ + "Serializer"
            return self.get_related_type_and_import(
                related_model, related_serializer, app_name, serializer_name
            )
        elif isinstance(field, serializers.ManyRelatedField):
            related_model = field.child_relation.queryset.model
            related_serializer = related_model.__name__ + "Serializer"
            ts_type, import_statement = self.get_related_type_and_import(
                related_model, related_serializer, app_name, serializer_name
            )
            return f"{ts_type}[]", import_statement
        elif isinstance(field, serializers.FileField):
            return "File", None
        elif isinstance(field, serializers.ListSerializer):
            child_serializer = field.child
            related_serializer = child_serializer.__class__.__name__
            ts_type, import_statement = self.get_related_type_and_import(
                child_serializer.Meta.model,
                related_serializer,
                app_name,
                serializer_name,
            )
            return f"{ts_type}[]", import_statement
        elif isinstance(field, serializers.SerializerMethodField):
            inferred_type = self.infer_serializer_method_field_type(
                field, original_serializer, field_name
            )
            return inferred_type, None
        elif isinstance(field, serializers.UUIDField):
            return "string", None  # UUIDField can be represented as string
        elif isinstance(field, serializers.JSONField):
            return (
                "{ [key: string]: any }",
                None,
            )  # JSONField can be represented as dictionary
        elif issubclass(type(field), serializers.ModelSerializer):
            nested_serializer = field.__class__.__name__
            return self.get_related_type_and_import(
                field.Meta.model, nested_serializer, app_name, serializer_name
            )
        return "any", None

    def handle_field_with_choices(self, field, field_name, serializer_name):
        enum_name = f"{serializer_name}{field_name.capitalize()}Enum"
        choices = field.choices
        enum_definition = f"export enum {enum_name} {{\n"
        for value, label in choices.items():
            enum_definition += (
                f"  {label.replace(' ', '_').replace('�', 'í')} = '{value}',\n"
            )
        enum_definition += "}\n"
        return enum_name, enum_definition

    def convert_serializer_to_ts_interface(self, name, serializer, app_name):
        fields = serializer().get_fields()
        ts_fields = []
        imports = set()
        enums = set()

        for field_name, field in fields.items():
            ts_type, enum_definition = self.get_ts_type(
                field, field_name, app_name, name, original_serializer=serializer
            )
            ts_fields.append(f"{field_name}: {ts_type};")

            if ts_type == "any":
                self.any_fields_log.append(f"{app_name}.{name}.{field_name}")
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
