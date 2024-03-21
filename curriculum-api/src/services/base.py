from abc import ABC
from datetime import date
import logging
from elasticsearch import AsyncElasticsearch
from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import class_mapper, RelationshipProperty, selectinload, joinedload
from fastapi import HTTPException, status
from src.utils.pagination import Pagination, paginate

logger = logging.getLogger(__name__)

class BaseService(ABC):
    service_name: str
    model = None
    schema = None
    OBJECT_CACHE_EXPIRE_IN_SECONDS = 60 * 5
    search_fields = []

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, db: AsyncSession):
        self.redis = redis
        self.elastic = elastic
        self.db = db

    async def create_object(self, obj_sch):
        db_obj = self.model(**obj_sch.dict())
        self.db.add(db_obj)
        await self.db_commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update_object(self, obj_id: str, obj_sch):
        db_obj = await self._get_object_from_db(obj_id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Object not found")
        await self._update_object_in_db(db_obj, obj_sch)
        await self.db.refresh(db_obj)
        obj_sch = self.schema.model_validate(db_obj.__dict__)
        await self._put_object_to_cache(obj_sch)
        return obj_sch

    async def get_all(self):
        result = await self.db.execute(select(self.model))
        return result.scalars()

    async def get_all_with_pagination(self, pagination: Pagination, filter_params=None):
        if filter_params is None:
            logger.debug("no no")
            return await paginate(self.db, pagination, select(self.model), self.schema)
        else:
            query = await self.get_query(filter_params)
            logger.debug("yes yes %s", query)
            print("yes yes %s", query)
            return await paginate(self.db, pagination, query, self.schema)

    async def get_by_id(self, obj_id: str):
        db_obj = await self._object_from_cache(obj_id)
        if not db_obj:
            db_obj = await self._get_object_from_db(obj_id)
            if not db_obj:
                raise HTTPException(status_code=404, detail="Object not found")
            db_obj = self.schema.model_validate(db_obj.__dict__)
            await self._put_object_to_cache(db_obj)
        return db_obj

    async def delete_by_id(self, obj_id: str) -> None:
        db_obj = await self._get_object_from_db(obj_id)
        if not db_obj:
            return None
        await self._delete_object_from_db(db_obj)
        await self._delete_object_from_cache(obj_id)
        return None

    async def _object_from_cache(self, obj_id: str):
        print('Get Object From Cache')
        data = await self.redis.get(f'{self.service_name}_{obj_id}')
        if not data:
            return None
        data = self.schema.parse_raw(data)
        return data

    async def _get_object_from_db(self, obj_id):
        return (await self.db.execute(select(self.model).filter_by(id=obj_id))).scalar()

    async def _update_object_in_db(self, db_obj, obj_sch):
        for var, value in vars(obj_sch).items():
            setattr(db_obj, var, value) if value else None
        self.db.add(db_obj)
        await self.db_commit()

    async def _put_object_to_cache(self, obj_sch):
        print('Set Object To Cache')
        await self.redis.set(
            f'{self.service_name}_{obj_sch.id}',
            obj_sch.json(),
            self.OBJECT_CACHE_EXPIRE_IN_SECONDS
        )

    async def _delete_object_from_cache(self, obj_id: str):
        await self.redis.delete(f'{self.service_name}_{obj_id}')

    async def _delete_object_from_db(self, db_obj):
        await self.db.delete(db_obj)
        await self.db_commit()

    async def get_query(self, filter_params):
        query = select(self.model)
        for i in filter_params.dict():
            param_value = getattr(filter_params, i)
            if param_value is not None:
                if i == 'search':
                    for fld in self.search_fields:
                        query = query.filter(getattr(self.model, fld).ilike(f'%{param_value}%'))
                else:
                    if isinstance(param_value, date):
                        query = query.filter(func.date(getattr(self.model, i)) == param_value)
                    elif isinstance(param_value, bool):
                        query = query.filter(getattr(self.model, i) == bool(param_value))

                    else:
                        query = query.filter(getattr(self.model, i) == str(param_value))
        relationships = class_mapper(self.model).relationships.keys()

        for relationship in relationships:
            query = query.options(selectinload(getattr(self.model, relationship)))

        return query

    async def db_commit(self):
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
