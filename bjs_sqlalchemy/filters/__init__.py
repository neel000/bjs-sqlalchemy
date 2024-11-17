import json

class GetField:
    @property
    def _get_common_keys(self):
        filter_keys = set(self._filter_field)
        param_keys = set(self._params.keys())
        return list(filter_keys & param_keys)

class FilterSet(GetField):

    __valid_in_operation = {
        "eq": "__eq__",
        "in": "in_",
        "not_in": "not_in",
    }

    __not_valid_in_operation = {  
        "ne": "__ne__", 
        "lt": "__lt__",
        "lte": "__le__",
        "gt": "__gt__",
        "gte": "__ge__",
        "is": "is_",
        "icontains":"like",
        "like": "like",
        "ilike": "ilike", 
        "not_like": "notlike",
        "not_ilike": "notilike",
    }

    __operation = {**__valid_in_operation, **__not_valid_in_operation}
    
    def __init__(self, params, queryset):
        self._params = params
        self._queryset = queryset
        self.__model = self.__class__.Meta.model
        self._filter_field = self.__class__.Meta.fields
    
    @staticmethod
    def _exact_query(key, model, value_list:list, op=None):
        val = value_list if len(value_list) >1 else value_list[0]
        op = op if op else "__eq__" if type(val) != list else "in_"
        attr = getattr(model, key)
        filter_func = getattr(attr, op)(val)
        return (filter_func,)
    
    @staticmethod
    def _valid_json_string(string):
        try:
            string = string.replace("'", '"')
            return json.loads(string)
        except Exception as e:
            return string
        

    def _in_constrain(self, key, model, op, value_list):
        trim_data = []

        for i in value_list:
            data_list = self._valid_json_string(i)
            
            if type(data_list) == list:
                trim_data.extend(data_list)
            else:
                trim_data.append(data_list)

        return self._exact_query(
            key=key, model=model, value_list=[trim_data], op=self.__operation[op]
        )
    
    def __non_constrain_filter(self, key, model, op, value_list):
        data = tuple()
        for i in value_list:
            value = ["%{}%".format(i)] if op == "icontains" else [i]
            data+= self._exact_query(
            key=key, model=model, value_list=value, op=self.__operation[op]
        )
        return data
    
    def _constrain_filter(self, key, model, op, value_list):
        if op == "in" or op == "not_in":
            return self._in_constrain(key, model, op, value_list)
        
        if op in self.__not_valid_in_operation.keys() and len(value_list) >1:
            return self.__non_constrain_filter(key, model, op, value_list)


        if op == "icontains":
            value_list = ["%{}%".format(value_list[0])]

        return self._exact_query(
            key=key, model=model, value_list=value_list, op=self.__operation[op]
        )

    def _advance_filter(self, key, value_list):
        join_list = key.split("__")
        constrain = join_list[-1]
        relation_fields = join_list[:-1] if not constrain in self.__operation.keys() else join_list[:-2]
        model = self.__model
        
        for i in relation_fields:
            attr = getattr(model, i)
            self._queryset = self._queryset.outerjoin(attr)
            model = attr.property.mapper.class_

        if not constrain in self.__operation.keys():
            filter_func = self._exact_query(
                key=constrain, model=model, value_list=value_list
            )
    
        else:
            filter_func = self._constrain_filter(
                key=join_list[-2], model=model, op=constrain, value_list=value_list
            )

        return filter_func

    def __filter(self):
        data = tuple()
        
        for key in self._get_common_keys:
            value_list = self._params.getlist(key)
            trim_value = [value for value in value_list if value]
            if trim_value:
                if not "__" in key:
                    filter_func = self._exact_query(
                        key=key, model=self.__model, value_list=trim_value
                    )
                else:
                    filter_func = self._advance_filter(key, value_list=trim_value)

                data += filter_func

        return data
    
    @property
    def qs(self):
        filter_data = self.__filter()
        query = self._queryset.filter(*filter_data)
        
        return query

