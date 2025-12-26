from sqlalchemy.orm import registry

table_registry = registry()

from .signal import Signal as Signal  # noqa E402
from .target import TargetData as TargetData  # noqa E402
