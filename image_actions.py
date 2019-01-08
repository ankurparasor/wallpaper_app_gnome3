"""
Library for download and perform operations on images on Reddit.com
"""
import urllib
import shutil
import json
from os import mknod, path
import itertools
import time
import traceback
import subprocess
import datetime
import requests
from Logger import Logger

IMAGE_NO = 0
MAX_IMAGE_NO = 30
def _loop():
    try:
        log = Logger()
        global IMAGE_NO
        image_number_file = path.join(path.dirname(path.realpath(__file__)), 'image_number.txt')
        with open(image_number_file, 'r') as _fh:
            i = _fh.read()
        i = int(i)
        IMAGE_NO = i
        log.info("Current image number = %s" % IMAGE_NO)
        i = (i + 1) if i < MAX_IMAGE_NO else 0
        with open(image_number_file, 'w') as _fh:
            i = str(i)
            _fh.write(i)
    except Exception:
        traceback.print_exc()
        raise

class ImageOps:
    """
    This class has all the functions to be used for image manipulation
    """
    def __init__(self, url, jpg_image):
        self.url = url
        self.jpg_image = jpg_image
        self.log = Logger()

    def retry_func(delays=(0, 1, 5, 30, 180, 600, 3600),
                   exception=Exception):
        """
        This will be used as a decorator to perform retries
        """
        def wrapper(function):
            def wrapped(*args, **kwargs):
                problems = []
                for delay in itertools.chain(delays, [None]):
                    try:
                        return function(*args, **kwargs)
                    except Exception as problem:
                        problems.append(problem)
                        if delay is None:
                            print "Retryable failed definitely: %s" %problems
                            raise
                        else:
                            time.sleep(delay)
            return wrapped
        return wrapper

    @retry_func(delays=itertools.cycle([10]))
    def internet_on(self, limit):
        self.log.info("Checking internet connectivity ..")
        try:
            google_url = 'http://216.58.192.142'
            self.log.info("Trying to connect to [%s] -> fancy for google.com"%google_url)
            requests.get(google_url, timeout=10)
            return True
        except ConnectionError:
            self.log.error("Connection error while connecting to google.com")
            return False
        except Timeout:
            self.log.error("Connection timed-out while connecting to google.com")
            return False

    def is_image(self):
        """
        Does the url contain an image
        """
        h = requests.head(self.url, allow_redirects=True)
        header = h.headers
        content_type = header.get('content-type')
        if 'text' in content_type.lower():
            return False
        if 'html' in content_type.lower():
            return False
        return True

    def download_image(self, _absolute_download_path):
        """
        Download the image.
        """
        global IMAGE_NO
        _loop()
        image_url_file = path.join(path.dirname(path.realpath(__file__)), 'image_url.txt')
        retries = 5
        _n = 0
        while _n < retries:
            self.log.info("Opening url: [%s]"%self.url)
            response = requests.get(self.url)
            rawdata = json.loads(response.text)
            print rawdata, "=" * 80, rawdata.keys()
            if 'data' in rawdata.keys():
                break
            self.log.error("Corrupted json")
            self.log.info("Retrying after sleeping for 1 sec ...")
            time.sleep(1)
            _n = _n + 1
        image_url = rawdata['data']['children'][IMAGE_NO]['data']['url']
        image_title = rawdata['data']['children'][IMAGE_NO]['data']['title']
        self.log.info("New image url: [%s]"%image_url)
        if not path.isfile(image_url_file):
            self.log.info("%s does not exist. Creating it .."%image_url_file)
            mknod(image_url_file)
        with open(image_url_file, 'r') as _fh:
            wallpaper_url = _fh.read()
            self.log.info("Current wallpaper url: [%s]"%wallpaper_url)
            assert wallpaper_url != image_url.strip(), "Its the same image. Will skip download."
            self.log.info("New image found.")
        with open(image_url_file, 'w') as _fh:
            _fh.write(image_url)
        r = requests.get(image_url)
        if r.status_code == 200:
            with open(path.join(_absolute_download_path, self.jpg_image), "wb") as _fh:
                _fh.write(r.content)
        self.log.info("Image downloaded.")
        return image_title

    def save_image(self, _absolute_save_path):
        """
        Saves the current wallpaper by appending current date_time to its name
        """
        self.log.info("Saving image ...")
        saved_image = '_'.join([self.jpg_image, datetime.datetime.now().strftime("%Y-%m-%d-%H_%M")])
        commandbash = "cp %s %s" % (
            path.join(path.dirname(path.realpath(__file__)), self.jpg_image),
            path.join(path.dirname(path.realpath(__file__)), saved_image)
            )
        try:
            process = subprocess.Popen(commandbash, stdout=subprocess.PIPE, shell=True)
            proc_stdout = process.communicate()[0].strip()
            self.log.info("Result: %s" % (proc_stdout))
            if path.isfile(path.join(path.dirname(path.realpath(__file__)), saved_image)):
                self.log.info("Image saved. Yayy!!")
        except OSError as _msg:
            self.log.error("Failed to save image: %s" % _msg)
