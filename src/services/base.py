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
from src.utils.pagination import paginate

logger = logging.getLogger(__name__)

class BaseService(ABC):
    service_name: str
    model = None
    schema = None
    detail_schema = None
    OBJECT_CACHE_EXPIRE_IN_SECONDS = 60 * 5
    search_fields = []
    relationship_options = {}
    relationships = []
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, db: AsyncSession):
        self.redis = redis
        self.elastic = elastic
        self.db = db

    async def create_object(self, obj_sch):
        others = {}
        obj_dict = obj_sch.dict()
        for key, value in self.relationship_options.items():
            others[value['field']] = await self._set_obj_ids(obj_dict.pop(key), value['model'])
        db_obj = self.model(**obj_dict)
        for key, value in others.items():
            setattr(db_obj, key, value)
        self.db.add(db_obj)
        await self.db_commit()
        await self.db.refresh(db_obj)
        if self.detail_schema:
            return await self._get_object_from_db(db_obj.id)
        return db_obj

    async def update_object(self, obj_id: str, obj_sch):
        db_obj = await self._get_object_from_db(obj_id)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Object not found")
        for key, value in self.relationship_options.items():
            if getattr(obj_sch, key) is not None:
                setattr(db_obj, value['field'], await self._set_obj_ids(getattr(obj_sch, key), value['model']))
        await self._update_object_in_db(db_obj, obj_sch)
        await self.db.refresh(db_obj)
        if self.detail_schema:
            obj_sch = self.detail_schema.model_validate(db_obj.__dict__)
        else:
            obj_sch = self.schema.model_validate(db_obj.__dict__)
        await self._put_object_to_cache(obj_sch)
        return obj_sch

    async def _set_obj_ids(self, obj_ids, mdl):
        if obj_ids is None:
            return []
        objs = (await self.db.execute(select(mdl).filter(mdl.id.in_(obj_ids)))).scalars()

        return [obj for obj in objs]

    async def get_all(self):
        result = await self.db.execute(select(self.model))
        return result.scalars()

    async def get_all_with_pagination(self, filter_params=None):
        if filter_params is None:
            query = select(self.model)
        else:
            query = await self.get_query(filter_params)
        for relationship in self.relationships:
            query = query.options(selectinload(getattr(self.model, relationship)))
        if self.detail_schema:
            return await paginate(self.db, query, self.detail_schema)
        else:
            return await paginate(self.db, query, self.schema)

    async def get_by_id(self, obj_id: str):
        db_obj = None
        # db_obj = await self._object_from_cache(obj_id)
        if not db_obj:
            db_obj = await self._get_object_from_db(obj_id)
            if not db_obj:
                raise HTTPException(status_code=404, detail="Object not found")
            if self.detail_schema:
                db_obj = self.detail_schema.model_validate(db_obj.__dict__)
            else:
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
        for var, value in obj_sch.dict(exclude_unset=True).items():
            if var not in self.relationship_options.keys() and value is not None:
                setattr(db_obj, var, value)
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

        return query

    async def db_commit(self):
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
