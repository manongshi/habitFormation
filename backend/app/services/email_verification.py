import hashlib
import hmac

from fastapi import HTTPException, status
from redis import Redis

from app.core.config import settings

VERIFY_SCRIPT = """
if redis.call('EXISTS', KEYS[1]) == 0 then
  return -1
end
local expected = redis.call('HGET', KEYS[1], 'code_hash')
if expected ~= ARGV[1] then
  local attempts = redis.call('HINCRBY', KEYS[1], 'attempts', 1)
  if attempts >= tonumber(ARGV[2]) then
    redis.call('DEL', KEYS[1])
    return -3
  end
  return -2
end
redis.call('DEL', KEYS[1])
return 1
"""


class EmailVerificationService:
    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def _identity(email: str) -> str:
        return hashlib.sha256(email.lower().encode("utf-8")).hexdigest()

    @staticmethod
    def _code_hash(email: str, scene: str, code: str) -> str:
        message = f"{email.lower()}:{scene}:{code}".encode("utf-8")
        return hmac.new(
            settings.email_code_secret.encode("utf-8"),
            message,
            hashlib.sha256,
        ).hexdigest()

    def save_code(self, email: str, scene: str, code: str) -> None:
        identity = self._identity(email)
        code_key = f"email_code:{scene}:{identity}"
        cooldown_key = f"email_code:cooldown:{scene}:{identity}"
        daily_key = f"email_code:daily:{scene}:{identity}"

        if not self.redis.set(
            cooldown_key,
            "1",
            ex=settings.email_code_cooldown_seconds,
            nx=True,
        ):
            ttl = max(self.redis.ttl(cooldown_key), 1)
            raise HTTPException(status_code=429, detail=f"发送过于频繁，请 {ttl} 秒后重试")

        daily_count = self.redis.incr(daily_key)
        if daily_count == 1:
            self.redis.expire(daily_key, 86400)
        if daily_count > settings.email_code_daily_limit:
            self.redis.delete(cooldown_key)
            raise HTTPException(status_code=429, detail="今日验证码发送次数已达上限")

        pipeline = self.redis.pipeline()
        pipeline.hset(
            code_key,
            mapping={
                "code_hash": self._code_hash(email, scene, code),
                "attempts": "0",
            },
        )
        pipeline.expire(code_key, settings.email_code_expire_seconds)
        pipeline.execute()

    def remove_code(self, email: str, scene: str) -> None:
        identity = self._identity(email)
        self.redis.delete(
            f"email_code:{scene}:{identity}",
            f"email_code:cooldown:{scene}:{identity}",
        )

    def verify_and_consume(self, email: str, scene: str, code: str) -> None:
        identity = self._identity(email)
        code_key = f"email_code:{scene}:{identity}"
        result = self.redis.eval(
            VERIFY_SCRIPT,
            1,
            code_key,
            self._code_hash(email, scene, code),
            settings.email_code_max_attempts,
        )
        if result == -1:
            raise HTTPException(status_code=400, detail="验证码已过期，请重新获取")
        if result == -2:
            raise HTTPException(status_code=400, detail="验证码错误")
        if result == -3:
            raise HTTPException(status_code=400, detail="验证码错误次数过多，请重新获取")

