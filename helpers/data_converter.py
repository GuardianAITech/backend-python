def convert_to_dict(obj):
    if isinstance(obj, list):
        return [convert_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_dict(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'):
        return {key: convert_to_dict(value) for key, value in obj.__dict__.items()}
    else:
        return obj
    
def compare_last_scan(latest_last_scan, new_last_scan):
    if not latest_last_scan:
        return new_last_scan

    changes = {}
    for key in new_last_scan:
        if key.startswith("last_"):
            new_value = new_last_scan[key]
            old_value = latest_last_scan.get(key, 0)

            if key in latest_last_scan:
                old_value = latest_last_scan[key]

            if key == 'last_block' and not isinstance(old_value, (int, float)):
                old_value = 0

            numeric_change = new_value - old_value

            percentage_change = ((numeric_change) / abs(old_value)) * 100 if old_value != 0 else 0

            if percentage_change == float('inf'):
                percentage_change = 0

            changes[key] = {"numeric_change": numeric_change, "percentage_change": percentage_change}

    return {"last_scan_changes": changes}





