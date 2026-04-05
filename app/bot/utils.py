"""
Утилиты для Telegram-бота
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar, Any
from functools import wraps

# Создаём пул потоков для выполнения синхронных операций
executor = ThreadPoolExecutor(max_workers=10)

T = TypeVar('T')


async def run_sync(func: Callable[..., T], *args: Any, timeout: float = 10.0, **kwargs: Any) -> T:
    """
    Выполняет синхронную функцию в отдельном потоке, не блокируя event loop.
    
    Args:
        func: Синхронная функция для выполнения
        *args: Позиционные аргументы функции
        timeout: Максимальное время выполнения в секундах (по умолчанию 10)
        **kwargs: Именованные аргументы функции
    
    Returns:
        Результат выполнения функции
    
    Raises:
        asyncio.TimeoutError: Если операция превысила timeout
    """
    loop = asyncio.get_event_loop()
    
    # Выполняем синхронную функцию в ThreadPoolExecutor
    future = loop.run_in_executor(executor, lambda: func(*args, **kwargs))
    
    # Применяем таймаут
    try:
        result = await asyncio.wait_for(future, timeout=timeout)
        return result
    except asyncio.TimeoutError:
        raise asyncio.TimeoutError(f"Операция превысила лимит времени {timeout}с")
