import json
import random
from itertools import chain
from math import sqrt
from pathlib import Path
from typing import List
import operator

import click
import tqdm
from PIL import Image

from cache import Cache
from color_utils import color_distance

MAIN_IMAGE = 'main.png'

ACCURACY = 3


class Mosaic:
    def __init__(self, dir_path, cache: Cache):
        self.dir_path = dir_path
        self.image_data = cache.load_image_metadata()

    def assemble(self, orignal, cols, rows) -> Image:
        mini_width = orignal.size[0] // cols
        mini_height = orignal.size[1] // rows

        test_image = orignal.resize((cols * ACCURACY, rows * ACCURACY))
        output = Image.new('RGBA', orignal.size)
        for i in tqdm.trange(cols):
            for j in range(rows):
                # START_X, START_Y, END_X, END_Y
                cropped = test_image.crop(
                    (i * ACCURACY, j * ACCURACY,
                     i * ACCURACY + (ACCURACY - 1), j * ACCURACY + (ACCURACY - 1))
                )
                best_match_name = self.find_match(cropped.getdata())
                paste_point = (i * mini_width, j * mini_height)
                resized = Image.open(best_match_name).resize((mini_width, mini_height))
                output.paste(resized, paste_point)
        return output

    def find_match(self, beeg_data: List[List[int]], threshold=250) -> str:
        highest = ('', None)
        possible_matches = []

        for name, smol_data in self.image_data.items():
            if (score := self.match_score(beeg_data, smol_data)) < (highest[1] or score + 1):
                highest = (name, score)
            if score < threshold:
                possible_matches.append(name)

        if len(possible_matches) > 2:
            return random.choice(possible_matches)
        return self.find_match(beeg_data, threshold + 100)

    @staticmethod
    def match_score(data1, data2):
        score = 0
        for i, j in zip(data1, data2):
            score += color_distance(i, j)
        return score


def str_to_path(ctx, param, value):
    return Path(value)


@click.command()
@click.option('-c', '--cols', type=click.INT, default=70, help='Mini-pictures columns')
@click.option('-r', '--rows', type=click.INT, default=50, help='Mini-pictures rows')
@click.option('-i', '--input-dir', type=click.Path(file_okay=False, exists=True), default='pics', help='', callback=str_to_path) # TODO
def main(cols: int, rows: int, input_dir: click.Path):
    orig = Image.open(MAIN_IMAGE)
    orig = orig.resize((orig.size[0] * 3, orig.size[1] * 3))

    cache = Cache(input_dir, cols, rows, ACCURACY, orig.size[1] / orig.size[0])
    cache.setup()

    set = Mosaic(input_dir, cache)

    set.assemble(orig, cols, rows).save(f'output-{cache.suffix}.png')


if __name__ == "__main__":
    main()
