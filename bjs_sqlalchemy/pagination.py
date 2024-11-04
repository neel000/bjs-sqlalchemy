class PageNoPagination:
    def __init__(self, params, queryset):
        self.queryset = queryset
        limit = params.get("limit", None)
        page = params.get("page", None)
        self.limit ,self.page_no = self._valid_limit_page(limit, page)
    
    @staticmethod
    def _valid_limit_page(limit, page):
        limit = limit if type(limit) == int else (
            int(limit) if limit and limit.isdigit() else None
        )
        page = page if type(page) == int else (
            int(page) if page and page.isdigit() else 1
        )
        return limit, page
    
    async def __pagination(self):
        pagination = {}
        pagination["count"] = self.queryset.count()
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
        query = self.queryset.limit(self.limit).offset(offset).all()
        data = {"results":query, "pagination":pagination}
        return data

    async def main(self):
        if not self.limit:
            return {"results":self.queryset.all()}
        return await self.__pagination()

class LimitOffSetPagination:
    def __init__(self, params, queryset):
        self.queryset = queryset
        limit = params.get("limit", None)
        offset = params.get("offset", None)
        self.limit ,self.offset = self._valid_limit_offset(limit, offset)
    
    @staticmethod
    def _valid_limit_offset(limit, offset):
        limit = limit if type(limit) == int else (
            int(limit) if limit and limit.isdigit() else None
        )
        offset = offset if type(offset) == int else (
            int(offset) if offset and offset.isdigit() else 0
        )
        return limit, offset
    
    async def __pagination(self):
        pagination = {}
        pagination["count"] = self.queryset.count()
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

        query = self.queryset.limit(self.limit).offset(self.offset).all()
        return {"results":query, "pagination":pagination}

    async def main(self):
        if not self.limit:
            return {"results":self.queryset.all()}
        return await self.__pagination()
    