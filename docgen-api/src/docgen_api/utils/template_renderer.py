"""Utility functions for template rendering."""

import os
from typing import Any, Dict

import pdfkit
from jinja2 import BaseLoader, Environment, select_autoescape

from docgen_api.models.template import Template


# Get wkhtmltopdf path from environment or use default based on OS
WKHTMLTOPDF_PATH = os.getenv('WKHTMLTOPDF_PATH', {
    'win32': r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',  # Windows path
    'linux': '/usr/bin/wkhtmltopdf',  # Linux path
    'darwin': '/usr/local/bin/wkhtmltopdf'  # MacOS path
}[os.name if os.name != 'nt' else 'win32'])

# Configure pdfkit options
PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)


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
        return template.template_content, template_key, lambda: True


def create_jinja_env():
    """Create Jinja2 environment with database loader and caching.

    Returns:
        Environment: Configured Jinja2 environment
    """
    env = Environment(
        loader=DatabaseLoader(),
        autoescape=select_autoescape(['html']),
        enable_async=True,
        cache_size=100,  # Cache up to 100 templates
        auto_reload=False  # Disable auto reload since we handle it via database
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
    """Convert HTML to PDF using pdfkit.

    Args:
        html_content: HTML content to convert

    Returns:
        bytes: PDF content

    Raises:
        RuntimeError: If wkhtmltopdf is not installed or accessible
    """
    try:
        options = {
            'encoding': 'UTF-8',
            'no-outline': None,
            'quiet': ''
        }

        # Check if wkhtmltopdf exists at the configured path
        if not os.path.exists(WKHTMLTOPDF_PATH):
            raise RuntimeError(
                f"wkhtmltopdf not found at {WKHTMLTOPDF_PATH}. Please ensure wkhtmltopdf is installed."
            )

        return pdfkit.from_string(
            html_content,
            False,
            options=options,
            configuration=PDFKIT_CONFIG
        )
    except OSError as e:
        raise RuntimeError(
            f"Error executing wkhtmltopdf. Please ensure it's properly installed. Error: {str(e)}"
        ) from e
