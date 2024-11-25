from .db_config import AsyncDBSession
import asyncio
from sqlalchemy import func
from sqlalchemy.future import select
import unittest
from .models import (
    Users, Address
)
from bjs_sqlalchemy.filters import FilterSet
from bjs_sqlalchemy.proxy_request import ProxyRequest
from bjs_sqlalchemy import serializers
from bjs_sqlalchemy.pagination.async_pagination import (
    PageNoPagination, LimitOffSetPagination
)

class UserFilter(FilterSet):
    class Meta:
        model = Users
        fields = {
                "name",
                "address__name",
                "contact__contact_detail__id",
                "name__in", "id__not_in", "id__ne", 
                "id__gt", "id__gte", "id__lt", 
                "id__lte", "name__is", "name__icontains",
                "name__like", "name__not_like",
                "name__ilike", "name__not_ilike"
            }

class UserSerializer(serializers.Serializer):
    name:str

    class Meta:
        models = Users
    
    class Config:
        from_attributes = True

class TestClient(unittest.TestCase):
    def get_filter(self, params, query):
        filter_data = self.filter_class(params=self.proxy(params), queryset=query).qs
        return filter_data
    
    def test(self):
        func_list = [fun for fun in self.__dir__() if fun.startswith("async_")]
        for fun in func_list:
            fun = getattr(self, fun)
            asyncio.run((fun()))
        if self.__class__ != TestClient:
            print(f"{self.__class__.__name__} {len(func_list)} RUN")

class TestAsyncFilter(TestClient):
    model = Users
    proxy = ProxyRequest
    user_filter_class = UserFilter
    serializer_class = UserSerializer
    list_pagination_serializer = serializers.ListPaginationSerializer(serializer_class)

    def get_filter(self, filter_class, params, query):
        filter_data = filter_class(params=self.proxy(params), queryset=query).qs
        return filter_data
    
    async def async_test_check_session(self):
        session = await AsyncDBSession()
        count_query = select(func.count()).select_from(self.model)
        count_result = await session.execute(count_query)
        self.assertEqual(count_result.scalar_one(), 10)
        await session.close()
    
    async def async_test_blank_params(self):
        session = await AsyncDBSession()
        query = select(self.model)
        params = ""
        data = self.get_filter(self.user_filter_class, params, query)
        data = await session.execute(query)
        instance = data.scalars().all()
        assert len(instance) == 10
        await session.close()
    
    async def async_test_single_data_pass_with_serializer(self):
        session = await AsyncDBSession()
        query = select(self.model)
        params = ""
        data = self.get_filter(self.user_filter_class, params, query)
        data = await session.execute(query)
        instance = data.scalars().first()
        data = self.serializer_class(**instance.__dict__)
        self.assertEqual(data.model_dump(), {'id': 1, 'name': 'Indranil-1'})
        await session.close()

    async def async_test_list_data_pass_with_serializer(self):
        session = await AsyncDBSession()
        query = select(self.model)
        params = ""
        data = self.get_filter(self.user_filter_class, params, query)
        data = await session.execute(query)
        instance = data.scalars().all()

        serializer = serializers.ListPaginationSerializer(self.serializer_class)
        srz_data = serializer(results=instance)
        expect_data = {
            'pagination': None, 
            'results': [
                {'id': 1, 'name': 'Indranil-1'}, 
                {'id': 2, 'name': 'Indranil-2'}, 
                {'id': 3, 'name': 'Indranil-3'}, 
                {'id': 4, 'name': 'Indranil-4'}, 
                {'id': 5, 'name': 'Indranil-5'}, 
                {'id': 6, 'name': 'Indranil-6'}, 
                {'id': 7, 'name': 'Indranil-7'}, 
                {'id': 8, 'name': 'Indranil-8'}, 
                {'id': 9, 'name': 'Indranil-9'}, 
                {'id': 10, 'name': 'Indranil-10'}
                ]
            }
        self.assertEqual(srz_data.model_dump(), expect_data)
        await session.close()

    async def async_test_list_data_query_pass_with_serializer(self):
        session = await AsyncDBSession() 
        query = select(self.model)
        params = "?name=Indranil-1"
        filter_query = self.get_filter(self.user_filter_class, params, query)
        data = await session.execute(filter_query)
        instance = data.scalars().all()

        serializer = serializers.ListPaginationSerializer(self.serializer_class)
        srz_data = serializer(results=instance)
        expect_data = {
            'pagination': None, 
            'results': [
                {'id': 1, 'name': 'Indranil-1'}, 
                ]
            }
        self.assertEqual(srz_data.model_dump(), expect_data)
        await session.close()

    async def async_test_back_populate_relation(self):
        session = await AsyncDBSession() 
        query = select(self.model)
        params = "?address__name=Kolkata"
        filter_query = self.get_filter(self.user_filter_class, params, query)
        
        data = await session.execute(filter_query)
        instance = data.scalars().all()

        assert len(instance) == 1
        await session.close()


    # async def async_test_count_check(self):
    #     session = await AsyncDBSession() 
    #     query = select(self.model)
    #     params = ""
    #     filter_query = self.get_filter(self.user_filter_class, params, query)
        # filter_query = filter_query.limit(1).offset(1)

        # result = await session.execute(filter_query.with_only_columns([func.count()]))
        # count = result.scalar()
        
        # stmt = query.with_only_columns(func.count())  # Pass func.count() as a positional argument
        # result = await session.execute(stmt)
    
        # count = result.scalar()
        # print(count)


        # data = await session.execute(query)
        # instance = data.scalars().all()
        # print(instance)

        # # print(instance.name)
        # # .count()
        # # print("offset" in instance.__dir__())
        # await session.close()

    # def test(self):
    #     func_list = [fun for fun in self.__dir__() if fun.startswith("async_test")]
    #     for fun in func_list:
    #         fun = getattr(self, fun)
    #         asyncio.run((fun()))
        
    #     print(f"Testcase {len(func_list)} RUN")

