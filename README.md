# PhotoMosaic

The goal of this project is to generate a mosaic of small photos that form together a larger picture.

```
Usage: mosaic.py [OPTIONS]
Options:
  -c, --cols INTEGER              Mini-pictures columns  
  -r, --rows INTEGER              Mini-pictures rows  
  -i, --input-dir DIRECTORY       Directory of images to use  
    -m, --output-dim-multiplier INTEGER
                                  Multiply output image size  
  --help                          Show this message and exit.  
```

* Note: The output is not deterministic because of randomization included to prevent repetition in the mosaic.  
  The script finds a few good candidates for each mini-image, and one of them is chosen randomly.


* Pro-tip: After generating an image you are satisfied with, open your favorite image editor  
and overlay the original image with low opacity (the 'overlay' setting in Photoshop works great)