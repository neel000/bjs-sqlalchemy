# SQLAlchemy Filters
This package will help you to filtering your data on sqlalchemy query..

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features
    __operation = {  
        "ne": "__ne__",
        "lt": "__lt__",
        "lte": "__le__",
        "gt": "__gt__",
        "gte": "__ge__",
        "in": "in_",
        "like": "like",
        "is": "is_",
        "is_not": "not_in",
        "icontains":"like"
    }

## Usages
#Sqlalchemy Models
```bash
class ProductCategory(BaseModel):
    __tablename__ = "ProductCategory"

    name = Column(String(length=50), unique=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    sub_category = relationship("ProductSubCategory", back_populates="category")

class ProductSubCategory(BaseModel):
    __tablename__ = "ProductSubCategory"
    name = Column(String(length=50), unique=True, doc="Subcategory name")
    category_id = Column(Integer, ForeignKey("ProductCategory.id"))
    category = relationship("ProductCategory", back_populates="sub_category")
    item = relationship("Item", back_populates="sub_category")


class Item(BaseModel):
    __tablename__ = "Item"
    name = Column(String(length=50), unique=True, doc="Subcategory name")
    sub_category_id = Column(Integer, ForeignKey("ProductSubCategory.id"))
    sub_category = relationship("ProductSubCategory", back_populates="item")
```
# Sqlalchemy Filters
```bash
from sqlalchemy filters import FilterSet
from ..models import ProductCategory
from bjs_sqlalchemy.proxy_request import ProxyRequest

class ProductCategoryFilter(FilterSet):
    class Meta:
        model = ProductCategory
        fields = {
            "name" 
            "name__icontains", 
            "sub_category__name__in",
            "is_deleted":False,
            "sub_category__item__name",
            "name__is"
        }
```

# Filter Data
```bash
proxy_request = ProxyRequest("?name=Indranil")
query = session.query(ProductCategory)
filter_data = ProductCategoryFilter(params=proxy_request, queryset=query)
print(filter_data.all())
```

# python setup.py sdist bdist_wheel
## Installation
Instructions on how to install your package.

```bash
pip install bjs-sqlalchemy
```