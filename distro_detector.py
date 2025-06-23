import subprocess
import platform
import os

def get_distro_info():
    """Get system information compatible with both Linux and macOS"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        try:
            # Get macOS version information
            result = subprocess.run(['sw_vers'], 
                                   capture_output=True, 
                                   text=True)
            if result.returncode == 0:
                return f"macOS System Information:\n{result.stdout}"
        except FileNotFoundError:
            pass
        
        # Fallback for macOS
        try:
            result = subprocess.run(['system_profiler', 'SPSoftwareDataType'], 
                                   capture_output=True, 
                                   text=True)
            if result.returncode == 0:
                return f"macOS System Profile:\n{result.stdout}"
        except FileNotFoundError:
            pass
        
        # Basic macOS info
        return f"macOS {platform.mac_ver()[0]}"
    
    elif system == "Linux":
        try:
            # Using lsb_release for distribution detection
            result = subprocess.run(['lsb_release', '-a'], 
                                   capture_output=True, 
                                   text=True)
            if result.returncode == 0:
                return result.stdout
        except FileNotFoundError:
            pass
        
        # Fallback to neofetch if lsb_release isn't available
        try:
            result = subprocess.run(['neofetch', '--stdout'], 
                                   capture_output=True, 
                                   text=True)
            if result.returncode == 0:
                return result.stdout
        except FileNotFoundError:
            pass
        
        # Another fallback option
        try:
            with open('/etc/os-release', 'r') as f:
                return f.read()
        except:
            pass
    
    # Generic fallback
    return f"{system} {platform.release()}"

