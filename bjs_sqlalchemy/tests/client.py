import inspect
import asyncio

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
        
    print("============================PASSS=====================================")