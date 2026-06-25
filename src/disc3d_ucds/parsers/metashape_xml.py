from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET


def extract_intrinsics(path: str | Path) -> dict:
    """Extract a single-frame camera calibration from a Metashape XML export."""
    path = Path(path)
    root = ET.parse(path).getroot()
    sensor = root.find(".//sensor")
    if sensor is None:
        raise ValueError("No <sensor> found in Metashape XML")

    res = sensor.find("resolution")
    if res is None:
        raise ValueError("No <resolution> found in sensor")

    width = int(res.attrib["width"])
    height = int(res.attrib["height"])

    calibration = sensor.find("calibration[@class='adjusted']")
    if calibration is None:
        calibration = sensor.find("calibration[@class='initial']")
    if calibration is None:
        raise ValueError("No initial or adjusted calibration found")

    f_tag = calibration.find("f")
    if f_tag is None or not f_tag.text:
        raise ValueError("Calibration contains no <f> focal length")

    f = float(f_tag.text)

    cx_tag = calibration.find("cx")
    cy_tag = calibration.find("cy")
    cx = width / 2.0 + (float(cx_tag.text) if cx_tag is not None and cx_tag.text else 0.0)
    cy = height / 2.0 + (float(cy_tag.text) if cy_tag is not None and cy_tag.text else 0.0)

    return {
        "camera_model": "PINHOLE",
        "width": width,
        "height": height,
        "fx": f,
        "fy": f,
        "cx": cx,
        "cy": cy,
        "distortion": None,
        "source_file": str(path),
    }
