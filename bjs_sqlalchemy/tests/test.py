import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proxy_request import ProxyRequest
from models import Session, Users, Address, Contact, ContactDetail
from filters import FilterSet
from pagination import PageNoPagination, LimitOffSetPagination
from sqlalchemy.orm import joinedload
import asyncio
import inspect

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
        
class AddressFilter(FilterSet):
    class Meta:
        model = Address
        fields = {
            "user__name"
        }

class ContactDetailFilter(FilterSet):
    class Meta:
        model = ContactDetail
        fields = {
            "contact__user__name"
        }

class TestClient:
    @staticmethod
    def is_async_function(func):
        return inspect.iscoroutinefunction(func)

    def main(self):
        test_cases = [fun for fun in self.__dir__() if fun.startswith("test_")]
        print(f"{self.__class__.__name__} Test Case")
        x = 1
        for test in test_cases:
            attr = getattr(self, test)
            if self.is_async_function(attr):
                asyncio.run(attr())
                test = f"async {test}"
            else:
                attr()
            print(f"PASS-TEST-{x}, {test}")
            x+=1

class ProxyRequestTest(TestClient):
    
    def test_get_key(self):
        key = ProxyRequest(params="").keys()
        assert key == []

        key = ProxyRequest(params="?name=Indranil").keys()
        assert key == ["name"]

        key = ProxyRequest(params="?name=Indranil&name=Indranil2").keys()
        assert key == ["name"]

        key = ProxyRequest(params="?name=Indranil&name=Indranil2&age=30").keys()
        key.sort()
        result = ["name", "age"]
        result.sort()
        assert key == result

    def test_get_getlist(self):
        value_list = ProxyRequest(params="").getlist("name")
        assert value_list == []

        key = ProxyRequest(params="?name=Indranil").getlist("name")
        assert key == ["Indranil"]

        key = ProxyRequest(params="?name=Indranil&name=Indranil2").getlist("name")
        assert key == ["Indranil", "Indranil2"]

        key = ProxyRequest(params="?name=Indranil&name=Indranil2&age=30").getlist("age")
        assert key == ["30"]

