# from bjs_sqlalchemy.filters import FilterSet

import os
command = os.system

command("python -m unittest model_test.test")
command("python -m unittest filter_pagination_test.test")
command("python -m unittest testclient_test.test")
command("python -m unittest serializers_test.test")


# from bjs_sqlalchemy.
# .model_test.test import *