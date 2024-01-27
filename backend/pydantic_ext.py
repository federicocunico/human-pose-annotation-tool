from typing import List
from pydantic import BaseModel as PydanticBaseModel
from typing_extensions import Annotated

import numpy as np
from pydantic import BeforeValidator, ConfigDict, PlainSerializer


def nd_array_custom_before_validator(x: List):
    # custome before validation logic
    return np.asarray(x)


def nd_array_custom_serializer(x: np.ndarray):
    # custome serialization logic
    return np.asarray(x).tolist()


NdArray = Annotated[
    np.ndarray,
    BeforeValidator(nd_array_custom_before_validator),
    PlainSerializer(nd_array_custom_serializer, return_type=List),
]


class BaseModel(PydanticBaseModel):
    # class Config:
    #     arbitrary_types_allowed = True
    model_config = ConfigDict(arbitrary_types_allowed=True)