class FilterTest(TestClient):
    proxy = ProxyRequest
    user_filter_class = UserFilter
    address_filter_class = AddressFilter
    
    def get_filter(self, filter_class, params, query):
        filter_data = filter_class(params=self.proxy(params), queryset=query).qs
        return filter_data
    
    def test_blank_query(self):
        session = Session()
        query = session.query(Users.name)
        params = ""
        data = self.get_filter(self.user_filter_class, params, query).all()
        assert len(data) == 10

    def test_single_equal(self):
        session = Session()
        query = session.query(Users.name)
        params = "?name=Indranil-1"
        data = self.get_filter(self.user_filter_class, params, query).all()
        assert len(data) == 1
        assert data[0][0] == "Indranil-1"
        session.close()
        
    def test_reverse_foreignkey_equal(self):
        session = Session()
        query = session.query(Users)
        params = "?address__name=Kolkata"

        users = self.get_filter(
            self.user_filter_class, params, query
            ).options(
                joinedload(Users.address)
            ).all()
        
        assert len(users) == 1
        
        for user in users:
            is_found = False
            for address in user.address:
                if address.name == "Kolkata":
                    is_found = True
                    break
            
            assert is_found

        session.close()
        
    def test_foreignkey_equal(self):
        session = Session()
        query = session.query(Address)
        params = "?user__name=Indranil-3"

        address = self.get_filter(self.address_filter_class, params, query).options(
            joinedload(Address.user)
        ).all()

        assert (len(address)==1)
        # for addres in address:
        assert (address[0].user.name == "Indranil-3")

        session.close()
        
    def test_foreignkey_to_foreignkey_equal(self):
        
        session = Session()
        query = session.query(ContactDetail).options(
            joinedload(ContactDetail.contact)
        )
        params = "?contact__user__name=Indranil-3"

        filter_data = self.get_filter(ContactDetailFilter, params=params, query=query).all()

        assert len(filter_data) == 2
        assert (filter_data[0].contact.user.name == "Indranil-3")
        assert (filter_data[1].contact.user.name == "Indranil-3")
        session.close()
    
    def test_reverse_foreignkey_to_foreignkey_equal(self):
        session = Session()
        params = "?contact__contact_detail__id=15"
        query = session.query(Users).options(
            joinedload(Users.contact).joinedload(Contact.contact_detail)
        ).options(joinedload(Users.address))
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert len(filter_data) == 1
        assert (filter_data[0].id == 3)
        session.close()

    def test_same_key_multiple_value_equal(self):
        session = Session()
        params = "?name=Indranil-1&name=Indranil-3"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert len(filter_data) == 2
        assert filter_data[0].id == 1
        assert filter_data[1].id == 3
        session.close()

    def test_no_data_after_filter(self):
        session = Session()
        query = session.query(Users)
        params = "?name=hfkfj"
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert len(filter_data) == 0
        session.close()
    
    #IN OPERATOR TEST CASE
    def test_single_in_with_double_coute(self):
        session = Session()
        query = session.query(Users)
        params = '?name__in=["Indranil-1", "Indranil-2"]'
        data = self.get_filter(self.user_filter_class, params, query).all()
        assert len(data) == 2
        assert (data[0].name == "Indranil-1")
        assert (data[1].name == "Indranil-2")
        session.close()

    def test_single_in_with_single_coute(self):
        session = Session()
        query = session.query(Users)
        params = "?name__in=['Indranil-1', 'Indranil-2']"
        data = self.get_filter(self.user_filter_class, params, query).all()
        assert len(data) == 2
        assert (data[0].name == "Indranil-1")
        assert (data[1].name == "Indranil-2")
        session.close()

    def test_single_in_invalid_format(self):
        session = Session()
        query = session.query(Users)
        params = "?name__in=[Indranil-1,    Indranil-2"
        data = self.get_filter(self.user_filter_class, params, query).all()
        assert len(data) == 0
        session.close()
    
    #Not IN CHECK
    def test_not_in_with_invalid_id(self):
        session = Session()
        id_list = [99, 999]
        params = f"id__not_in={id_list}"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert len(filter_data) == 10
        session.close()

    def test_not_in_with_all_valid_id(self):
        session = Session()
        id_list = [1,2,3]
        params = f"id__not_in={id_list}"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert len(filter_data) == 7
        for i in filter_data:
            assert (i.id not in id_list)
        session.close()
    
    def test_not_in_with_invalid_valid_id(self):
        session = Session()
        id_list = [1,2,3, 99, 89, 10]
        params = f"id__not_in={id_list}"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert len(filter_data) == 6
        for i in filter_data:
            assert (i.id not in id_list)
        session.close()

    #NE Check for Not Equal
    def test_ne_with_exist_ids(self):
        session = Session()
        params = "?id__ne=1&id__ne=2"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert len(filter_data) == 8
    
    def test_ne_with_not_exist_ids(self):
        session = Session()
        params = "?id__ne=101&id__ne=20"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert len(filter_data) == 10
        session.close()

    #GT & GTE Test
    def test_gt_with_over_greater_ids(self):
        session = Session()
        params = "?id__gt=11"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert not filter_data

    def test_gt_with_valid_greater_ids(self):
        session = Session()
        params = "?id__gt=1"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert  len(filter_data) == 9

    def test_gte_with_valid_greater_ids(self):
        session = Session()
        params = "?id__gte=1"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert  len(filter_data) == 10

    def test_gte_with_over_greater_ids(self):
        session = Session()
        params = "?id__gte=11"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert  len(filter_data) == 0
    
    #LT & LTE Test
    def test_lt_with_over_less_ids(self):
        session = Session()
        params = "?id__lt=1"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert not filter_data

    def test_lt_with_valid_less_ids(self):
        session = Session()
        params = "?id__lt=10"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert  len(filter_data) == 9

    def test_lte_with_valid_less_ids(self):
        session = Session()
        params = "?id__lte=10"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert  len(filter_data) == 10

    def test_lte_with_over_less_ids(self):
        session = Session()
        params = "?id__lte=0"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params=params, query=query).all()
        assert  len(filter_data) == 0
    
    #Is Operatior
    def test_is_with_invalid_name(self):
        session = Session()
        params = "?name__is=Indranil"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert not filter_data
        session.close()

    def test_is_with_valid_name(self):
        session = Session()
        params = "?name__is=Indranil-1"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert len(filter_data) == 1
        assert filter_data[0].name == "Indranil-1"
        session.close()
    
    #Icontains Check
    def test_icontains_matching_name(self):
        session = Session()
        params = "?name__icontains=indr"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params, query).all()
        params = "?name__icontains=ran"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert (len(filter_data) == 10)
        params = "?name__icontains=3"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert (len(filter_data) == 1)
        session.close()
    
    def test_icontains_not_matching_name(self):
        session = Session()
        params = "?name__icontains=gfhfgfhfg"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert (len(filter_data) == 0)
        session.close()
    
    #Like Check
    def test_like_matching_name(self):
        session = Session()
        query = session.query(Users)
        params = "?name__like=Indranil-1"
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert len(filter_data)==1

        params = "?name__like=Indr%"
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert len(filter_data)==10

        params = "?name__like=%nil-1"
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert len(filter_data)==1
        session.close()

    def test_like_not_matching_name(self):
        session = Session()
        query = session.query(Users)
        params = "?name__like=%nil-101"
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert len(filter_data)==0
        session.close()

    #Not Like Check
    def test_not_like_matching_name(self):
        session = Session()
        query = session.query(Users)
        params = "?name__not_like=Indranil-1"
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert len(filter_data)==9

        params = "?name__not_like=Indr%"
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert len(filter_data)==0

        params = "?name__not_like=%nil-1"
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert len(filter_data)==9
        session.close()

    def test_not_like_not_matching_name(self):
        session = Session()
        query = session.query(Users)
        params = "?name__not_like=%nil-101"
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert len(filter_data)==10
        session.close()

    #I-Like Check
    def test_ilike_matching_name(self):
        session = Session()
        query = session.query(Users)
        params = "?name__ilike=indranil-%"
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert (len(filter_data)==10)

        params = "?name__ilike=%dranil-1"
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert (len(filter_data)==1)

        params = "?name__ilike=indranil-1&name__ilike=indranil-%"
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert (len(filter_data)==1)

    def test_ilike_not_matching_name(self):
        session = Session()
        params = "?name__ilike=hjdljf-%"
        query = session.query(Users)
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert (len(filter_data)==0)

        params = "?name__ilike=indranil-1&name__ilike=indranil-2"
        filter_data = self.get_filter(UserFilter, params, query).all()
        assert (len(filter_data)==0)

class PageNoPaginationTest(TestClient):
    async def test_without_passing_limit(self):
        session = Session()
        query = session.query(Users)
        data = await PageNoPagination(params={}, queryset=query).main()
        assert len(data["results"]) == query.count()
        session.close()
    
    async def test_with_passing_limit(self):
        session = Session()
        query = session.query(Users)
        data = await PageNoPagination(params={"limit":1}, queryset=query).main()
        total = query.count()
        pagination = {
            'count': total, 'total_pages': total//1, 
            'next_page': 2, 
            'previous_page': None
        }
        
        assert data["pagination"] == pagination
        assert len(data["results"]) == 1
        session.close()

    async def test_with_passing_limit_page(self):
        session = Session()
        query = session.query(Users)
        params = {"limit":2, "page":3}
        data = await PageNoPagination(params=params, queryset=query).main()
        total = query.count()
        pagination = {
            'count': total, 
            'total_pages': total//2, 
            'next_page': params["page"]+1, 
            'previous_page': params["page"]-1
        }
        
        assert data["pagination"] == pagination
        assert len(data["results"]) == params["limit"]
        session.close()

    async def test_with_passing_limit_invalid_page(self):
        session = Session()
        query = session.query(Users)
        data = await PageNoPagination(params={"limit":2, "page":20}, queryset=query).main()
        total = query.count()
        pagination = {
            'count': total, 
            'total_pages': total//2, 
            'next_page': None, 
            'previous_page': total//2
        }
        
        assert data["pagination"] == pagination
        assert len(data["results"]) == 0
        session.close() 

class LimitOffSetPaginationTest(TestClient):
    def test_valid_limit_offset(self):
        params = {"limit":"10"}
        data = LimitOffSetPagination(params=params, queryset=None)
        assert data.limit == int(params["limit"])
        assert data.offset == 0

        params = {"limit":20}
        data = LimitOffSetPagination(params=params, queryset=None)
        assert data.limit == params["limit"]
        assert data.offset == 0

        params = {"limit":20, "offset":"20"}
        data = LimitOffSetPagination(params=params, queryset=None)
        assert data.limit == params["limit"]
        assert data.offset == int(params["limit"])

        params = {"limit":"20", "offset":"20"}
        data = LimitOffSetPagination(params=params, queryset=None)
        assert data.limit == int(params["limit"])
        assert data.offset == int(params["limit"])

    async def test_main_function_withoutpassing_limit_or_invalid_limit(self):
        session = Session()
        query = session.query(Users)
        data = await LimitOffSetPagination(params={}, queryset=query).main()
        assert len(data["results"]) == query.count()

        data = await LimitOffSetPagination(params={"limit":"opop"}, queryset=query).main()
        assert len(data["results"]) == query.count()
        session.close()
    
    async def test_main_function_with_passing_valid_limit_offset(self):
        session = Session()
        query = session.query(Users)

        data = await LimitOffSetPagination(params={"limit":5}, queryset=query).main()
        assert data["pagination"] == {'count': 10, 'total_pages': 2, 'next_offset': 5, 'previous_offset': None}
        assert len(data["results"]) == 5

        data = await LimitOffSetPagination(params={"limit":5, "offset":5}, queryset=query).main()
        assert data["pagination"] == {'count': 10, 'total_pages': 2, 'next_offset': None, 'previous_offset': None}
        assert len(data["results"]) == 5
        session.close()
    
    async def test_main_function_with_passing_invalid_limit_offset(self):
        session = Session()
        query = session.query(Users)
        
        data = await LimitOffSetPagination(params={"limit":10, "offset":100}, queryset=query).main()
        assert data["pagination"] == {'count': 10, 'total_pages': 1, 'next_offset': None, 'previous_offset': query.count()}
        assert len(data["results"]) == 0

        data = await LimitOffSetPagination(params={"limit":1, "offset":100}, queryset=query).main()
        assert data["pagination"] == {'count': 10, 'total_pages': 10, 'next_offset': None, 'previous_offset': 10}
        assert len(data["results"]) == 0
        session.close()

if __name__=="__main__":
    FilterTest().main()
    PageNoPaginationTest().main()
    LimitOffSetPaginationTest().main()
    ProxyRequestTest().main()

