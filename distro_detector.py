import subprocess

def get_distro_info():
    try:
        # Using lsb_release for distribution detection
        result = subprocess.run(['lsb_release', '-a'], 
                               capture_output=True, 
                               text=True)
        return result.stdout
    except FileNotFoundError:
        # Fallback to neofetch if lsb_release isn't available
        try:
            result = subprocess.run(['neofetch', '--stdout'], 
                                   capture_output=True, 
                                   text=True)
            return result.stdout
        except FileNotFoundError:
            # Another fallback option
            try:
                with open('/etc/os-release', 'r') as f:
                    return f.read()
            except:
                return "Unknown distribution"

