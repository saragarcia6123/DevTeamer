from fastapi import HTTPException
from datetime import datetime
from lib.utils import now
from services.redis_client import redis_client

r = redis_client.r


async def enforce_email_action_cooldown(
    email: str, action: str, cooldown_seconds: int = 30
):
    """
    Ensures cooldown period for an email-based action (e.g., verification, password reset).
    Raises HTTPException(429) if the cooldown has not expired yet.
    """
    key = f"{email}_{action.upper()}_LAST_REQUEST"
    last_request_time_str = await r.get(key)

    if last_request_time_str:
        last_request_time = datetime.fromisoformat(last_request_time_str)
        time_since_last = (now() - last_request_time).total_seconds()

        if time_since_last < cooldown_seconds:
            time_left = int(cooldown_seconds - time_since_last) 
            raise HTTPException(
                status_code=429,
                detail=''.join([f"Please wait {time_left}", 
                    "seconds before requesting again."]),
            )

    await r.set(key, now().isoformat(), ex=cooldown_seconds)
