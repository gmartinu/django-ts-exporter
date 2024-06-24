MODELS_INTERFACE = """import { RelatedModel } from "./RelatedModel.ts";

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
