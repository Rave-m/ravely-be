import pandas as pd
from fastapi import FastAPI, HTTPException

from pydantic import BaseModel
from typing import List, Dict
app = FastAPI()

class DataItem(BaseModel):
    id: int
    name: str
    value: float
    
class DataResponse(BaseModel):
    data: List[DataItem]