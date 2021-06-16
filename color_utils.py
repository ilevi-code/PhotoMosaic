from itertools import chain
from math import sqrt


def color_distance(color1, color2):
    """
    Good image score is about 50
    """
    handicap = 50 if sum(chain(color1, color2)) > 200 * 6 else 0
    rdiff = color1[0] - color2[0]
    gdiff = color1[1] - color2[1]
    bdiff = color1[2] - color2[2]
    rmean = (color1[0] + color2[0]) // 2
    # Thanks to https://stackoverflow.com/a/8863952
    return sqrt(
        (((512 + rmean) * rdiff * rdiff) >> 8) + 4 * gdiff * gdiff + (((767 - rmean) * bdiff * bdiff) >> 8)) - handicap
