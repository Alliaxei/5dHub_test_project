from typing import Union
from pydantic import BaseModel,HttpUrl

class UrlRequest(BaseModel):
    """ Pydantic model for validating incoming URL requests """
    url: Union[HttpUrl, str]

    class Config:
        json_schema_extra = {
            "example" : {
                "url" : "https://example.com", # Пример url
            }
        }
