# Import all the models, so that Base clinical has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.commodity import Commodity  # noqa
from app.models.market import Market  # noqa
from app.models.price_entry import PriceEntry  # noqa
from app.models.supply_index import SupplyIndex  # noqa
