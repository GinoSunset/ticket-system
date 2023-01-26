from PIL import Image


def is_image(file):
    """
    check img use PIL
    """
    try:
        Image.open(file)
        return True
    except:
        return False
