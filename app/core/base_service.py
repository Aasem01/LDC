from abc import ABC
from typing import Optional
from app.core.interfaces import IConfiguration
from app.utils.logger import Logger

class BaseService(ABC):
    """Base class for all services"""
    def __init__(self, config: IConfiguration, logger_name: str):
        self.config = config
        self.logger = Logger(logger_name)
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the service"""
        if not self._initialized:
            self._initialize()
            self._initialized = True

    def _initialize(self) -> None:
        """Service-specific initialization"""
        raise NotImplementedError("Subclasses must implement _initialize")

    def shutdown(self) -> None:
        """Shutdown the service"""
        if self._initialized:
            self._shutdown()
            self._initialized = False

    def _shutdown(self) -> None:
        """Service-specific shutdown"""
        raise NotImplementedError("Subclasses must implement _shutdown")

    @property
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized 