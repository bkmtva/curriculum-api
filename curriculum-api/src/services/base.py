from abc import ABC
from elasticsearch import AsyncElasticsearch
from fastapi import HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class BaseService(ABC):
    service_name: str
    model = None
    schema = None
    OBJECT_CACHE_EXPIRE_IN_SECONDS = 60 * 5

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, db: AsyncSession):
        self.redis = redis
        self.elastic = elastic
        self.db = db

    async def create_object(self, obj_sch):
        db_obj = self.model(**obj_sch.dict())
        self.db.add(db_obj)
        await self.db.commit()
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
        await self.db.commit()

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
        await self.db.commit()
