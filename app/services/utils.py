import logging
import uuid
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer

import jwt
from werkzeug.security import check_password_hash, generate_password_hash


from core.config import auth_settings


ACCESS_TOKEN_EXPIRY = 3600


def generate_passwd_hash(password: str) -> str:
    hash = generate_password_hash(password)

    return hash


def verify_password(password: str, hash: str) -> bool:
    return check_password_hash(hash, password)


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload["jti"] = str(uuid.uuid4())

    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload,
        key=auth_settings.authjwt_secret_key,
        algorithm=auth_settings.authjwt_algorithm,
    )

    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=auth_settings.authjwt_secret_key,
            algorithms=[auth_settings.authjwt_algorithm],
        )

        return token_data

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None


serializer = URLSafeTimedSerializer(
    secret_key=auth_settings.authjwt_secret_key, salt="email-configuration"
)


def create_url_safe_token(data: dict):

    token = serializer.dumps(data)

    return token


def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)

        return token_data

    except Exception as e:
        logging.error(str(e))
