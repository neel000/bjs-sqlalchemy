from bjs_sqlalchemy.filters import FilterSet
from bjs_sqlalchemy.tests.model_test.models import TestCharFieldModel

class TestCharFilter(FilterSet):
    class Meta:
        model = TestCharFieldModel
        fields = {
            "name"
        }
