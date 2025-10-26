"""Firestore service"""

from typing import Optional, Any
from datetime import datetime, timedelta
import structlog
from firebase_admin import firestore

logger = structlog.get_logger()

# Get Firestore client
try:
    db = firestore.client()
    logger.info("firestore_client_initialized")
except Exception as e:
    logger.error("firestore_client_initialization_failed", error=str(e))
    db = None


class FirestoreCache:
    """Firestore-based cache service"""

    def __init__(self, collection_name: str = "cache"):
        self.collection_name = collection_name

    def _get_collection(self):
        """Get Firestore collection"""
        if db is None:
            raise Exception("Firestore client not initialized")
        return db.collection(self.collection_name)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            doc_ref = self._get_collection().document(key)
            doc = doc_ref.get()

            if not doc.exists:
                logger.debug("cache_miss", key=key)
                return None

            data = doc.to_dict()

            # Check expiration
            expires_at = data.get("expires_at")
            if expires_at and expires_at < datetime.utcnow():
                logger.debug("cache_expired", key=key)
                # Delete expired cache
                doc_ref.delete()
                return None

            logger.debug("cache_hit", key=key)
            return data.get("value")

        except Exception as e:
            logger.error("cache_get_failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache"""
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)

            doc_ref = self._get_collection().document(key)
            doc_ref.set(
                {
                    "key": key,
                    "value": value,
                    "created_at": datetime.utcnow(),
                    "expires_at": expires_at,
                }
            )

            logger.debug("cache_set", key=key, ttl=ttl)
            return True

        except Exception as e:
            logger.error("cache_set_failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            doc_ref = self._get_collection().document(key)
            doc_ref.delete()
            logger.debug("cache_deleted", key=key)
            return True

        except Exception as e:
            logger.error("cache_delete_failed", key=key, error=str(e))
            return False

    async def clear_expired(self) -> int:
        """Clear all expired cache entries"""
        try:
            now = datetime.utcnow()
            expired_docs = self._get_collection().where("expires_at", "<", now).stream()

            count = 0
            for doc in expired_docs:
                doc.reference.delete()
                count += 1

            logger.info("expired_cache_cleared", count=count)
            return count

        except Exception as e:
            logger.error("clear_expired_failed", error=str(e))
            return 0


class UserProfileService:
    """User profile service using Firestore"""

    def __init__(self, collection_name: str = "user_profiles"):
        self.collection_name = collection_name

    def _get_collection(self):
        """Get Firestore collection"""
        if db is None:
            raise Exception("Firestore client not initialized")
        return db.collection(self.collection_name)

    async def get_profile(self, uid: str) -> Optional[dict]:
        """Get user profile"""
        try:
            doc_ref = self._get_collection().document(uid)
            doc = doc_ref.get()

            if not doc.exists:
                logger.debug("user_profile_not_found", uid=uid)
                return None

            return doc.to_dict()

        except Exception as e:
            logger.error("get_profile_failed", uid=uid, error=str(e))
            return None

    async def create_profile(self, uid: str, profile_data: dict) -> bool:
        """Create user profile"""
        try:
            doc_ref = self._get_collection().document(uid)

            profile_data.update(
                {
                    "uid": uid,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            )

            doc_ref.set(profile_data)
            logger.info("user_profile_created", uid=uid)
            return True

        except Exception as e:
            logger.error("create_profile_failed", uid=uid, error=str(e))
            return False

    async def update_profile(self, uid: str, update_data: dict) -> bool:
        """Update user profile"""
        try:
            doc_ref = self._get_collection().document(uid)

            update_data.update(
                {
                    "updated_at": datetime.utcnow(),
                }
            )

            doc_ref.update(update_data)
            logger.info("user_profile_updated", uid=uid)
            return True

        except Exception as e:
            logger.error("update_profile_failed", uid=uid, error=str(e))
            return False

    async def delete_profile(self, uid: str) -> bool:
        """Delete user profile"""
        try:
            doc_ref = self._get_collection().document(uid)
            doc_ref.delete()
            logger.info("user_profile_deleted", uid=uid)
            return True

        except Exception as e:
            logger.error("delete_profile_failed", uid=uid, error=str(e))
            return False


# Global cache instance
cache = FirestoreCache()
user_profile_service = UserProfileService()


async def check_firestore() -> str:
    """Check Firestore connection"""
    try:
        if db is None:
            return "error"

        # Try to read a collection
        collections = db.collections()
        list(collections)  # Force evaluation

        return "ok"
    except Exception as e:
        logger.error("firestore_check_failed", error=str(e))
        return "error"
