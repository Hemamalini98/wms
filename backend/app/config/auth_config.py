import os

SECRET_KEY  = os.getenv("JWT_SECRET_KEY", "wms-secret-key-change-in-production-2024")
ALGORITHM   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8        # 8 hours default
REMEMBER_ME_EXPIRE_DAYS     = 30            # 30 days when remember_me=True
