import uuid
from decimal import Decimal

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import CHAR, Integer, Numeric, TypeDecorator


class GUID(TypeDecorator):
    """
    Cross-dialect UUID type.

    Uses PostgreSQL's native UUID type when available and stores UUID values as
    36-character strings on other backends.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(str(value))
        return str(value if isinstance(value, uuid.UUID) else uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


class ScaledDecimal(TypeDecorator):
    """
    Decimal type that stores scaled integers on SQLite and NUMERIC elsewhere.

    SQLite does not natively preserve Decimal fidelity for SQLAlchemy Numeric
    columns, so tests use integer cents while PostgreSQL continues to use
    NUMERIC(precision, scale).
    """

    impl = Numeric
    cache_ok = True

    def __init__(self, precision: int = 10, scale: int = 2, **kwargs):
        super().__init__(**kwargs)
        self.precision = precision
        self.scale = scale
        self.multiplier = 10**scale
        self.quantizer = Decimal("1").scaleb(-scale)

    def load_dialect_impl(self, dialect):
        if dialect.name == "sqlite":
            return dialect.type_descriptor(Integer())
        return dialect.type_descriptor(Numeric(self.precision, self.scale, asdecimal=True))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
        quantized = decimal_value.quantize(self.quantizer)
        if dialect.name == "sqlite":
            return int(quantized * self.multiplier)
        return quantized

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "sqlite":
            return (Decimal(value) / Decimal(self.multiplier)).quantize(self.quantizer)
        if isinstance(value, Decimal):
            return value.quantize(self.quantizer)
        return Decimal(str(value)).quantize(self.quantizer)
