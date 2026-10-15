from prepza_common.event_models import OutboxColumns

from app.models.base import Base


class OutboxEvent(OutboxColumns, Base):
    __tablename__ = "outbox"
