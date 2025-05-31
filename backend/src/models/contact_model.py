from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from database import Base

if TYPE_CHECKING:
    from models.client_model import ClientDBModel

class ContactDBModel(Base):
    __tablename__ = 'contacts'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    
    # Relationship back to client
    client: Mapped["ClientDBModel"] = relationship("ClientDBModel", back_populates="contacts") 