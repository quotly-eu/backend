from pydantic import BaseModel

class BaseModel(BaseModel):
  class Config:
    populate_by_name = True