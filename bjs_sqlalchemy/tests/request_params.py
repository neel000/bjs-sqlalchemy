
class RequestParamsProxy:
    def __init__(self, params:str=""):
        self.params = params if not params.startswith("?") else params[1:]
    
    def extract_key_dict(self):
        pass

    def getlist(self, key):
        # params = 
        data = []
        params = self.params.split("&")
        for i in params:
            y = i.split("=")
            if y[0] == key:
                if y[1]:
                    data.append(y[1])

        return data
    
    def keys(self):
        data = set()
        params = self.params.split("&")

        for i in params:
            y = i.split("=")
            data.add(y[0])
        return list(data)

