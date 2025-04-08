import os
import pwd
import getpass

def get_user_info():
    username = getpass.getuser()
    home_dir = os.path.expanduser('~')
    user_info = pwd.getpwnam(username)
    
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
        'uid': user_info.pw_uid,
        'gid': user_info.pw_gid,
        'home': home_dir,
        'shell': user_info.pw_shell,
        'folders': user_folders
    }

def is_in_home_directory(path):
    home_dir = os.path.expanduser('~')
    return os.path.realpath(path).startswith(os.path.realpath(home_dir))

