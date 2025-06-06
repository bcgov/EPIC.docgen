"""Utility functions for template rendering."""

from base64 import b64decode
from typing import Any, Dict

from jinja2 import BaseLoader, Environment, select_autoescape
from weasyprint import HTML

from docgen_api.models.template import Template


class DatabaseLoader(BaseLoader):
    """Custom loader that loads templates from database."""

    def get_source(self, environment: Environment, template_key: str) -> tuple[str, str, callable]:
        """Get template source from database.

        Args:
            environment: Jinja2 environment
            template_key: Key of the template to load

        Returns:
            tuple: (template source, template path, uptodate function)
        """
        template = Template.find_by_template_key(template_key)
        if template is None:
            raise ValueError(f'Template {template_key} not found')

        # Return source, filename, and uptodate function
        return b64decode(template.template_content).decode('utf-8'), template_key, lambda: True


def create_jinja_env():
    """Create Jinja2 environment with database loader and caching.

    Returns:
        Environment: Configured Jinja2 environment
    """
    env = Environment(
        loader=DatabaseLoader(),
        autoescape=select_autoescape(['html']),
        enable_async=True,
        cache_size=0,  # Disable caching
        auto_reload=True  # Enable auto reload to reflect changes
    )
    return env


def render_html(template_key: str, data: Dict[str, Any]) -> str:
    """Render template with data to HTML.

    Args:
        template_key: Key of the template to render
        data: Data to render template with

    Returns:
        str: Rendered HTML
    """
    env = create_jinja_env()
    template = env.get_template(template_key)
    return template.render(**data)


def render_pdf(html_content: str) -> bytes:
    """Convert HTML to PDF using WeasyPrint.

    Args:
        html_content: HTML content to convert

    Returns:
        bytes: PDF content

    Raises:
        RuntimeError: If PDF generation fails
    """
    try:
        # Create HTML object from string content
        html = HTML(string=html_content)

        # Generate PDF with minimal configuration
        pdf_bytes = html.write_pdf(
            target=None,  # Returns bytes when target is None
            zoom=1  # Default zoom factor
        )
        return pdf_bytes

    except Exception as e:
        raise e
