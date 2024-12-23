from builtins import ValueError, any, bool, str
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid
import re

from app.utils.nickname_gen import generate_nickname
from app.utils.security import validate_password

class UserRole(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    AUTHENTICATED = "AUTHENTICATED"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

def validate_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        return url
    url_regex = r'^https?:\/\/[^\s/$.?#].[^\s]*$'
    if not re.match(url_regex, url):
        raise ValueError('Invalid URL format')
    return url

def validate_nickname(value: str) -> str:
    """
    Validate the nickname according to the rules:
    - Must start with a letter.
    - Must be 3-30 characters long.
    - Can only contain alphanumeric characters, underscores, or hyphens.
    - Uniqueness is enforced at the service layer and model
    """
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]{2,29}$", value):
        raise ValueError(
            "Nickname must start with a letter, be 3-30 characters long, and contain only alphanumeric characters, underscores, or hyphens."
        )
    return value

class UpdateBioRequest(BaseModel):
    bio: str = Field(..., max_length=500, description="The new bio for the user (max length: 500 characters).",example="Intern software developer with a bachelor degree")

class UpdateProfilePictureRequest(BaseModel):
    profile_picture_url: str = Field(..., description="The new profile picture URL.", example="https://example.com/profiles/john_new.jpg")

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    nickname: Optional[str] = Field(
        None,
        example=generate_nickname(),
        min_length=3,
        max_length=30
    )
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    bio: Optional[str] = Field(None, example="Experienced software developer specializing in web applications.")
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profiles/john.jpg")
    linkedin_profile_url: Optional[str] =Field(None, example="https://linkedin.com/in/johndoe")
    github_profile_url: Optional[str] = Field(None, example="https://github.com/johndoe")

    _validate_urls = validator('profile_picture_url', 'linkedin_profile_url', 'github_profile_url', pre=True, allow_reuse=True)(validate_url)

    @validator("nickname", pre=True, always=True)
    def validate_nickname_field(cls, value):
        if value:
            return validate_nickname(value)
        return value
 
    class Config:
        from_attributes = True

class UserCreate(UserBase):
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="Secure*1234")

    @validator("password", pre=True, always=True)
    def validate_password_field(cls, value):
        if value:
            validate_password(value)  # Raises a ValueError if invalid
        return value

class UserUpdate(UserBase):
    email: Optional[EmailStr] = Field(None, example="john.doe@example.com")
    nickname: Optional[str] = Field(
        None,
        example=generate_nickname(),
        min_length=3,
        max_length=30
    )
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    bio: Optional[str] = Field(None, example="Experienced software developer specializing in web applications.")
    profile_picture_url: Optional[str] = Field(None, example="https://example.com/profiles/john.jpg")
    linkedin_profile_url: Optional[str] =Field(None, example="https://linkedin.com/in/johndoe")
    github_profile_url: Optional[str] = Field(None, example="https://github.com/johndoe")

    @root_validator(pre=True)
    def check_at_least_one_value(cls, values):
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        return values

    @validator("nickname", pre=True, always=True)
    def validate_nickname_field(cls, value):
        if value:
            return validate_nickname(value)
        return value

class UserResponse(UserBase):
    id: uuid.UUID = Field(..., example=uuid.uuid4())
    role: UserRole = Field(default=UserRole.AUTHENTICATED, example="AUTHENTICATED")
    email: EmailStr = Field(..., example="john.doe@example.com")
    nickname: Optional[str] = Field(
        None,
        example=generate_nickname(),
        min_length=3,
        max_length=30
    )  
    role: UserRole = Field(default=UserRole.AUTHENTICATED, example="AUTHENTICATED")
    is_professional: Optional[bool] = Field(default=False, example=True)

    @validator("nickname", pre=True, always=True)
    def validate_nickname_field(cls, value):
        if value:
            return validate_nickname(value)
        return value

class LoginRequest(BaseModel):
    email: str = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="Secure*1234")

class ErrorResponse(BaseModel):
    error: str = Field(..., example="Not Found")
    details: Optional[str] = Field(None, example="The requested resource was not found.")

class UserListResponse(BaseModel):
    items: List[UserResponse] = Field(..., example=[{
        "id": uuid.uuid4(), "nickname": generate_nickname(), "email": "john.doe@example.com",
        "first_name": "John", "bio": "Experienced developer", "role": "AUTHENTICATED",
        "last_name": "Doe", "bio": "Experienced developer", "role": "AUTHENTICATED",
        "profile_picture_url": "https://example.com/profiles/john.jpg", 
        "linkedin_profile_url": "https://linkedin.com/in/johndoe", 
        "github_profile_url": "https://github.com/johndoe"
    }])
    total: int = Field(..., example=100)
    page: int = Field(..., example=1)
    size: int = Field(..., example=10)