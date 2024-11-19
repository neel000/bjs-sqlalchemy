
from bjs_sqlalchemy.pagination.mixin import (
    AsyncPaginationMixin as PaginationMixin, 
    LimitPageMixin, LimitOffsetMixin
)

class PageNoPagination(PaginationMixin, LimitPageMixin):
    def __init__(self, params, queryset, session):
        self.queryset = queryset
        limit = params.get("limit", None)
        page = params.get("page", None)
        self.limit ,self.page_no = self._valid_limit_page(limit, page)
        self.session = session
    
    async def _pagination(self):
        pagination = {}
        pagination["count"] = await self.count()
        total_page = pagination["count"] // self.limit
        reminder = pagination["count"] % self.limit
        pagination["total_pages"] = total_page

        if reminder:
            pagination["total_pages"]+=1
        
        if not (self.page_no >= 1 and self.page_no <= pagination["total_pages"]):
            pagination["next_page"] = None
            pagination["previous_page"] = pagination["total_pages"]
            return {"results":[], "pagination":pagination}

        pagination["next_page"] = self.page_no+1 if self.page_no < pagination["total_pages"] else None
        pagination["previous_page"] = self.page_no -1 if self.page_no > 1 else None
        
        offset = (self.page_no -1) *self.limit
        
        query = await self.get_all_data(limit=self.limit, offset=offset)
        data = {"results":query, "pagination":pagination}
        return data

class LimitOffSetPagination(PaginationMixin, LimitOffsetMixin):

    def __init__(self, params, queryset, session):
        self.queryset = queryset
        limit = params.get("limit", None)
        offset = params.get("offset", None)
        self.limit ,self.offset = self._valid_limit_offset(limit, offset)
        self.session = session
    
    async def _pagination(self):
        pagination = {}
        pagination["count"] = await self.count()
        total_page = pagination["count"] // self.limit
        reminder = pagination["count"] % self.limit
        pagination["total_pages"] = total_page

        if reminder:
            pagination["total_pages"]+=1
        
        if self.offset < 0 or self.offset > pagination["count"]:
            pagination["next_offset"] = None
            pagination["previous_offset"] = pagination["count"]
            return {"pagination":pagination, "results":[]}

        next_offset = self.offset+self.limit
        pagination["next_offset"] = next_offset if next_offset < pagination["count"] else None
        previous_offset = self.offset-self.limit if self.offset > 0 else 0
        pagination["previous_offset"] = previous_offset if previous_offset>0 else None

        query = await self.get_all_data(limit=self.limit, offset=self.offset)
        return {"results":query, "pagination":pagination}

