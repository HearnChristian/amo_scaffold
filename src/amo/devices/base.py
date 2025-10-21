from typing import Any, Dict

class Device:
    """Uniform interface for all devices."""
    def connect(self) -> bool: raise NotImplementedError
    def set(self, **kwargs) -> None: raise NotImplementedError
    def get(self, what: str) -> Any: raise NotImplementedError
    def status(self) -> Dict[str, Any]: raise NotImplementedError
    def shutdown(self) -> None: pass
