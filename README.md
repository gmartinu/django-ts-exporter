# django-ts-exporter

Export Django models and serializers to TypeScript interfaces.

This tool allows you to easily export Django models and serializers as TypeScript interfaces, enabling better type safety and integration between Django backend and TypeScript frontend applications.

## Features

- Export Django models to TypeScript interfaces.
- Export Django REST Framework serializers to TypeScript interfaces.
- Support for various Django field types.
- Generates TypeScript enums for Django model choices.
- Supports both `models` and `serializers` as the source.
- Logs any fields that cannot be determined.

## Supported Field Types

### Models

- CharField -> `string`
- IntegerField -> `number`
- BooleanField -> `boolean`
- DateTimeField -> `string` (ISO 8601)
- DateField -> `string` (ISO 8601)
- DecimalField -> `number`
- UUIDField -> `string`
- JSONField -> `{ [key: string]: any }`
- ForeignKey -> `RelatedModel`
- ManyToManyField -> `RelatedModel[]`
- OneToOneField -> `RelatedModel`
- FileField -> `File`
- Fields with choices -> `enum`

### Serializers

- CharField -> `string`
- IntegerField -> `number`
- BooleanField -> `boolean`
- DateTimeField -> `string` (ISO 8601)
- DateField -> `string` (ISO 8601)
- DecimalField -> `number`
- PrimaryKeyRelatedField -> `RelatedSerializer`
- ManyRelatedField -> `RelatedSerializer[]`
- FileField -> `File`
- ListSerializer -> `RelatedSerializer[]`
- SerializerMethodField -> inferred type or `any`
- Fields with choices -> `enum`

## Installation

```bash
pip install django-ts-exporter
```

## Usage

### Basic Usage

```bash
django-ts-exporter --outdir ./typescript --exclude info e2e --logs --source models
```

### Available Commands

```bash
django-ts-exporter --help
```

Outputs:

```text
usage: django-ts-exporter [-h] [--outdir OUTDIR] [--exclude [EXCLUDE ...]] [--logs] [--source {serializers,models}] [-v]

Export Django models and serializers to TypeScript interfaces.

optional arguments:
  -h, --help            show this help message and exit
  --outdir OUTDIR       Output directory for the TypeScript files. (default: ./typescript)
  --exclude [EXCLUDE ...]
                        List of apps to exclude from export. (default: [])
  --logs                Enable detailed logs. (default: False)
  --source {serializers,models}
                        Source to export: serializers or models (default: serializers)
  -v, --version         show program's version number and exit
```

## Example

To export TypeScript interfaces from Django serializers:

```bash
django-ts-exporter --outdir ./typescript --exclude info e2e --logs --source serializers
```

To export TypeScript interfaces from Django models:

```bash
django-ts-exporter --outdir ./typescript --exclude info e2e --logs --source models
```

## Running Tests

To run the tests, use the following command:

```bash
python -m unittest discover tests
```

## Contributing

Feel free to open issues or submit pull requests on [GitHub](https://github.com/gmartinu/django-ts-exporter).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
