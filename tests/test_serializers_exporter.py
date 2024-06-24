import unittest
from django.test import TestCase
from django.apps import apps
from django.conf import settings
from django_ts_exporter.serializers_exporter import SerializersExporter
from constants.serializers_exporter import SERIALIZERS_INTERFACE

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

        expected_content = SERIALIZERS_INTERFACE

        self.assertEqual(content.strip(), expected_content.strip())


if __name__ == "__main__":
    unittest.main()
