# app/services/rate_limit.py
from datetime import datetime, timedelta, timezone
import math
from typing import Optional, Tuple
import jwt
import sys

from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import RateLimitCounter
from app.core.settings import settings

def _bucket_start(now: datetime, granularity_seconds: int) -> datetime:
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    ts = int(now.timestamp())
    bucket_ts = (ts // granularity_seconds) * granularity_seconds
    return datetime.fromtimestamp(bucket_ts, tz=timezone.utc)

def check_and_increment(
    db: Session,
    user_id: Optional[int],
    ip_address: Optional[str],
    action_key: str,
    window_seconds: int,
    limit: int,
    granularity: int = 60,
) -> Tuple[bool, int]:
    print(f"[RATE_LIMIT] check_and_increment called: action={action_key}, user_id={user_id}, ip={ip_address}", file=sys.stderr)
    
    now = datetime.now(timezone.utc)  # FIX: use datetime.now(timezone.utc) instead of utcnow()
    bucket = _bucket_start(now, granularity)

    try:
        bind = db.get_bind()
        dialect = bind.dialect.name if bind is not None else ""
    except Exception as e:
        print(f"[RATE_LIMIT] Error getting dialect: {e}", file=sys.stderr)
        dialect = ""

    # ---------------------------------------------------------
    # 1. MySQL Path (Production) - Optimized Raw SQL
    # ---------------------------------------------------------
    if dialect in ("mysql", "pymysql", "mysql+pymysql"):
        try:
            upsert_sql = text("""
                INSERT INTO rate_limit_counters (user_id, ip_address, action_key, time_bucket_start, count, granularity, created_at, updated_at)
                VALUES (:user_id, :ip_address, :action_key, :bucket, 1, :granularity, NOW(), NOW())
                ON DUPLICATE KEY UPDATE count = count + 1, updated_at = NOW()
            """)
            db.execute(upsert_sql, {"user_id": user_id, "ip_address": ip_address, "action_key": action_key, "bucket": bucket, "granularity": granularity})
            db.commit()
            
            buckets_needed = max(1, math.ceil(window_seconds / granularity))
            min_bucket = bucket - timedelta(seconds=(buckets_needed - 1) * granularity)
            agg_sql = text("""
                SELECT COALESCE(SUM(count), 0) FROM rate_limit_counters
                WHERE action_key = :action_key
                  AND ((:user_id IS NULL AND user_id IS NULL) OR user_id = :user_id)
                  AND ((:ip_address IS NULL AND ip_address IS NULL) OR ip_address = :ip_address)
                  AND time_bucket_start >= :min_bucket
            """)
            row = db.execute(agg_sql, {"action_key": action_key, "user_id": user_id, "ip_address": ip_address, "min_bucket": min_bucket}).fetchone()
            total = int(row[0]) if row is not None else 0
        except Exception as e:
            print(f"[RATE_LIMIT] MySQL path error: {e}", file=sys.stderr)
            db.rollback()
            return True, 0

    # ---------------------------------------------------------
    # 2. SQLite / Tests Path
    # ---------------------------------------------------------
    else:
        print(f"[RATE_LIMIT] Using SQLite path", file=sys.stderr)
        max_retries = 3
        success = False
        for attempt in range(max_retries):
            try:
                print(f"[RATE_LIMIT] Attempt {attempt+1}: Querying for existing counter", file=sys.stderr)
                query = db.query(RateLimitCounter).filter(
                    RateLimitCounter.action_key == action_key,
                    RateLimitCounter.time_bucket_start == bucket,
                    RateLimitCounter.user_id == user_id,
                    RateLimitCounter.ip_address == ip_address
                )
                
                counter = query.first()
                print(f"[RATE_LIMIT] Found existing counter: {counter is not None}", file=sys.stderr)

                if counter:
                    counter.count += 1
                    counter.updated_at = datetime.now(timezone.utc)
                    print(f"[RATE_LIMIT] Updating counter to count={counter.count}", file=sys.stderr)
                else:
                    counter = RateLimitCounter(
                        user_id=user_id,
                        ip_address=ip_address,
                        action_key=action_key,
                        time_bucket_start=bucket,
                        count=1,
                        granularity=granularity,
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc)
                    )
                    print(f"[RATE_LIMIT] Creating new counter", file=sys.stderr)
                
                db.add(counter)
                db.commit()
                print(f"[RATE_LIMIT] Successfully committed", file=sys.stderr)
                success = True
                break
            except IntegrityError as e:
                print(f"[RATE_LIMIT] IntegrityError on attempt {attempt+1}: {e}", file=sys.stderr)
                db.rollback()
                continue
            except Exception as e:
                print(f"[RATE_LIMIT] Exception on attempt {attempt+1}: {type(e).__name__}: {e}", file=sys.stderr)
                db.rollback()
                if attempt == max_retries - 1:
                    return True, 0
        
        if not success:
            print(f"[RATE_LIMIT] Failed after all retries", file=sys.stderr)
            return True, 0

        try:
            buckets_needed = max(1, math.ceil(window_seconds / granularity))
            min_bucket = _bucket_start(datetime.now(timezone.utc), granularity) - timedelta(seconds=(buckets_needed - 1) * granularity)
            
            query = db.query(func.coalesce(func.sum(RateLimitCounter.count), 0)).filter(
                RateLimitCounter.action_key == action_key,
                RateLimitCounter.time_bucket_start >= min_bucket
            )
            
            if user_id is None:
                query = query.filter(RateLimitCounter.user_id.is_(None))
            else:
                query = query.filter(RateLimitCounter.user_id == user_id)
            if ip_address is None:
                query = query.filter(RateLimitCounter.ip_address.is_(None))
            else:
                query = query.filter(RateLimitCounter.ip_address == ip_address)

            total = int(query.scalar() or 0)
            print(f"[RATE_LIMIT] Aggregated total: {total}, limit: {limit}", file=sys.stderr)
        except Exception as e:
            print(f"[RATE_LIMIT] Aggregation error: {e}", file=sys.stderr)
            return True, 0

    if total > limit:
        now_ts = int(datetime.now(timezone.utc).timestamp())
        retry_after = granularity - (now_ts % granularity)
        if retry_after <= 0: retry_after = 1
        print(f"[RATE_LIMIT] BLOCKED: total={total} > limit={limit}, retry_after={retry_after}", file=sys.stderr)
        return False, int(retry_after)
    
    print(f"[RATE_LIMIT] ALLOWED: total={total} <= limit={limit}", file=sys.stderr)
    return True, 0


