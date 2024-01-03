# orgs_backend

# Overview

## Organization - DONE
* organization_edit - DONE
* join_organization - DONE
* get_organization - DONE

## Groups
* create_group
* accept_group / reject_group
* leave_group

## Wallet
* get_wallet_info
* get_group_wallet_info - only consider active members

Every user has a wallet for every organization
The "wallet" of the group is the sum of the wallets of its members

## Task
* get_task
* create_task
* approve_task_creation
* reject_task_creation
* submit_task
* require_changes_task
* succeed_task
* fail_task

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

