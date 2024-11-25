import imghdr
from functools import partial
from pathlib import Path
from typing import Optional, Tuple, Union

import imagehash
import pandas as pd
from PIL import ExifTags, Image

from ydata_profiling.config import Settings
from ydata_profiling.model.summary_algorithms import (
    describe_image_1d,
    named_aggregate_summary,
)
from ydata_profiling.model.var_description.default import VarDescription
from ydata_profiling.utils.imghdr_patch import *  # noqa: F401,F403


def open_image(path: Path) -> Optional[Image.Image]:
    """

    Args:
        path:

    Returns:

    """
    try:
        return Image.open(path)
    except (OSError, AttributeError):
        return None


def is_image_truncated(image: Image) -> bool:
    """Returns True if the path refers to a truncated image

    Args:
        image:

    Returns:
        True if the image is truncated
    """
    try:
        image.load()
    except (OSError, AttributeError):
        return True
    else:
        return False


def get_image_shape(image: Image) -> Optional[Tuple[int, int]]:
    """

    Args:
        image:

    Returns:

    """
    try:
        return image.size
    except (OSError, AttributeError):
        return None


def hash_image(image: Image) -> Optional[str]:
    """

    Args:
        image:

    Returns:

    """
    try:
        return str(imagehash.phash(image))
    except (OSError, AttributeError):
        return None


def decode_byte_exif(exif_val: Union[str, bytes]) -> str:
    """Decode byte encodings

    Args:
        exif_val:

    Returns:

    """
    if isinstance(exif_val, str):
        return exif_val
    else:
        return exif_val.decode()


def extract_exif(image: Image) -> dict:
    """

    Args:
        image:

    Returns:

    """
    try:
        exif_data = image._getexif()
        if exif_data is not None:
            exif = {
                ExifTags.TAGS[k]: decode_byte_exif(v)
                for k, v in exif_data.items()
                if k in ExifTags.TAGS
            }
        else:
            exif = {}
    except (AttributeError, OSError):
        # Not all file types (e.g. .gif) have exif information.
        exif = {}

    return exif


def path_is_image(p: Path) -> bool:
    return imghdr.what(p) is not None


def count_duplicate_hashes(image_descriptions: dict) -> int:
    """

    Args:
        image_descriptions:

    Returns:

    """
    counts = pd.Series(
        [x["hash"] for x in image_descriptions if "hash" in x]
    ).value_counts()
    return counts.sum() - len(counts)


def extract_exif_series(image_exifs: list) -> dict:
    """

    Args:
        image_exifs:

    Returns:

    """
    exif_keys = []
    exif_values: dict = {}

    for image_exif in image_exifs:
        # Extract key
        exif_keys.extend(list(image_exif.keys()))

        # Extract values per key
        for exif_key, exif_val in image_exif.items():
            if exif_key not in exif_values:
                exif_values[exif_key] = []

            exif_values[exif_key].append(exif_val)

    series = {"exif_keys": pd.Series(exif_keys, dtype=object).value_counts().to_dict()}

    for k, v in exif_values.items():
        series[k] = pd.Series(v).value_counts()

    return series


def extract_image_information(
    path: Path, exif: bool = False, hash: bool = False
) -> dict:
    """Extracts all image information per file, as opening files is slow

    Args:
        path: Path to the image
        exif: extract exif information
        hash: calculate hash (for duplicate detection)

    Returns:
        A dict containing image information
    """
    information: dict = {}
    image = open_image(path)
    information["opened"] = image is not None
    if image is not None:
        information["truncated"] = is_image_truncated(image)
        if not information["truncated"]:
            information["size"] = image.size
            if exif:
                information["exif"] = extract_exif(image)
            if hash:
                information["hash"] = hash_image(image)

    return information


def image_summary(series: pd.Series, exif: bool = False, hash: bool = False) -> dict:
    """

    Args:
        series: series to summarize
        exif: extract exif information
        hash: calculate hash (for duplicate detection)

    Returns:

    """

    image_information = series.apply(
        partial(extract_image_information, exif=exif, hash=hash)
    )
    summary = {
        "n_truncated": sum(
            1 for x in image_information if "truncated" in x and x["truncated"]
        ),
        "image_dimensions": pd.Series(
            [x["size"] for x in image_information if "size" in x],
            name="image_dimensions",
        ),
    }

    image_widths = summary["image_dimensions"].map(lambda x: x[0])
    summary.update(named_aggregate_summary(image_widths, "width"))
    image_heights = summary["image_dimensions"].map(lambda x: x[1])
    summary.update(named_aggregate_summary(image_heights, "height"))
    image_areas = image_widths * image_heights
    summary.update(named_aggregate_summary(image_areas, "area"))

    if hash:
        summary["n_duplicate_hash"] = count_duplicate_hashes(image_information)

    if exif:
        exif_series = extract_exif_series(
            [x["exif"] for x in image_information if "exif" in x]
        )
        summary["exif_keys_counts"] = exif_series["exif_keys"]
        summary["exif_data"] = exif_series

    return summary


@describe_image_1d.register
def pandas_describe_image_1d(
    config: Settings, series: pd.Series, summary: VarDescription
) -> Tuple[Settings, pd.Series, VarDescription]:
    if series.hasnans:
        raise ValueError("May not contain NaNs")
    if not hasattr(series, "str"):
        raise ValueError("series should have .str accessor")

    summary.update(image_summary(series, config.vars.image.exif))

    return config, series, summary
