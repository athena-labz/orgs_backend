from tortoise import Tortoise, run_async
from app.lib import environment


DATABASE = environment.get("DATABASE")

async def init():
    await Tortoise.init(
        db_url=DATABASE,
        modules={'models': ['model']}
    )

    # Generate the schema
    await Tortoise.generate_schemas()

# run_async is a helper function to run simple async Tortoise scripts.
run_async(init())