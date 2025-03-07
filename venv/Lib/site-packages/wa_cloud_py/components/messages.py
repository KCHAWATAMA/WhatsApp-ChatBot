from typing import List

from pydantic import BaseModel, Field


class CatalogSection(BaseModel):
    title: str
    retailer_product_ids: list[str]

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the CatalogSection object.

        Returns:
            dict: A dictionary representation of the CatalogSection object.
        """
        return {
            "title": self.title,
            "product_items": [
                {"product_retailer_id": _id} for _id in self.retailer_product_ids
            ],
        }


class ImageHeader(BaseModel):
    url: str

    def to_dict(self) -> dict:
        return {
            "type": "image",
            "image": {"link": self.url},
        }


class ReplyButton(BaseModel):
    id: str
    title: str

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the ReplyButton object.

        Returns:
            dict: A dictionary representation of the ReplyButton object.
        """
        return {
            "type": "reply",
            "reply": {"id": self.id, "title": self.title},
        }


class SectionRow(BaseModel):
    id: str
    title: str
    description: str = Field(default="")

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the SectionRow object.

        Returns:
            dict: A dictionary representation of the SectionRow object.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
        }


class ListSection(BaseModel):
    title: str
    rows: list[SectionRow]

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the ListSection object.

        Returns:
            dict: A dictionary representation of the ListSection object.
        """
        return {
            "title": self.title,
            "rows": [row.to_dict() for row in self.rows],
        }
