"""Template Service."""

from docgen_api.models.template import Template
from docgen_api.exceptions import ResourceNotFoundError


class TemplateService:
    """TemplateService."""

    @classmethod
    def create(cls, template_obj: dict):
        """Create template object."""
        template_obj: Template = Template(**template_obj)
        template_obj.save()
        return template_obj

    @classmethod
    def update(cls, template_id: str, template_data: dict):
        """Update template content.

        Args:
            template_id (str): The ID of the template to update
            template_data (dict): Dictionary containing template_content to update

        Returns:
            Template: Updated template object

        Raises:
            ResourceNotFoundError: If template with given ID is not found
        """
        template: Template = Template.find_by_id(template_id)
        if not template:
            raise ResourceNotFoundError(
                f'Template with id {template_id} not found')

        template.template_content = template_data.get('template_content')
        template.save()
        return template

    @classmethod
    def get_by_template_id(cls, template_id: str):
        """Get template by template_id.

        Args:
            template_id (str): The ID of the template to retrieve

        Returns:
            Template: Template object if found

        Raises:
            ResourceNotFoundError: If template with given ID is not found
        """
        template = Template.find_by_id(template_id)
        if not template:
            raise ResourceNotFoundError(
                f'Template with template_id {template_id} not found')
        return template

    @classmethod
    def soft_delete(cls, template_id: str):
        """Soft delete template by template_id.

        Args:
            template_id (str): The ID of the template to delete

        Returns:
            Template: Deleted template object

        Raises:
            ResourceNotFoundError: If template with given ID is not found
        """
        template = Template.find_by_id(template_id)
        if not template:
            raise ResourceNotFoundError(
                f'Template with template_id {template_id} not found')

        template.is_active = False
        template.is_deleted = True
        template.save()
        return template
