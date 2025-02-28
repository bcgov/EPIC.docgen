"""Template Resource."""

from http import HTTPStatus

from flask_restx import Namespace, Resource

from docgen_api.auth import auth
from docgen_api.schemas import TemplateCreateSchema, TemplateSchema
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


@cors_preflight("GET, OPTIONS, POST")
@API.route("", methods=["POST", "GET", "OPTIONS"])
class Templates(Resource):
    """Template Resource."""

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Create an template")
    @API.expect(template_request_schema)
    @API.response(code=201, model=template_list_schema, description="TemplateCreated")
    @API.response(400, "Bad Request")
    def post():
        """Create a template."""
        template_data = TemplateCreateSchema().load(API.payload)
        created_template = TemplateService.create(template_data)
        return TemplateSchema().dump(created_template), HTTPStatus.CREATED
