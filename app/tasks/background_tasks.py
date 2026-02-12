import asyncio
from datetime import datetime, timedelta
from app.db.mongo import get_database
from typing import Optional

async def delete_old_invitations(interval_seconds: int = 600, limit_days: int = 7):
    """
    Background task to delete invitations that are ACCEPTED or REJECTED 
    and haven't been updated for 'limit_days'.
    
    :param interval_seconds: How often the task runs in seconds.
    :param limit_days: Age of invitations (in days) to delete.
    """
    while True:
        try:
            # Connect to DB (assuming get_database returns the db instance)
            db = await get_database() 
            invitations_collection = db["invitations"] # Access collection directly or via dependency if preferred

            cutoff_time = datetime.utcnow() - timedelta(days=limit_days)
            
            # Delete query
            result = await invitations_collection.delete_many({
                "status": {"$in": ["ACCEPTED", "REJECTED"]},
                # "updated_at": {"$lt": cutoff_time} # Any invitation updated before cutoff date, are is deleted via this background task.
            })

            if result.deleted_count > 0:
                print(f"[Cleanup] Deleted {result.deleted_count} old invitations.")
            
            else:
                print("[Cleanup] No old invitations to delete.")
            
        except Exception as e:
            print(f"[Cleanup Error] Error deleting old invitations: {e}")
        
        # Sleep for the specified interval
        await asyncio.sleep(interval_seconds)
