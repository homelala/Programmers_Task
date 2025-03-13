import copy
from typing import Optional

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin as BaseMarshmallowPlugin, OpenAPIConverter as BaseOpenAPIConverter, SchemaResolver as BaseSchemaResolver

from flask import current_app
from flask_apispec import marshal_with
from flask_apispec.apidoc import Converter as BaseApiDocConverter
from funcy import partial, memoize, project, first
from marshmallow import Schema


def _get_app_name(endpoint: str) -> Optional[str]:
    splitted = endpoint.split(".")
    if len(splitted) > 1:
        return splitted[0]
    return None


def _get_cache_key(*args, **kwargs):
    return kwargs["app_name"]

class OpenAPIConverter(BaseOpenAPIConverter):
    def schema2parameters(self, schema, *, default_in="body", name="body", required=False, description=None):
        from apispec.ext.marshmallow.openapi import __location_map__

        openapi_default_in = __location_map__.get(default_in, default_in)

        if default_in == "body":
            prop = self.resolve_nested_schema(schema)
            param = {
                "in": openapi_default_in,
                "required": required,
                "name": name,
                "schema": prop,
            }
            if description:
                param["description"] = description
            return [param]
        else:
            from apispec.ext.marshmallow.common import get_fields

            fields = get_fields(schema, exclude_dump_only=True)
            return self.fields2parameters(fields, default_in=default_in)


class ApiDocConverter(BaseApiDocConverter):
    def get_operation(self, rule, view, parent=None):
        from flask_apispec.utils import resolve_annotations, merge_recursive

        annotation = resolve_annotations(view, "docs", parent)
        docs = merge_recursive(annotation.options)
        operation = {
            "responses": self.get_responses(view, parent),
            "parameters": self.get_parameters(rule, view, docs, parent),
        }
        request_body = self.get_request_body(view, parent)
        if request_body:
            operation["requestBody"] = request_body
        docs.pop("params", None)
        return merge_recursive([operation, docs])

    def _resolve_converter(self, schema):
        from marshmallow.utils import is_instance_or_subclass

        openapi = self.marshmallow_plugin.converter

        if is_instance_or_subclass(schema, Schema):
            return openapi.schema2parameters

        if callable(schema):
            schema = schema(request=None)
            if is_instance_or_subclass(schema, Schema):
                return openapi.schema2parameters

        return openapi.fields2parameters

    def _parse_args_annotation(self, view, parent=None):
        from flask_apispec.utils import resolve_annotations

        annotation = resolve_annotations(view, "args", parent)
        args = first(annotation.options)
        if not args or "args" not in args:
            return None, None, None

        schema = args["args"]
        options = copy.copy(args.get("kwargs", {}))
        locations = options.pop("locations", [])
        return schema, options, locations

    def get_request_body(self, view, parent=None):
        schema, options, locations = self._parse_args_annotation(view, parent)
        converter = self._resolve_converter(schema)

        if schema is None:
            return None

        if not locations or not any(location in ("json", "form", "files") for location in locations):
            return None

        options["default_in"] = "body"
        params = converter(schema, **options)
        param = first(params)
        if param is None:
            return None

        result = project(param, ["description", "required"])
        result["content"] = {}

        for location in locations:
            if "json" == location:
                result["content"]["application/json"] = {"schema": param["schema"]}
            elif "form" == location:
                result["content"]["application/x-www-form-urlencoded"] = {"schema": param["schema"]}
            elif "files" == location:
                result["content"]["multipart/form-data"] = {"schema": param["schema"]}
        if not result["content"]:
            return None

        return result

    def get_parameters(self, rule, view, docs, parent=None):
        parameters = super().get_parameters(rule, view, docs)
        return [parameter for parameter in parameters if parameter["in"] != "body"]


class SchemaResolver(BaseSchemaResolver):
    def resolve_response(self, response):
        super().resolve_response(response)
        self._patch_openapi3_response(response)

    def _patch_openapi3_response(self, response):
        if "schema" in response and "content" not in response:
            schema = response.pop("schema")
            response["content"] = {"*/*": {"schema": schema}}

    def resolve_parameters(self, parameters):
        parameters = super().resolve_parameters(parameters)
        for parameter in parameters:
            self._patch_openapi3_parameter(parameter)
        return parameters

    def _patch_openapi3_parameter(self, parameter):
        if "schema" not in parameter:
            schema = {}
            for key in ("type", "default", "nullable", "format"):
                if key in parameter:
                    value = parameter.pop(key)
                    schema[key] = value
            parameter["schema"] = schema


class MarshmallowPlugin(BaseMarshmallowPlugin):
    Converter = OpenAPIConverter
    Resolver = SchemaResolver


@memoize(key_func=_get_cache_key)
def generate_api_spec(title=None, version=None, app_name=None, global_params=None) -> dict:
    from flask_apispec.paths import rule_to_path

    spec = APISpec(
        title=title,
        version=version,
        openapi_version="3.0.0",
        plugins=(MarshmallowPlugin(),),
    )

    converter = ApiDocConverter(current_app, spec)

    for endpoint, view_func in current_app.view_functions.items():
        endpoint_bp_name = _get_app_name(endpoint)
        if endpoint_bp_name != app_name:
            continue
        if hasattr(view_func, "__apispec__"):
            # noinspection PyProtectedMember
            rule = current_app.url_map._rules_by_endpoint[endpoint][0]
            spec.path(
                view=view_func,
                path=rule_to_path(rule),
                operations={method.lower(): converter.get_operation(rule, view_func, converter.get_parent(view_func)) for method in rule.methods if method not in ["OPTIONS", "HEAD"]},
                parameters=global_params,
            )
    return spec.to_dict()


marshal_empty = partial(marshal_with, Schema)
