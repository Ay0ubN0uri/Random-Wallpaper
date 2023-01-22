import os
import sys
import subprocess
import re


class PyWallpaper():
    def get_desktop_environment(self):
        if sys.platform in ["win32", "cygwin"]:
            return "windows"
        elif sys.platform == "darwin":
            return "mac"
        else: #Most likely either a POSIX system or something not much common
            desktop_session = os.environ.get("DESKTOP_SESSION")
            if desktop_session is not None: #easier to match if we doesn't have  to deal with caracter cases
                desktop_session = desktop_session.lower()
                if desktop_session in ["gnome","unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox", 
                                        "blackbox", "openbox", "icewm", "jwm", "afterstep","trinity", "kde"]:
                    return desktop_session
                elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
                    return "xfce4"
                elif desktop_session.startswith('ubuntustudio'):
                    return 'kde'
                elif desktop_session.startswith('ubuntu'):
                    return 'gnome'     
                elif desktop_session.startswith("lubuntu"):
                    return "lxde" 
                elif desktop_session.startswith("kubuntu"): 
                    return "kde" 
                elif desktop_session.startswith("razor"): # e.g. razorkwin
                    return "razor-qt"
                elif desktop_session.startswith("wmaker"): # e.g. wmaker-common
                    return "windowmaker"
            if os.environ.get('KDE_FULL_SESSION') == 'true':
                return "kde"
            elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                if not "deprecated" in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                    return "gnome2"
            elif self.is_running("xfce-mcs-manage"):
                return "xfce4"
            elif self.is_running("ksmserver"):
                return "kde"
        return "unknown"

    def is_running(self, process):
        try: #Linux/Unix
            s = subprocess.Popen(["ps", "axw"],stdout=subprocess.PIPE)
        except: #Windows
            s = subprocess.Popen(["tasklist", "/v"],stdout=subprocess.PIPE)
        for x in s.stdout:
            if re.search(process, x):
                return True
        return False
    
    def set_wallpaper(self,file_loc):
            desktop_env = self.get_desktop_environment()
            try:
                if desktop_env in ["gnome", "unity", "cinnamon"]:
                    color_scheme = subprocess.run(['gsettings', 'get','org.gnome.desktop.interface', 'color-scheme'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()[1:-1]
                    if color_scheme.lower() == 'prefer-dark':
                        command = f"gsettings set org.gnome.desktop.background picture-uri-dark 'file://{file_loc}'"
                    else:
                        command = f"gsettings set org.gnome.desktop.background picture-uri 'file://{file_loc}'"
                    os.system(command)
                elif desktop_env in ["kde3", "trinity"]:
                    args = 'dcop kdesktop KBackgroundIface setWallpaper 0 "%s" 6' % file_loc
                    subprocess.Popen(args,shell=True)
                elif desktop_env=="xfce4":
                    args0 = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-path", "-s", file_loc]
                    args1 = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-style", "-s", "3"]
                    args2 = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-show", "-s", "true"]
                    subprocess.Popen(args0)
                    subprocess.Popen(args1)
                    subprocess.Popen(args2)
                    args = ["xfdesktop","--reload"]
                    subprocess.Popen(args)
                elif desktop_env=="windows":
                    import ctypes
                    SPI_SETDESKWALLPAPER = 20 
                    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, file_loc , 0)
                else:
                    sys.stderr.write("Warning: Failed to set wallpaper. Your desktop environment is not supported.")
                    sys.stderr.write("You can try manually to set Your wallpaper to %s" % file_loc)
                    return False
                return True
            except:
                sys.stderr.write("ERROR: Failed to set wallpaper. There might be a bug.\n")
                return False