import os
command = os.system

command("python -m unittest model_test.test")
command("python -m unittest model_test.async_test")
command("python -m unittest filter_pagination_test.test")
command("python -m unittest filter_pagination_test.async_test")
command("python -m unittest testclient_test.test")
command("python -m unittest serializers_test.test")


