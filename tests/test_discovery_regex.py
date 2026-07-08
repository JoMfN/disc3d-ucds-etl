from disc3d_ucds.discovery import SCAN_DIR_RE, CAMPOS_RE, EDOF_DIR_RE, CALIBRATED_XML_RE


def test_scan_dir_regex():
    m = SCAN_DIR_RE.match("20250430T104842__06778f__Carabus_violaceus_meyeri__DISC3D")
    assert m
    assert m.group("timestamp") == "20250430T104842"
    assert m.group("object_id") == "06778f"
    assert m.group("label") == "Carabus_violaceus_meyeri"


def test_campos_regex():
    m = CAMPOS_RE.match("20250430T104842__06778f__Carabus_violaceus_meyeri__CamPos.txt")
    assert m
    assert m.group("object_id") == "06778f"


def test_edof_regex():
    m = EDOF_DIR_RE.match("06778f__edof")
    assert m


def test_xml_regex():
    m = CALIBRATED_XML_RE.match("20250430T104842__06778f__Carabus_violaceus_meyeri_Calibrated_Cameras_06778f_20250430T104842.xml")
    assert m
    assert m.group("object_id") == "06778f"
