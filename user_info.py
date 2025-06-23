import os
import getpass
import platform

def get_user_info():
    """Get user information compatible with both Linux and macOS"""
    username = getpass.getuser()
    home_dir = os.path.expanduser('~')
    
    # Handle user info differently for macOS vs Linux
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # macOS doesn't have the same pwd module behavior
        try:
            import pwd
            user_info = pwd.getpwnam(username)
            uid = user_info.pw_uid
            gid = user_info.pw_gid
            shell = user_info.pw_shell
        except (ImportError, KeyError):
            # Fallback for macOS
            uid = os.getuid()
            gid = os.getgid()
            shell = os.environ.get('SHELL', '/bin/zsh')
    else:
        # Linux
        try:
            import pwd
            user_info = pwd.getpwnam(username)
            uid = user_info.pw_uid
            gid = user_info.pw_gid
            shell = user_info.pw_shell
        except (ImportError, KeyError):
            uid = os.getuid()
            gid = os.getgid()
            shell = os.environ.get('SHELL', '/bin/bash')
    
    # Define user folders based on platform
    if system == "Darwin":  # macOS
        user_folders = {
            'home': home_dir,
            'desktop': os.path.join(home_dir, 'Desktop'),
            'documents': os.path.join(home_dir, 'Documents'),
            'downloads': os.path.join(home_dir, 'Downloads'),
            'pictures': os.path.join(home_dir, 'Pictures'),
            'music': os.path.join(home_dir, 'Music'),
            'movies': os.path.join(home_dir, 'Movies'),  # macOS uses 'Movies' instead of 'Videos'
            'public': os.path.join(home_dir, 'Public'),
            'library': os.path.join(home_dir, 'Library')
        }
    else:
        # Linux
        user_folders = {
            'home': home_dir,
            'desktop': os.path.join(home_dir, 'Desktop'),
            'documents': os.path.join(home_dir, 'Documents'),
            'downloads': os.path.join(home_dir, 'Downloads'),
            'pictures': os.path.join(home_dir, 'Pictures'),
            'music': os.path.join(home_dir, 'Music'),
            'videos': os.path.join(home_dir, 'Videos')
        }
    
    return {
        'username': username,
        'uid': uid,
        'gid': gid,
        'home': home_dir,
        'shell': shell,
        'folders': user_folders,
        'platform': system
    }

def is_in_home_directory(path):
    """Check if a path is within the user's home directory"""
    home_dir = os.path.expanduser('~')
    try:
        return os.path.realpath(path).startswith(os.path.realpath(home_dir))
    except (OSError, ValueError):
        # Handle cases where path might not exist or be invalid
        return False

