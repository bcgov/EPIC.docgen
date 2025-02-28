"""Template Service."""

from docgen_api.models.template import Template


class TemplateService:
    """TemplateService."""

    @classmethod
    def create(cls, template_obj: dict):
        """Create template object."""
        template_obj: Template = Template(**template_obj)
        template_obj.save()
        return template_obj
