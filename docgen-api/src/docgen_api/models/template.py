"""Model for template."""

from sqlalchemy import Boolean, Column, Index, Integer, String

from .base_model import BaseModel


class Template(BaseModel):
    """Template Model Class."""

    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    app = Column(
        String, nullable=False, comment="The name of the app where the template belongs"
    )
    template_key = Column(String, nullable=False,
                          comment="The unique identifier of the template")
    template_content = Column(String, nullable=False,
                              comment="The html template content")
    is_deleted = Column(Boolean, default=False,
                        server_default="f", nullable=False)
    __table_args__ = (
        Index(
            "unique_non_deleted_template_key",  # Index name
            "template_key",
            unique=True,
            postgresql_where=(is_deleted is False),  # Condition for uniqueness
        ),
    )

    @classmethod
    def find_by_template_key(cls, template_key: str):
        """Find template by template_key.

        Args:
            template_key (str): Template key to search for

        Returns:
            Template: Found template or None
        """
        return cls.query.filter_by(template_key=template_key, is_deleted=False).first()

    @classmethod
    def find_by_template_key_and_app(cls, template_key: str, app: str):
        """Find template by template_key and app.

        Args:
            template_key (str): Template key to search for
            app (str): App name to search for

        Returns:
            Template: Found template or None
        """
        return cls.query.filter_by(
            template_key=template_key,
            app=app,
            is_deleted=False
        ).first()
