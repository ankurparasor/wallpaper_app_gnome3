"""
Script uses custom libraries to download an image from a url (jsonable link)
and set as wallpaper for Gnome3 DE.
"""
import subprocess
from os import path
import sys
from Logger import Logger
from image_actions import ImageOps

URL = "https://www.reddit.com/r/EarthPorn.json"
#URL = "https://www.reddit.com/r/MinimalWallpaper.json"
#URL = "https://www.reddit.com/r/wallpaper+wallpapers.json"
#URL = "https://www.reddit.com/r/wallpapers.json"
#URL = "https://www.reddit.com/r/iWallpaper.json"
#URL = "https://www.reddit.com/r/WQHD_Wallpaper.json"
IMAGE_NAME = "earthporn_2.jpg"
ICON = "reddit.png"

def subprocess_cmd(command):
    """
    Uses Python's subprocess.Popen to run commands.
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print proc_stdout

def arg_parser(argv):
    """
    Used for parsing argument passed to the script
    """
    _arg = argv[1]
    return _arg

def main():
    """
    MAIN
    """
    log = Logger()
    url = URL
    image_name = IMAGE_NAME
    _download_path = path.dirname(path.realpath(__file__))
    log.info("Download/Save path: %s" % _download_path)

    _image_ops = ImageOps(url, image_name)
    if len(sys.argv) > 1 and arg_parser(sys.argv) == 'save':
        _image_ops.save_image(_download_path)
        return
    assert _image_ops.internet_on(
        limit=5), "ERROR: Check Internet connectivity."
    if not _image_ops.is_image():
        log.error("The url doesn't point to an image :( Try again.")
    title = _image_ops.download_image(_download_path)
    _downloaded_image = path.join(_download_path, image_name)
    set_wallpaper_cmd = "gsettings set org.gnome.desktop.background " \
        "picture-uri file://%s" % _downloaded_image
    subprocess_cmd(set_wallpaper_cmd)
    log.info("Wallpaper set: %s" % _downloaded_image)
    notify_title_cmd = "notify-send -i %s Wallpaper_Description \"%s\"" %(
                        path.join(path.dirname(__file__), ICON), title)
    print notify_title_cmd
    print "=" * 80
    subprocess_cmd(notify_title_cmd)

if __name__ == '__main__':
    main()