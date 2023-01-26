"""
set is_img in CommentFile
"""


import os
import sys
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ticsys.settings")
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
django.setup()

from ticket.models import CommentFile, CommentImage
from ticket.utils import is_image


def set_is_image_on_comment_file():

    for comment_file in CommentFile.objects.all():
        if is_image(comment_file.file):
            print(f"{comment_file}is img")
            CommentImage.objects.create(
                comment=comment_file.comment, image=comment_file.file
            )
            comment_file.delete()
            continue
        print(f"{comment_file} is NOT img")


if __name__ == "__main__":
    set_is_image_on_comment_file()
