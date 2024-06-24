import unittest
from django.test import TestCase
from django.apps import apps
from django.conf import settings
from django_ts_exporter.models_exporter import ModelsExporter

# Configure settings for the Django test environment if not already configured
if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "tests",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
    )

apps.populate(settings.INSTALLED_APPS)


class ModelsExporterTestCase(TestCase):
    def test_model_export(self):
        exporter = ModelsExporter(
            outdir="./tests/typescript/", apps=["tests"], enable_logs=True
        )
        exporter.export()

        with open("./tests/typescript/tests/TestModel.ts", "r", encoding="utf-8") as f:
            content = f.read()

        expected_content = """import { RelatedModel } from "./RelatedModel.ts";

export interface TestModel {
  id: number;
  char_field: string;
  integer_field: number;
  boolean_field: boolean;
  datetime_field: string;
  date_field: string;
  decimal_field: number;
  uuid_field: string;
  json_field: { [key: string]: any };
  foreign_key: RelatedModel;
  one_to_one: RelatedModel;
  file_field: File;
  many_to_many: RelatedModel[];
}

"""
        self.assertEqual(content.strip(), expected_content.strip())


if __name__ == "__main__":
    unittest.main()
