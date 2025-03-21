"""Template Resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from docgen_api.auth import auth
from docgen_api.schemas import TemplateCreateSchema, TemplateSchema, TemplateUpdateSchema
from docgen_api.services.template import TemplateService
from docgen_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("agencies", description="Endpoints for Agency Management")

template_request_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, TemplateCreateSchema(), "Template"
)
template_list_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, TemplateSchema(), "TemplateList"
)
template_update_schema = ApiHelper.convert_ma_schema_to_restx_model(
    API, TemplateUpdateSchema(), "TemplateUpdate"
)


@cors_preflight("GET, OPTIONS, POST, PATCH, DELETE")
@API.route("", methods=["POST", "GET", "OPTIONS"])
@API.route("/<template_id>", methods=["GET", "PATCH", "DELETE", "OPTIONS"])
class Templates(Resource):
    """Template Resource."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Create a template")
    @API.expect(template_request_schema)
    @API.response(code=201, model=template_list_schema, description="Template Created")
    @API.response(400, "Bad Request")
    def post():
        """Create a template."""
        template_data = TemplateCreateSchema().load(API.payload)
        created_template = TemplateService.create(template_data)
        return TemplateSchema().dump(created_template), HTTPStatus.CREATED

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Get a template by ID")
    @API.response(code=200, model=template_list_schema, description="Template Retrieved")
    @API.response(404, "Template not found")
    def get(template_id=None):
        """Get a template by ID."""
        if template_id:
            template = TemplateService.get_by_template_id(template_id)
            return TemplateSchema().dump(template), HTTPStatus.OK
        # TODO: Implement get all templates endpoint
        return [], HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Update a template")
    @API.expect(template_update_schema)
    @API.response(code=200, model=template_list_schema, description="Template Updated")
    @API.response(404, "Template not found")
    @API.response(400, "Bad Request")
    def patch(template_id):
        """Update a template."""
        template_data = TemplateUpdateSchema().load(API.payload)
        updated_template = TemplateService.update(template_id, template_data)
        return TemplateSchema().dump(updated_template), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Delete a template")
    @API.response(code=200, model=template_list_schema, description="Template Deleted")
    @API.response(404, "Template not found")
    def delete(template_id):
        """Delete a template."""
        deleted_template = TemplateService.soft_delete(template_id)
        return TemplateSchema().dump(deleted_template), HTTPStatus.OK
