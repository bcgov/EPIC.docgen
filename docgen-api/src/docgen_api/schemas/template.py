"""Schema for template."""

# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Template Schema."""


from docgen_api.models.template import Template
from .base_schema import AutoSchemaBase, BaseSchema
from marshmallow import EXCLUDE, fields, pre_load, validate


class TemplateSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Template schema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
        model = Template
        include_fk = True


class TemplateCreateSchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """Template create Schema."""

    template_key = fields.Str(
        metadata={
            "description": "Unique key of the template (only alphabets and underscores allowed)"},
        required=True,
        validate=validate.Regexp(
            r'^[A-Za-z_]+$',
            error='template_key must contain only alphabetic characters and underscores'
        )
    )
    app = fields.Str(
        metadata={
            "description": "The app name(eg: COMPLIANCE, SUBMIT, TRACK ...)"
        }
    )
    template_content = fields.Str(
        metadata={"description": "The html template"})

    @pre_load
    def format_fields(self, data, **kwargs):  # pylint: disable=unused-argument
        """Format fields before loading.

        - Capitalize app name
        - Capitalize template_key
        """
        if data.get('app'):
            data['app'] = data['app'].upper()
        if data.get('template_key'):
            data['template_key'] = data['template_key'].upper()
        return data


class TemplateUpdateSchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """Template update Schema."""

    template_content = fields.Str(
        metadata={"description": "The html template"})


class TemplateRenderSchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """Schema for template render request."""

    template_key = fields.Str(
        metadata={"description": "Key of the template to render"},
        required=True
    )
    app = fields.Str(
        metadata={"description": "App name for the template"},
        required=True
    )
    data = fields.Dict(
        metadata={"description": "Data to render the template with"},
        required=True
    )
    output_type = fields.Str(
        metadata={"description": "Type of output (pdf or html)"},
        required=True,
        validate=validate.OneOf(['pdf', 'html'])
    )

    @pre_load
    def format_fields(self, data, **kwargs):  # pylint: disable=unused-argument
        """Format fields before loading."""
        if data.get('app'):
            data['app'] = data['app'].upper()
        if data.get('template_key'):
            data['template_key'] = data['template_key'].upper()
        if data.get('output_type'):
            data['output_type'] = data['output_type'].lower()
        return data
