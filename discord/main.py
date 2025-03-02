from configparser import ConfigParser
from typing import Optional, TypedDict

import jwt
import requests


class DiscordOAuthHandler:
    def __init__(self):
        parser = ConfigParser()
        parser.read("config.ini")
        self.__client_id = parser.get("Discord", "client_id")
        self.__client_secret = parser.get("Discord", "client_secret")
        self.__redirect_uri = parser.get("Discord", "redirect_uri")
        self.__key = parser.get("JWT", "key")

        self.discord_api_endpoint = "https://discord.com/api/v10"

    def receive_access_response(
        self,
        code: str,
    ) -> "AccessResponse":
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.__redirect_uri,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(
            f"{self.discord_api_endpoint}/oauth2/token",
            data=data,
            headers=headers,
            auth=(self.__client_id, self.__client_secret)
        )
        return response.json()

    def receive_user_information(self, access_token: str) -> "UserObject":
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            f"{self.discord_api_endpoint}/users/@me",
            headers=headers
        )
        return response.json()

    def decode_token(self, token: str):
        access_response: AccessResponse = jwt.decode(token, self.__key, algorithms=["HS256"])
        return access_response


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
