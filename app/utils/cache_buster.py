import os
import hashlib
from flask import url_for

def get_file_version(filepath):
    """Get a version string for a file based on its modification time and size"""
    try:
        if os.path.exists(filepath):
            stat = os.stat(filepath)
            # Create a hash based on modification time and file size
            version_data = f"{stat.st_mtime}_{stat.st_size}"
            return hashlib.md5(version_data.encode()).hexdigest()[:8]
    except:
        pass
    return "v1"

def static_url_with_version(filename):
    """Generate a static URL with version parameter for cache busting"""
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    filepath = os.path.join(static_folder, filename)
    version = get_file_version(filepath)
    return f"/static/{filename}?v={version}"

def get_static_url(filename):
    """Get static URL with cache busting version"""
    return static_url_with_version(filename)
