import os
import sys
import django
import argparse
from pathlib import Path
from django.apps import apps
from django.conf import settings
from .serializers_exporter import SerializersExporter
from .models_exporter import ModelsExporter


class TypeScriptExporter:
    def __init__(self, outdir, exclude, enable_logs, source):
        self.outdir = outdir
        self.exclude = exclude
        self.enable_logs = enable_logs
        self.source = source

    def find_django_settings_module(self):
        current_dir = os.getcwd()
        manage_py_path = os.path.join(current_dir, "manage.py")
        if not os.path.exists(manage_py_path):
            raise FileNotFoundError(
                "manage.py not found. Please run this script from the root of your Django project."
            )

        with open(manage_py_path, "r") as f:
            for line in f:
                if "os.environ.setdefault" in line and "DJANGO_SETTINGS_MODULE" in line:
                    parts = line.split(",")
                    if len(parts) > 1:
                        settings_part = parts[1].strip().strip(")")
                        settings_module = settings_part.strip().strip("'\"")
                        return settings_module

        raise RuntimeError(
            "Could not determine the Django settings module. Please ensure DJANGO_SETTINGS_MODULE is set in manage.py."
        )

    def get_local_apps(self):
        local_apps = []
        installed_apps = settings.INSTALLED_APPS
        base_dir = settings.BASE_DIR

        for app in installed_apps:
            app_path = os.path.join(base_dir, app.replace(".", "/"))
            if os.path.isdir(app_path) and app not in self.exclude:
                local_apps.append(app)
        return local_apps

    def find_project_root(self):
        current_dir = Path(__file__).resolve().parent
        while current_dir != current_dir.root:
            if (current_dir / "manage.py").exists():
                return current_dir
            current_dir = current_dir.parent
        raise RuntimeError(
            "Could not find the project root. Please ensure this script is run within a Django project."
        )

    def run(self):
        settings_module = self.find_django_settings_module()
        project_root = self.find_project_root()
        sys.path.append(str(project_root))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

        try:
            django.setup()
        except Exception as e:
            print(f"Error during django.setup(): {e}")
            raise

        local_apps = self.get_local_apps()
        if self.enable_logs:
            print(f"Local apps: {local_apps}")

        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        else:
            overwrite = (
                input(
                    f"Directory {self.outdir} already exists. Do you want to overwrite it? (yes/no): "
                )
                .strip()
                .lower()
            )
            if overwrite not in ["y", "yes"]:
                print(
                    "Operation cancelled. Use the --outdir parameter to specify a different output directory."
                )
                return

        if self.source == "serializers":
            exporter = SerializersExporter(self.outdir, local_apps, self.enable_logs)
        else:
            exporter = ModelsExporter(self.outdir, local_apps, self.enable_logs)

        exporter.export()


def main():
    parser = argparse.ArgumentParser(
        description="Export Django models and serializers to TypeScript interfaces.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-o",
        "--outdir",
        type=str,
        default="./typescript",
        help="Output directory for the TypeScript files.",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        nargs="*",
        default=[],
        help="List of apps to exclude from export.",
    )
    parser.add_argument(
        "-l", "--logs", action="store_true", help="Enable detailed logs."
    )
    parser.add_argument(
        "-s",
        "--source",
        type=str,
        choices=["serializers", "models"],
        default="serializers",
        help="Source to export: serializers or models",
    )
    parser.add_argument(
        "-v", "--version", action="version", version="django-ts-exporter 0.1.0"
    )
    args = parser.parse_args()

    exporter = TypeScriptExporter(args.outdir, args.exclude, args.logs, args.source)
    exporter.run()


if __name__ == "__main__":
    main()