def rate_limit_dependency(action_key: str, limit: int, window_seconds: int, granularity: int = 60):
    from fastapi import Depends
    from app.db.session import get_db
    def _dep(request: Request, db: Session = Depends(get_db)):
        print(f"[RATE_LIMIT_DEP] Dependency called for action={action_key}", file=sys.stderr)
        user_id = None
        try:
            st_user = getattr(request.state, "user", None)
            if st_user is not None:
                user_id = getattr(st_user, "id", None)
        except Exception:
            user_id = None

        if user_id is None:
            try:
                auth = request.headers.get("Authorization") or request.headers.get("authorization")
                if auth and auth.startswith("Bearer "):
                    token = auth.split(" ", 1)[1].strip()
                    if token:
                        try:
                            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                            if "sub" in payload and payload["sub"] is not None:
                                try: user_id = int(payload["sub"])
                                except: user_id = None
                            elif "user_id" in payload:
                                try: user_id = int(payload["user_id"])
                                except: user_id = None
                            elif "id" in payload:
                                try: user_id = int(payload["id"])
                                except: user_id = None
                        except:
                            user_id = None
            except:
                user_id = None

        ip = None
        try:
            ip = request.client.host
        except Exception:
            ip = request.headers.get("X-Forwarded-For")

        print(f"[RATE_LIMIT_DEP] Calling check_and_increment with user_id={user_id}, ip={ip}", file=sys.stderr)
        allowed, retry_after = check_and_increment(db=db, user_id=user_id, ip_address=ip, action_key=action_key, window_seconds=window_seconds, limit=limit, granularity=granularity)
        if not allowed:
            headers = {"Retry-After": str(retry_after)}
            raise HTTPException(status_code=HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests", headers=headers)
        return True
    return _dep
