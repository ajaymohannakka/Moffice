from datetime import datetime, timezone, timedelta


def get_message_time(created_at):
    now = datetime.now(timezone.utc)
    time_difference = now - created_at
    if time_difference < timedelta(minutes=60):
        time_difference_str = f'{int(time_difference.total_seconds() / 60)} minutes ago'
    elif time_difference < timedelta(hours=24):
        time_difference_str = f'{int(time_difference.total_seconds() / 3600)} hours ago'
    elif time_difference < timedelta(days=30):
        time_difference_str = f'{int(time_difference.total_seconds() / 86400)} days ago'
    else:
        time_difference_str = f'{int(time_difference.total_seconds() / 604800)} weeks ago'
    return time_difference_str
    