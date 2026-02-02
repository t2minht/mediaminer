import subprocess
import sys


def video_scrapper(url, download_type):
    if download_type == "single":
        print("single")
    elif download_type == "channel":
        print("channel")
    elif download_type == "file":
        print("file")   