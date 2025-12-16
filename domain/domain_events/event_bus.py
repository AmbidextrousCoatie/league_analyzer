"""
Domain Event Bus

Simple in-memory event bus for domain events.
In production, this could be replaced with a message queue.
"""

from typing import Callable, TypeVar, Type
from collections import defaultdict
import logging

from domain.domain_events.domain_event import DomainEvent

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=DomainEvent)


class DomainEventBus:
    """
    Simple event bus for domain events.
    
    Handlers are registered per event type and called synchronously
    when events are published.
    """
    
    _handlers: dict[Type[DomainEvent], list[Callable[[DomainEvent], None]]] = defaultdict(list)
    
    @classmethod
    def subscribe(cls, event_type: Type[T], handler: Callable[[T], None]) -> None:
        """
        Subscribe a handler to an event type.
        
        Args:
            event_type: The type of event to subscribe to
            handler: Callable that takes an event and returns None
        """
        cls._handlers[event_type].append(handler)
        logger.debug(f"Subscribed handler to {event_type.__name__}")
    
    @classmethod
    def publish(cls, event: DomainEvent) -> None:
        """
        Publish a domain event to all subscribed handlers.
        
        Args:
            event: The domain event to publish
        """
        event_type = type(event)
        handlers = cls._handlers.get(event_type, [])
        
        logger.debug(f"Publishing {event_type.__name__} to {len(handlers)} handler(s)")
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    f"Error handling {event_type.__name__} in handler {handler.__name__}: {e}",
                    exc_info=True
                )
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered handlers (useful for testing)."""
        cls._handlers.clear()
        logger.debug("Event bus cleared")

