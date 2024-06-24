import unittest
from django.test import TestCase
from django.apps import apps
from django.conf import settings
from rest_framework import serializers
from django_ts_exporter.serializers_exporter import SerializersExporter
from tests.models import RelatedModel, TestModel

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


class SerializersExporterTestCase(TestCase):
    def test_serializer_export(self):
        exporter = SerializersExporter(
            outdir="./tests/typescript/", apps=["tests"], enable_logs=True
        )
        exporter.export()

        with open(
            "./tests/typescript/tests/TestModelSerializer.ts", "r", encoding="utf-8"
        ) as f:
            content = f.read()

        expected_content = """import { RelatedModelSerializer } from "./RelatedModelSerializer.ts";

export interface TestModelSerializer {
  id: number;
  char_field: string;
  integer_field: number;
  boolean_field: boolean;
  datetime_field: string;
  date_field: string;
  decimal_field: number;
  uuid_field: string;
  json_field: { [key: string]: any };
  file_field: File;
  foreign_key: RelatedModelSerializer;
  one_to_one: RelatedModelSerializer;
  many_to_many: RelatedModelSerializer[];
}

"""
        self.assertEqual(content.strip(), expected_content.strip())


if __name__ == "__main__":
    unittest.main()