class TestAsyncPageNoPagination(TestClient):
    model = Users
    proxy = ProxyRequest
    filter_class = UserFilter
    serializer_class = UserSerializer
    list_pagination_serializer = serializers.ListPaginationSerializer(serializer_class)

    
   
    async def async_test_intregration(self):
        session = await AsyncDBSession()
        params = {}
        queryset = None
        pagination = PageNoPagination(params, queryset, session=session)
        assert not pagination.limit
        assert pagination.page_no == 1
        
        params = {"limit":2}
        pagination = PageNoPagination(params, queryset, session=session)
        assert pagination.limit == 2
        assert pagination.page_no == 1
        

        params = {"limit":"2"}
        pagination = PageNoPagination(params, queryset, session=session)
        assert pagination.limit == 2
        assert pagination.page_no == 1
        await session.close()

    async def async_test_count_query_check(self):
        session = await AsyncDBSession()
        params = {}
        queryset = select(Users)
        pagination = PageNoPagination(params, queryset, session=session)
        count =  await pagination.count()
        data = await pagination.get_all_data()
        assert count == len(data)

        queryset = select(Users).filter(Users.name=="Indranil-1", Users.id==1)
        pagination = PageNoPagination(params, queryset, session=session)
        count = await pagination.count()
        count =  await pagination.count()
        data = await pagination.get_all_data()
        assert count == len(data)

        queryset = select(Users)
        pagination = PageNoPagination(params, queryset, session=session)
        count =  await pagination.count()
        data = await pagination.get_all_data(limit=1, offset=1)
        assert count != len(data)
        assert data[0].name == "Indranil-2"
        await session.close()

    async def async_test_main_function(self):
        session = await AsyncDBSession()
        params = {}
        queryset = select(Users)
        pagination = PageNoPagination(params, queryset, session=session)
        data = await pagination.main()
        assert len(data['results']) == 10
        params = {"limit":1}
        queryset = select(Users)
        pagination = PageNoPagination(params, queryset, session=session)
        data = await pagination.main()
        assert len(data['results']) == 1

    async def async_test_filter_check_no_limit(self):
        session = await AsyncDBSession()
        params = "?name__in=['Indranil-1', 'Indranil-2']"
        queryset = select(Users)
        filter_query = self.get_filter(params=params, query=queryset)
        params = {}
        pagination = PageNoPagination(params, queryset=filter_query, session=session)
        data = await pagination.main()
        assert len(data['results']) == 2
        assert 'pagination' not in data
        srz_data = self.list_pagination_serializer(**data).model_dump()
        assert not srz_data['pagination']
        assert len(srz_data['results']) == 2
        await session.close()
    
    async def async_test_filter_check_with_limit(self):
        session = await AsyncDBSession()
        params = "?name__in=['Indranil-1', 'Indranil-2']"
        queryset = select(Users)
        
        filter_query = self.get_filter(params=params, query=queryset)
        params = {"limit":1}
        pagination = PageNoPagination(params, queryset=filter_query, session=session)
        data = await pagination.main()
        
        assert len(data['results']) == 1
        assert 'pagination' in data
        srz_data = self.list_pagination_serializer(**data).model_dump()
        assert srz_data['pagination']['count'] == 2
        assert len(srz_data['results']) == 1
        await session.close()

class TestLimitOffSetPagination(TestClient):
    model = Users
    proxy = ProxyRequest
    filter_class = UserFilter
    serializer_class = UserSerializer
    list_pagination_serializer = serializers.ListPaginationSerializer(serializer_class)

    async def async_test_main_function(self):
        session = await AsyncDBSession()
        params = {}
        queryset = select(Users)
        pagination = LimitOffSetPagination(params, queryset, session=session)
        data = await pagination.main()
        assert len(data['results']) == 10
        params = {"limit":1}
        queryset = select(Users)
        pagination = PageNoPagination(params, queryset, session=session)
        data = await pagination.main()
        assert len(data['results']) == 1
    
    async def async_test_filter_serializer_with_blank_query(self):
        session = await AsyncDBSession()
        params = ""
        queryset = select(Users)
        filter_query = self.get_filter(params=params, query=queryset)

        params = {}
        pagination = LimitOffSetPagination(params, filter_query, session=session)
        data = await pagination.main()
        assert 'pagination' not in data

        srz_data = self.list_pagination_serializer(**data).model_dump()
        assert not srz_data['pagination']
        assert len(srz_data['results']) == 10

        params = {"limit":1}
        pagination = LimitOffSetPagination(params, filter_query, session=session)
        data = await pagination.main()
        assert 'pagination' in data

        srz_data = self.list_pagination_serializer(**data).model_dump()
        assert srz_data['pagination']['count'] == 10
        assert len(srz_data['results']) == 1


    async def async_test_filter_serializer_with_blank_query(self):
        session = await AsyncDBSession()
        params = "?name=Indranil-1"
        queryset = select(Users)
        filter_query = self.get_filter(params=params, query=queryset)

        params = {}
        pagination = LimitOffSetPagination(params, filter_query, session=session)
        data = await pagination.main()
        assert 'pagination' not in data

        srz_data = self.list_pagination_serializer(**data).model_dump()
        assert not srz_data['pagination']
        assert len(srz_data['results']) == 1

        params = {"limit":1}
        pagination = LimitOffSetPagination(params, filter_query, session=session)
        data = await pagination.main()
        assert 'pagination' in data

        srz_data = self.list_pagination_serializer(**data).model_dump()
        assert srz_data['pagination']['count'] == 1
        assert len(srz_data['results']) == 1

