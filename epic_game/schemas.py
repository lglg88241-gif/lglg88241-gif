from pydantic import BaseModel, Field

class NewPlayer(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=20)
    password: str = Field(..., min_length=6, description="密码至少6位")
    class_id: int = Field(..., ge=1, le=3)

class GoldUpdate(BaseModel):
    add_gold: int = Field(..., gt=0)

class NewWeapon(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=50)