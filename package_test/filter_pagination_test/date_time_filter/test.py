from bjs_sqlalchemy.testclient import TestClient as TS
from bjs_sqlalchemy  import models
from bjs_sqlalchemy.filters import FilterSet
from bjs_sqlalchemy.proxy_request import ProxyRequest
from datetime import datetime, UTC
from sqlalchemy import Column, DateTime

class TestClient(TS):
    database_url = "sqlite:///./filter_pagination_test/date_time_filter/database.db"
    asyn_database_url = "sqlite+aiosqlite:///./filter_pagination_test/date_time_filter/database.db"
    

class DateTimeModel(models.Model):
    __tablename__ = 'DateTimeModel'
    created_at = Column(
        DateTime, default=datetime.now(UTC)
    )

class DateTimeFilter(FilterSet):
    class Meta:
        model = DateTimeModel
        fields = {
            'id__gt', 'id__lt', 'id__gte', 'id__lte',
            'id__range'
            # 'created_at__gt'
        }


class TestDateTimeFilter(TestClient):

    def test_filter_lt_le_gt_ge(self):
        _, data = DateTimeModel().save(session=self.session)
        _, data2 = DateTimeModel().save(session=self.session)
        query = self.session.query(DateTimeModel.id)

        params = ProxyRequest('?id__lt=2')
        count = len(DateTimeFilter(params=params, queryset=query).qs.all())
        self.assertEqual(count, 1)

        params = ProxyRequest('?id__lte=0')
        count = len(DateTimeFilter(params=params, queryset=query).qs.all())
        self.assertEqual(count, 0)

        params = ProxyRequest('?id__lte=3')
        count = len(DateTimeFilter(params=params, queryset=query).qs.all())
        self.assertEqual(count, 2)

        params = ProxyRequest('?id__lt=1')
        count = len(DateTimeFilter(params=params, queryset=query).qs.all())
        self.assertEqual(count, 0)

        params = ProxyRequest('?id__lte=1')
        count = len(DateTimeFilter(params=params, queryset=query).qs.all())
        self.assertEqual(count, 1)


        params = ProxyRequest('?id__gt=0')
        count = len(DateTimeFilter(params=params, queryset=query).qs.all())
        self.assertEqual(count, 2)

        params = ProxyRequest('?id__gte=2')
        count = len(DateTimeFilter(params=params, queryset=query).qs.all())
        self.assertEqual(count, 1)

        params = ProxyRequest('?id__gt=1')
        count = len(DateTimeFilter(params=params, queryset=query).qs.all())
        self.assertEqual(count, 1)

        params = ProxyRequest('?id__gte=1')
        count = len(DateTimeFilter(params=params, queryset=query).qs.all())
        self.assertEqual(count, 2)

        params = ProxyRequest('?id__range=[3, 5]')
        count = len(DateTimeFilter(params=params, queryset=query).qs.all())
        self.assertEqual(count, 0)
        
        data.delete(session=self.session)
        data2.delete(session=self.session)