# -*- coding: utf-8 -*-
import json

from schematics.types import StringType
from schematics.models import Model
from jsonschema.exceptions import ValidationError as jsonschemaValidationError
from schematics.exceptions import ValidationError as schematicsValidationError


class _Flexible(Model):
    """ Save code, version and props of schema """

    _loaded = False
    _schema_source = None

    version = StringType()
    code = StringType(max_length=10)
    properties = StringType()

    def validate(self, *args, **kwargs):
        """ Try find json schema and validate it with properties """
        if not self._loaded:
            self._load_schemas()
        schema_tuple = self._schema_source.get_schema(self.code, self.version)
        if schema_tuple:
            try:
                schema_tuple.schema.validate(json.loads(self.properties))
            except jsonschemaValidationError as error:
                raise schematicsValidationError(error.message)
            else:
                self.code = schema_tuple.code
                self.version = schema_tuple.version
        super(_Flexible, self).validate(*args, **kwargs)

    def _load_schemas(self):
        """ Load schemas """
        self._schema_source.load()
        self._loaded = True


class Flexible(object):

    def __init__(self, store_handler, schema_path):
        _Flexible._schema_source = store_handler(schema_path)

    @staticmethod
    def get_module():
        return _Flexible
