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
from marshmallow import EXCLUDE, fields, pre_load, validate

from docgen_api.models.template import Template

from .base_schema import AutoSchemaBase, BaseSchema


class TemplateSchema(AutoSchemaBase):  # pylint: disable=too-many-ancestors
    """Template schema."""

    class Meta(AutoSchemaBase.Meta):  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
        model = Template
        include_fk = True


class TemplateCreateSchema(BaseSchema):  # pylint: disable=too-many-ancestors
    """Template create Schema."""

    template_id = fields.Str(
        metadata={"description": "Unique ID of the template"}, required=True
    )
    app = fields.Str(
        metadata={"description": "The app name(eg: COMPIANCE, SUBMIT, TRACK ...)"}
    )
    template_content = fields.Str(metadata={"description": "The html template"})
