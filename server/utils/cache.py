"""
进程内缓存工具 - TTL缓存实现
用于权限等高频数据的缓存，减少数据库查询
"""
import time
import threading
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """简单的内存缓存，支持TTL过期"""

    def __init__(self):
        self._store: dict[str, tuple[any, float]] = {}  # key -> (value, expire_at)
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> any:
        """获取缓存值，已过期或不存在返回None"""
        with self._lock:
            if key not in self._store:
                self._misses += 1
                return None
            value, expire_at = self._store[key]
            if expire_at > 0 and time.time() > expire_at:
                del self._store[key]
                self._misses += 1
                return None
            self._hits += 1
            return value

    def set(self, key: str, value: any, ttl_seconds: int = 300):
        """设置缓存，ttl_seconds=0表示永不过期"""
        expire_at = time.time() + ttl_seconds if ttl_seconds > 0 else 0
        with self._lock:
            self._store[key] = (value, expire_at)

    def delete(self, key: str):
        """删除指定缓存"""
        with self._lock:
            self._store.pop(key, None)

    def delete_pattern(self, pattern: str):
        """删除匹配pattern的所有缓存，如 "permissions:*" """
        with self._lock:
            keys_to_delete = [k for k in self._store if self._matches(k, pattern)]
            for k in keys_to_delete:
                del self._store[k]
            if keys_to_delete:
                logger.info(f"cache: deleted {len(keys_to_delete)} keys matching '{pattern}'")

    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._store.clear()
            self._hits = 0
            self._misses = 0

    def _matches(self, key: str, pattern: str) -> bool:
        """简单通配符匹配，pattern支持 * 和 ?"""
        import fnmatch
        return fnmatch.fnmatch(key, pattern)

    def stats(self) -> dict:
        """返回缓存命中率统计"""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0
            return {
                "hits": self._hits,
                "misses": self._misses,
                "total": total,
                "hit_rate": round(hit_rate * 100, 2),
                "keys_count": len(self._store),
            }


# 全局单例缓存实例
_cache = SimpleCache()


def get_cache() -> SimpleCache:
    return _cache


# ========== 权限缓存快捷函数 ==========

PERMISSIONS_CACHE_TTL = 300  # 5分钟


def cache_key(user_id: int, role_id: int = None) -> str:
    """生成权限缓存key"""
    if role_id:
        return f"permissions:{user_id}:{role_id}"
    return f"permissions:{user_id}:all"


def get_permissions_cache(user_id: int, role_id: int = None) -> any:
    """获取权限缓存"""
    return _cache.get(cache_key(user_id, role_id))


def set_permissions_cache(user_id: int, data: any, role_id: int = None, ttl: int = PERMISSIONS_CACHE_TTL):
    """设置权限缓存"""
    _cache.set(cache_key(user_id, role_id), data, ttl)


def invalidate_permissions_cache(user_id: int, role_id: int = None):
    """清除指定用户的权限缓存"""
    if role_id:
        _cache.delete(cache_key(user_id, role_id))
    else:
        _cache.delete_pattern(f"permissions:{user_id}:*")
    logger.info(f"permissions cache invalidated for user_id={user_id}, role_id={role_id}")


def invalidate_user_caches(user_id: int):
    """清除用户所有相关缓存（登录时调用）"""
    _cache.delete_pattern(f"permissions:{user_id}:*")
    logger.info(f"all caches invalidated for user_id={user_id}")