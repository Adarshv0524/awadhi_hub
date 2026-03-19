# app/management/reconcile_engagement_kpis.py
"""
Reconcile / recompute engagement_kpis weight_score.

Usage:
  python -m app.management.reconcile_engagement_kpis --batch 100
"""
import argparse
from app.db.session import SessionLocal
from app.services.engagement_service import recompute_all_kpis

def main(batch: int = 1000):
    db = SessionLocal()
    try:
        total = recompute_all_kpis(db, batch_limit=batch)
        print(f"Recomputed {total} KPI rows")
    finally:
        db.close()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--batch", type=int, default=1000)
    args = p.parse_args()
    main(batch=args.batch)
