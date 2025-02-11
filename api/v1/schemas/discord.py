from typing import Optional, TypedDict


class AccessResponse(TypedDict):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str

class UserObject(TypedDict):
    id: str
    username: str
    discriminator: str
    global_name: Optional[str]
    avatar: Optional[str]
    bot: bool
    system: bool
    mfa_enabled: bool
    banner: Optional[str]
    accent_color: Optional[int]
    locale: str
    verified: bool
    email: Optional[str]
    flags: int
    premium_type: int
    public_flags: int
    avatar_decoration_data: Optional["AvatarDecoration"]

class AvatarDecoration(TypedDict):
    asset: str
    sku_id: str