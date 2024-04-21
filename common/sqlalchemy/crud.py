from typing import Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar('T')


async def get_or_create(session: AsyncSession, model: Type[T], defaults: dict, filter_by: dict) -> tuple[T, bool]:
    """
    Возвращает существующую запись в базе данных или создает новую, если она не найдена.

    :param session: Экземпляр асинхронной сессии SQLAlchemy.
    :param model: Класс модели, с которым будет проводиться операция.
    :param defaults: Словарь со значениями, которые будут использоваться для обновления или создания записи.
    :param filter_by: Поля и их значения, используемые для поиска существующей записи.
    :return: Объект модели, который был обновлен или создан. Был ли создан: True or False
    """
    query = select(model).filter_by(**filter_by)
    instance = await session.scalar(query)

    created = False
    if not instance:
        instance = model(**defaults)
        session.add(instance)
        created = True

    return instance, created


async def update_or_create(session: AsyncSession, model: Type[T], defaults: dict, filter_by: dict) -> tuple[T, bool]:
    """
    Обновляет существующую запись в базе данных или создает новую, если она не найдена.

    :param session: Экземпляр асинхронной сессии SQLAlchemy.
    :param model: Класс модели, с которым будет проводиться операция.
    :param defaults: Словарь со значениями, которые будут использоваться для обновления или создания записи.
    :param filter_by: Поля и их значения, используемые для поиска существующей записи.
    :return: Объект модели, который был обновлен или создан. Был ли создан: True or False
    """
    query = select(model).filter_by(**filter_by)
    instance = await session.scalar(query)

    created = False
    if instance:
        for key, value in defaults.items():
            setattr(instance, key, value)
    else:
        instance = model(**defaults)
        session.add(instance)
        created = True

    return instance, created
