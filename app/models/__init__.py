# Ensure all relationships are configured
from sqlalchemy.orm import configure_mappers

from .commodity import Commodity as Commodity
from .ingestion_run import IngestionRun as IngestionRun
from .market import Market as Market
from .price_entry import PriceEntry as PriceEntry
from .supply_index import SupplyIndex as SupplyIndex

configure_mappers()
