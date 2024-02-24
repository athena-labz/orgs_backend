# orgs_backend

## API
To run the api, run

```
$ uvicorn main:app --reload
```

## Tortoise - ORM
To initialize the database, run:
```python3
$ python3 initialize_database.py
```

To convert ORM model to pydantic, you can use

```python3
await Model_Pydantic.from_tortoise_orm(model_obj) # For single values
await Model_Pydantic.from_queryset(Model_Obj.all()) # For lists
```

