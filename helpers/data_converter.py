def convert_to_dict(obj):
    if isinstance(obj, list):
        return [convert_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_dict(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'):
        return {key: convert_to_dict(value) for key, value in obj.__dict__.items()}
    else:
        return obj