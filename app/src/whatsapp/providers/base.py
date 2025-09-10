from abc import ABC, abstractmethod


class MessagingProvider(ABC):
    """Abstract provider for WhatsApp-like messaging."""

    @abstractmethod
    def send_message(self, to: str, message: str) -> None:
        pass

    @abstractmethod
    def parse_incoming(self, data: dict) -> tuple[str, str, str]:
        """Return (from_number, text, contact_name)"""
        pass
