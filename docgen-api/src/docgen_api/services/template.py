"""Template Service."""

from docgen_api.exceptions import ResourceExistsError, ResourceNotFoundError
from docgen_api.models.template import Template
from docgen_api.utils.template_renderer import render_html, render_pdf


class TemplateService:
    """TemplateService."""

    @classmethod
    def create(cls, template_obj: dict):
        """Create template object.

        Args:
            template_obj (dict): Dictionary containing template data

        Returns:
            Template: Created template object

        Raises:
            ResourceExistsError: If template with same template_key and app already exists
        """
        existing_template = Template.find_by_template_key_and_app(
            template_key=template_obj.get('template_key'),
            app=template_obj.get('app')
        )

        if existing_template:
            raise ResourceExistsError(
                f'Template with template_key {template_obj.get("template_key")} '
                f'and app {template_obj.get("app")} already exists'
            )

        template_obj: Template = Template(**template_obj)
        template_obj.save()
        return template_obj

    @classmethod
    def update(cls, template_key: str, template_data: dict):
        """Update template content.

        Args:
            template_key (str): The key of the template to update
            template_data (dict): Dictionary containing template_content to update

        Returns:
            Template: Updated template object

        Raises:
            ResourceNotFoundError: If template with given key is not found
        """
        template = Template.find_by_template_key(template_key)
        if not template:
            raise ResourceNotFoundError(
                f'Template with template_key {template_key} not found')

        template.template_content = template_data.get('template_content')
        template.save()
        return template

    @classmethod
    def get_by_template_key(cls, template_key: str):
        """Get template by template_key.

        Args:
            template_key (str): The key of the template to retrieve

        Returns:
            Template: Template object if found

        Raises:
            ResourceNotFoundError: If template with given key is not found
        """
        template = Template.find_by_template_key(template_key)
        if not template:
            raise ResourceNotFoundError(
                f'Template with template_key {template_key} not found')
        return template

    @classmethod
    def soft_delete(cls, template_key: str):
        """Soft delete template by template_key.

        Args:
            template_key (str): The key of the template to delete

        Returns:
            Template: Deleted template object

        Raises:
            ResourceNotFoundError: If template with given key is not found
        """
        template = Template.find_by_template_key(template_key)
        if not template:
            raise ResourceNotFoundError(
                f'Template with template_key {template_key} not found')

        template.is_active = False
        template.is_deleted = True
        template.save()
        return template

    @classmethod
    def get_all_templates(cls):
        """Get all non-deleted templates.

        Returns:
            List[Template]: List of all active templates
        """
        return Template.get_all()

    @classmethod
    def render_template(cls, template_key: str, app: str, render_data: dict, output_type: str):
        """Render a template with given data.

        Args:
            template_key (str): Key of the template to render
            app (str): App name for the template
            render_data (dict): Data to render the template with
            output_type (str): Type of output (pdf or html)

        Returns:
            Union[str, bytes]: Rendered content (str for HTML, bytes for PDF)

        Raises:
            ResourceNotFoundError: If template not found
        """
        template = Template.find_by_template_key_and_app(template_key, app)
        if not template:
            raise ResourceNotFoundError(
                f'Template with key {template_key} and app {app} not found')

        # Render HTML
        html_content = render_html(template_key, render_data)

        # Return based on output type
        if output_type == 'pdf':
            return render_pdf(html_content)
        return html_content
