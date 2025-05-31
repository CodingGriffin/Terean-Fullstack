from typing import TYPE_CHECKING, List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.contact_model import ContactDBModel
    from models.project_model import ProjectDBModel

class ClientDBModel(Base):
    __tablename__ = 'clients'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    
    # Relationships
    contacts: Mapped[List["ContactDBModel"]] = relationship("ContactDBModel", back_populates="client")
    project: Mapped["ProjectDBModel"] = relationship("ProjectDBModel", back_populates="client") 