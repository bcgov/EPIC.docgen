"""Utility functions for template rendering."""

import os
import sys
from typing import Any, Dict

from jinja2 import BaseLoader, Environment, select_autoescape
from weasyprint import HTML

from docgen_api.models.template import Template


# # Platform-specific setup
# if sys.platform == 'win32':
#     # Windows paths - check both GTK3 Runtime and MSYS2 pacman
#     gtk_paths = [
#         r'C:\Program Files\GTK3-Runtime Win64\bin',
#         r'C:\msys64\mingw64\bin'
#     ]
#     for gtk_path in gtk_paths:
#         if os.path.exists(gtk_path) and gtk_path not in os.environ['PATH']:
#             os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH']
# elif sys.platform == 'darwin':
#     # macOS paths
#     possible_gtk_paths = [
#         '/usr/local/lib',  # Homebrew default path
#         '/opt/homebrew/lib',  # Apple Silicon Homebrew path
#         '/usr/lib'  # System path
#     ]
#     for path in possible_gtk_paths:
#         if os.path.exists(path):
#             if path not in os.environ['PATH']:
#                 os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
#             break
# else:
#     # POSIX (Linux/OpenShift) paths
#     gtk_path = os.environ.get('GTK_PATH', '/usr/lib/x86_64-linux-gnu')
#     if os.path.exists(gtk_path) and gtk_path not in os.environ['PATH']:
#         os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH']


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
