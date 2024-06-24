SERIALIZERS_INTERFACE = """import { RelatedModelSerializer } from "./RelatedModelSerializer.ts";

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
