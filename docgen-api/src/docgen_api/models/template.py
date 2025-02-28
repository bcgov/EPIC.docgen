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
    template_id = Column(Integer, nullable=False, comment="The unique identifier of the template")
    template_content = Column(String, nullable=False, comment="The html template content")
    is_deleted = Column(Boolean, default=False, server_default="f", nullable=False)
    __table_args__ = (
        Index(
            "unique_non_deleted_template_id",  # Index name
            "template_id",
            unique=True,
            postgresql_where=(is_deleted is False),  # Condition for uniqueness
        ),
    )
