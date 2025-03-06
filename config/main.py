from configparser import ConfigParser

parser = ConfigParser()
parser.read("config/config.ini")

# FastAPI metadata
tags_metadata = [
    {
        "name": "Quotes",
        "description": "Endpoints related to quotes"
    },
    {
        "name": "Users",
        "description": "Endpoints related to users"
    },
    {
        "name": "Roles",
        "description": "Endpoints related to roles"
    }
]