# from backend.dataset import AnnotationDataset
from backend.utility.dyn_import import load_module
from pydantic_ext import BaseModel


class Config(BaseModel):
    name: str
    data_root: str
    joints_number: int
    joints_links: list[tuple[int, int]] = []
    joints_names: list[str] = []

    dataloader_script: str
    dataloader_class: str

    def load_dataset(self) -> "AnnotationDataset":
        module = load_module(self.dataloader_script, module_name=self.name)
        cls = getattr(module, self.dataloader_class)
        return cls(self.data_root, self)
