"""Template Resource."""

from http import HTTPStatus
from io import BytesIO

from flask import send_file, request
from flask_restx import Namespace, Resource

from docgen_api.auth import auth
from docgen_api.schemas import TemplateCreateSchema, TemplateRenderSchema, TemplateSchema, TemplateUpdateSchema
from docgen_api.services.template import TemplateService
from docgen_api.utils.util import cors_preflight

from .apihelper import Api as ApiHelper


API = Namespace("templates", description="Endpoints for Template Management")

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
@API.route("/<template_key>", methods=["GET", "PATCH", "DELETE", "OPTIONS"])
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
    @ApiHelper.swagger_decorators(API, endpoint_description="Get all templates or a specific template by key")
    @API.response(code=200, model=template_list_schema, description="Templates Retrieved")
    @API.response(404, "Template not found")
    def get(template_key=None):
        """Get templates.

        Returns:
            - All templates if no template_key provided
            - Specific template if template_key is provided
        """
        if template_key:
            template = TemplateService.get_by_template_key(template_key)
            return TemplateSchema().dump(template), HTTPStatus.OK

        templates = TemplateService.get_all_templates()
        return TemplateSchema(many=True).dump(templates), HTTPStatus.OK

    @staticmethod
    @auth.require_api_key_or_jwt
    @ApiHelper.swagger_decorators(API, endpoint_description="Update a template")
    @API.expect(template_update_schema)
    @API.response(code=200, model=template_list_schema, description="Template Updated")
    @API.response(404, "Template not found")
    @API.response(400, "Bad Request")
    def patch(template_key):
        """Update a template."""
        template_data = TemplateUpdateSchema().load(API.payload)
        updated_template = TemplateService.update(template_key, template_data)
        return TemplateSchema().dump(updated_template), HTTPStatus.OK

    @staticmethod
    @auth.require
    @ApiHelper.swagger_decorators(API, endpoint_description="Delete a template")
    @API.response(code=200, model=template_list_schema, description="Template Deleted")
    @API.response(404, "Template not found")
    def delete(template_key):
        """Delete a template."""
        deleted_template = TemplateService.soft_delete(template_key)
        return TemplateSchema().dump(deleted_template), HTTPStatus.OK


@cors_preflight("POST, OPTIONS")
@API.route("/render", methods=["POST", "OPTIONS"])
class TemplateRender(Resource):
    """Resource for rendering templates."""

    @staticmethod
    @auth.require
    @API.doc(
        params={
            "use_total_pages": {
                "description": "True to have total_pages field injected while rendering",
                "type": "boolean",
                "required": False,
            }
        }
    )
    @ApiHelper.swagger_decorators(API, endpoint_description="Render a template")
    @API.expect(ApiHelper.convert_ma_schema_to_restx_model(API, TemplateRenderSchema(), "TemplateRender"))
    @API.response(code=200, description="Template Rendered Successfully")
    @API.response(404, "Template not found")
    @API.response(400, "Bad Request")
    def post():
        """Render a template with provided data."""
        render_request = TemplateRenderSchema().load(API.payload)
        use_total_pages = request.args.get('use_total_pages', 'false').lower() == 'true'

        rendered_content = TemplateService.render_template(
            template_key=render_request['template_key'],
            app=render_request['app'],
            render_data=render_request['data'],
            output_type=render_request['output_type'],
            use_total_pages=use_total_pages
        )

        if render_request['output_type'] == 'pdf':
            # Return PDF file
            pdf_buffer = BytesIO(rendered_content)
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"{render_request['template_key']}.pdf"
            )

        # Return HTML content
        return {'html': rendered_content}, HTTPStatus.OK
