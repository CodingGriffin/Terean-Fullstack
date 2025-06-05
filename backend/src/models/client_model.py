from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.contact_model import ContactDBModel
    from models.project_model import ProjectDBModel

class ClientDBModel(Base):
    __tablename__ = 'clients'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    # Relationships
    contacts: Mapped[List["ContactDBModel"]] = relationship("ContactDBModel", back_populates="client")
    projects: Mapped[List["ProjectDBModel"]] = relationship("ProjectDBModel", back_populates="client")