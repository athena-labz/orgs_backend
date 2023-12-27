# from fastapi.testclient import TestClient
# from tortoise.contrib.fastapi import register_tortoise

# from app.main import app
# from app.model import User
# from app import specs

# import pytest
# import logging
# import tortoise


# async def setup_database():
#     await tortoise.Tortoise.init(
#         db_url="sqlite://:memory:", modules={"models": ["app.model"]}
#     )
#     await tortoise.Tortoise.generate_schemas()


# async def shutdown_database():
#     await tortoise.Tortoise.close_connections()


# def setup_logging():
#     logging.basicConfig(
#         level=logging.DEBUG,
#         format="%(filename)s:%(lineno)s %(levelname)s:%(message)s",
#         force=True,
#     )


# @pytest.fixture(scope="session", autouse=True)
# async def test_client(request: pytest.FixtureRequest):
#     setup_logging()

#     await setup_database()

#     # client = TestClient(app)
#     # register_tortoise(
#     #     app, db_url="sqlite://:memory:", modules={"models": ["app.model"]}
#     # )

#     # with client as c:
#     #     yield c

#     yield

#     request.addfinalizer(await shutdown_database)

#     # await shutdown_database()

