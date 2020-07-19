import os


def get_pics_path_list(directory):
    """Returns the list of pictures in the directory.

    Only images with the following extensions are taken into account:
    ['.png', '.jpg', '.jpeg'].

    """
    if not os.path.exists(directory):
        return list()
    pics_path_list = [
        os.path.join(directory, path) for path
        in os.listdir(directory)
        if (os.path.isfile(os.path.join(directory, path)) and
            (os.path.splitext(path)[1].lower() in ('.png', '.jpg', '.jpeg')))
    ]
    return pics_path_list


def codepoint_to_str(cp):
    """Converts a string of the 'U+XXXX' format
    into a corresponding Unicode character.

    """
    return chr(int(cp.lstrip("U+").zfill(8), 16))


def time_in_range(start, end, x):
    """Checks if `x` is in the range [`start`, `end`)."""
    if start < end:
        return start <= x < end
    elif start > end:
        return start <= x or x < end
    else:
        return True
