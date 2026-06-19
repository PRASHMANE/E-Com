from pydantic import BaseModel, ConfigDict


class AddressCreate(BaseModel):
    full_name: str
    phone_number: str
    address_line_1: str
    address_line_2: str | None = None
    city: str
    state: str
    postal_code: str
    country: str = "India"
    is_default: bool = False


class AddressUpdate(AddressCreate):
    pass


class AddressResponse(AddressCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )