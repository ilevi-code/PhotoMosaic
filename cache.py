import json
from pathlib import Path

from PIL import Image
from tqdm import tqdm


class Cache:
    _CACHE_DIR = Path('_cache')

    def __init__(self, input_dir: Path, cols: int, rows: int, accuracy: int, image_ratio: float):
        self.input_dir = input_dir
        self.cols = cols
        self.rows = rows
        self.accuracy = accuracy
        self.desired_ratio = image_ratio
        self.suffix = f'{self.cols}-{self.rows}-{self.accuracy}'
        self._CROPPED_DIR = self._CACHE_DIR / f'cropped-{self.suffix}'

    def setup(self):
        self._CACHE_DIR.mkdir(exist_ok=True)
        self._CROPPED_DIR.mkdir(exist_ok=True)
        self._crop_all()
        self._generate_metadata()

    def _crop_all(self):
        for image_path in self.input_dir.iterdir():
            image_cach_path = self._CROPPED_DIR / image_path.name
            if not image_cach_path.exists():
                cropped = self._crop_to_fit(image_path)
                cropped.save(image_cach_path)

    def load_image_metadata(self):
        with open(self._CACHE_DIR / f"meta-{self.suffix}.json") as metadata:
            return json.load(metadata)

    def _generate_metadata(self):
        meta_path = self._CACHE_DIR / f"meta-{self.suffix}.json"
        if not Path(meta_path).exists():
            output = {}
            for file in self._CROPPED_DIR.iterdir():
                with Image.open(file) as image:
                    image = image.resize((self.accuracy, self.accuracy))
                    output[str(file)] = (list(image.getdata()))
            with open(meta_path, 'w') as meta_file:
                json.dump(output, meta_file)

    def _crop_to_fit(self, image_name: Path) -> Image:
        with Image.open(image_name) as image:
            width, height = image.size
            current_ratio = width / height
            if current_ratio < self.desired_ratio:
                # image too high
                desired_height = height * current_ratio / self.desired_ratio
                height_diff = (height - desired_height) // 2
                cropped = image.crop((0, height_diff, width, height - height_diff))
            else:
                # image too wide
                desired_width = width * self.desired_ratio / current_ratio
                width_diff = (width - desired_width) // 2
                cropped = image.crop((width_diff, 0, width - width_diff, height))
            return cropped
