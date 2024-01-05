from app.lib import environment


database_connection = environment.get("DATABASE")
TORTOISE_ORM = {
    "connections": {"default": database_connection},
    "apps": {
        "models": {
            "models": ["app.model", "aerich.models"],
            "default_connection": "default",
        },
    },
}