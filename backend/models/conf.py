# from backend.dataset import AnnotationDataset
from typing import List, Tuple
from backend.utility.dyn_import import load_module
from pydantic_ext import BaseModel


class Config(BaseModel):
    name: str
    data_root: str
    joints_number: int
    joints_links: List[Tuple[int, int]] = []
    joints_names: List[str] = []

    dataloader_script: str
    dataloader_class: str

    def __init__(self, **data):
        if "joints_names" in data:
            data["joints_names"] = [str(j) for j in data["joints_names"]]
        super().__init__(**data)

    def load_dataset(self) -> "AnnotationDataset":
        module = load_module(self.dataloader_script, module_name=self.name)
        cls = getattr(module, self.dataloader_class)
        return cls(self.data_root, self)
