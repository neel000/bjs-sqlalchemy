from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.sql.elements import BinaryExpression

class AsyncPaginationMixin:

    def __extract_filter(self):
        filter_query = self.queryset._whereclause
        if filter_query is None:
            return []
        
        if filter_query.__class__ == BinaryExpression:
            return (filter_query,)
        
        return filter_query.clauses
        
    async def count(self):
        model = self.queryset.column_descriptions[0]['entity']
        count_query = select(func.count()).select_from(model)
        filter = self.__extract_filter()
        count_query = count_query.filter(*filter)
        count_result = await self.session.execute(count_query)
        return count_result.scalar_one()
    
    async def get_all_data(self, limit=None, offset=None):
        query = self.queryset
        if limit:
            query = query.limit(limit)
        
        if offset:
            query = query.offset(offset)
        
        data = await self.session.execute(query)
        results = data.scalars().all()
        await self.session.close()
        return results

    async def main(self):
        if not self.limit:
            return {"results": await self.get_all_data()}
        return await self._pagination()

class LimitPageMixin:
    @staticmethod
    def _valid_limit_page(limit, page):
        limit = limit if type(limit) == int else (
            int(limit) if limit and limit.isdigit() else None
        )
        page = page if type(page) == int else (
            int(page) if page and page.isdigit() else 1
        )
        return limit, page

class LimitOffsetMixin:
    @staticmethod
    def _valid_limit_offset(limit, offset):
        limit = limit if type(limit) == int else (
            int(limit) if limit and limit.isdigit() else None
        )
        offset = offset if type(offset) == int else (
            int(offset) if offset and offset.isdigit() else 0
        )
        return limit, offset