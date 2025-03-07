from pydantic import BaseModel


class Command(BaseModel):
    name: str
    description: str

    def to_dict(self):
        return {"command_name": self.name, "command_description": self.description}
