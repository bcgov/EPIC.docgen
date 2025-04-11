"""Utility functions for template rendering."""

import os
import sys
from typing import Any, Dict

from jinja2 import BaseLoader, Environment, select_autoescape
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from docgen_api.models.template import Template


# Platform-specific setup
if sys.platform == 'win32':
    # Windows paths
    gtk_path = r'C:\Program Files\GTK3-Runtime Win64\bin'
    if os.path.exists(gtk_path) and gtk_path not in os.environ['PATH']:
        os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH']
elif sys.platform == 'darwin':
    # macOS paths
    possible_gtk_paths = [
        '/usr/local/lib',  # Homebrew default path
        '/opt/homebrew/lib',  # Apple Silicon Homebrew path
        '/usr/lib'  # System path
    ]
    for path in possible_gtk_paths:
        if os.path.exists(path):
            if path not in os.environ['PATH']:
                os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
            break
else:
    # POSIX (Linux/OpenShift) paths
    gtk_path = os.environ.get('GTK_PATH', '/usr/lib/x86_64-linux-gnu')
    if os.path.exists(gtk_path) and gtk_path not in os.environ['PATH']:
        os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH']


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
        # Configure font settings
        font_config = FontConfiguration()

        # Create HTML object with base_url to handle relative paths
        html = HTML(string=html_content)

        # Add CSS for better PDF rendering
        css = CSS(string='''
            @page {
                size: A4;
                margin: 1cm;
            }
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
            }
        ''')

        # Generate PDF with explicit configuration
        pdf_bytes = html.write_pdf(
            stylesheets=[css],
            font_config=font_config
        )
        return pdf_bytes

    except Exception as e:
        if sys.platform == 'win32':
            # Windows error handling
            gtk_path = r'C:\Program Files\GTK3-Runtime Win64\bin'
            if not os.path.exists(gtk_path):
                error_msg = (
                    f"GTK3 Runtime not found at {gtk_path}. "
                    f"Please install GTK3 Runtime from: "
                    f"https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases"
                )
            else:
                # Check for required DLLs
                required_dlls = [
                    'gobject-2.0-0.dll',
                    'glib-2.0-0.dll',
                    'cairo-2.dll',
                    'pango-1.0-0.dll',
                    'pangocairo-1.0-0.dll'
                ]
                missing_dlls = [
                    dll for dll in required_dlls
                    if not os.path.exists(os.path.join(gtk_path, dll))
                ]
                if missing_dlls:
                    error_msg = (
                        f"Missing required GTK3 DLLs: {', '.join(missing_dlls)}. "
                        f"Please reinstall GTK3 Runtime."
                    )
                else:
                    error_msg = (
                        f"Error generating PDF with WeasyPrint on Windows. "
                        f"GTK3 is installed but there might be a version mismatch. "
                        f"Error: {str(e)}"
                    )
        elif sys.platform == 'darwin':
            # macOS error handling
            possible_gtk_paths = [
                '/usr/local/lib',
                '/opt/homebrew/lib',
                '/usr/lib'
            ]
            found_path = None
            for path in possible_gtk_paths:
                if os.path.exists(path):
                    found_path = path
                    break

            if not found_path:
                error_msg = (
                    "GTK3 libraries not found. Please install GTK3 using one of these methods:\n"
                    "1. Using Homebrew: brew install gtk+3\n"
                    "2. Using MacPorts: sudo port install gtk3"
                )
            else:
                error_msg = (
                    f"Error generating PDF with WeasyPrint on macOS. "
                    f"GTK3 is installed at {found_path} but there might be an issue. "
                    f"Error: {str(e)}"
                )
        else:
            # POSIX (Linux/OpenShift) error handling
            gtk_path = os.environ.get('GTK_PATH', '/usr/lib/x86_64-linux-gnu')
            if not os.path.exists(gtk_path):
                error_msg = (
                    f"GTK3 libraries not found at {gtk_path}. "
                    f"Please ensure all WeasyPrint dependencies are installed."
                )
            else:
                error_msg = (
                    f"Error generating PDF with WeasyPrint. "
                    f"Please check WeasyPrint installation and dependencies. "
                    f"Error: {str(e)}"
                )

        raise Exception(error_msg) from e
