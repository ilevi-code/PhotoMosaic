import json
from pathlib import Path
from typing import List
from itertools import chain

import tqdm
from PIL import Image
from math import sqrt
import test

METADATA_PATH = './meta.json'
DIR = './pics/'
THUMBNAIL_DIR = './thmbs'
MAIN_IMAGE = 'main.png'

GRID_WIDTH = 34
GRID_HEIGHT = 20
ACCURACY = 3


def color_distance(color1, color2):
    rdiff = color1[0] - color2[0]
    gdiff = color1[1] - color2[1]
    bdiff = color1[2] - color2[2]
    rmean = (color1[0] + color2[0]) // 2
    # WTF https://stackoverflow.com/a/8863952
    return sqrt((((512 + rmean) * rdiff * rdiff) >> 8) + 4 * gdiff * gdiff + (((767 - rmean) * bdiff * bdiff) >> 8))


class ImageSet:
    def __init__(self, dir_path, thmbs_path):
        self.dir_path = dir_path
        self.thmbs_path = thmbs_path
        self.image_data = {}
        if not Path(METADATA_PATH).exists():
            self.analyze()
        with open(METADATA_PATH) as file:
            self.image_data = json.load(file)

    def analyze(self):
        output = {}
        for file in Path(self.dir_path).iterdir():
            with Image.open(file) as image:
                image = image.resize((ACCURACY, ACCURACY))
                output[str(file)] = (list(image.getdata()))
        with open(METADATA_PATH, 'w') as meta_file:
            json.dump(output, meta_file)

    def find_match(self, beeg_data: List[List[int]]):
        highest = ('', None)

        for name, smol_data in self.image_data.items():
            if (score := self.match_score(beeg_data, smol_data)) < (highest[1] or score + 1):
                highest = (name, score)

        self.image_data.pop(highest[0])
        return highest[0]

    @staticmethod
    def match_score(data1, data2):
        score = 0
        for i, j in zip(data1, data2):
            score += color_distance(i, j)
        return score


def main():
    set = ImageSet(DIR, THUMBNAIL_DIR)

    orig = Image.open(MAIN_IMAGE)
    mini_width = orig.size[0] // GRID_WIDTH
    mini_height = orig.size[1] // GRID_HEIGHT

    test_image = orig.resize((GRID_WIDTH * ACCURACY, GRID_HEIGHT * ACCURACY))
    mozaicd = Image.new('RGBA', orig.size)
    for i in tqdm.trange(GRID_WIDTH):
        for j in range(GRID_HEIGHT):
            # START_X, START_Y, END_X, END_Y
            cropped = test_image.crop(
                (i * ACCURACY, j * ACCURACY,
                 i * ACCURACY + (ACCURACY - 1), j * ACCURACY + (ACCURACY - 1))
            )
            best_match_name = set.find_match(cropped.getdata())
            paste_point = (i * mini_width, j * mini_height)
            resized = Image.open(best_match_name).resize((mini_width, mini_height))
            mozaicd.paste(resized, paste_point)
    mozaicd.save('here.png')


if __name__ == "__main__":
    main()
