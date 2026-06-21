import frappe
from frappe.utils import time_diff_in_hours


# =========================================================
# SAFE FLOAT CONVERTER
# =========================================================
def safe_float(value):
    try:
        return float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        return 0.0


# =========================================================
# FORMAT HOURS (UI DISPLAY)
# =========================================================
def format_hours(hours):
    try:
        hours = float(hours or 0)
        h = int(hours)
        m = int(round((hours - h) * 60))
        return f"{h}h {m}m"
    except:
        return "0h 0m"


# =========================================================
# FORMAT TIME (UI ONLY)
# =========================================================
def format_time_only(dt):
    if not dt:
        return "-"
    try:
        return dt.strftime("%I:%M %p").lstrip("0")
    except:
        return "-"


# =========================================================
# TIME DIFFERENCE (HOURS)
# =========================================================
def time_diff_hours(start, end):
    if start and end:
        try:
            return float(time_diff_in_hours(end, start))
        except:
            return 0.0
    return 0.0


# =========================================================
# TIME DIFFERENCE (MINUTES)
# =========================================================
def time_diff_minutes(start, end):
    if start and end:
        try:
            return float(time_diff_in_hours(end, start) * 60)
        except:
            return 0.0
    return 0.0