from ytmusic_deleter.common import HeaderCleanup


def test_cleanup_standard_firefox_headers():
    """Ensure already formatted headers are left alone."""
    raw = "Host: music.youtube.com\nUser-Agent: Mozilla/5.0"
    cleaned = HeaderCleanup.cleanup_headers(raw)
    assert cleaned == raw


def test_cleanup_chrome_alternating_headers():
    """Ensure standard alternating Chrome headers are joined correctly."""
    raw = "Host\nmusic.youtube.com\nAccept\n*/*"
    expected = "Host: music.youtube.com\nAccept: */*"
    cleaned = HeaderCleanup.cleanup_headers(raw)
    assert cleaned == expected


def test_cleanup_chrome_empty_values():
    """Ensure empty header values don't shift the alternating pattern."""
    raw = "Host\nmusic.youtube.com\nEmpty-Header\n\nAccept\n*/*"
    cleaned = HeaderCleanup.cleanup_headers(raw)
    assert "Host: music.youtube.com" in cleaned
    assert "Empty-Header: " in cleaned
    assert "Accept: */*" in cleaned


def test_cleanup_chrome_wrapped_multiline():
    """Ensure long values broken by terminal wrapping are stitched back together."""
    raw = (
        "cookie\n"
        "LOGIN_INFO=AFmmF2swRQIgXsr\n"
        "VISITOR_INFO1_LIVE=ulHbiv7\n"
        "PREF=f6=80&tz=America\n"
        "origin\n"
        "https://music.youtube.com"
    )
    cleaned = HeaderCleanup.cleanup_headers(raw)

    # The cookie parts should be combined into one single line
    expected_cookie = "cookie: LOGIN_INFO=AFmmF2swRQIgXsrVISITOR_INFO1_LIVE=ulHbiv7PREF=f6=80&tz=America"

    assert expected_cookie in cleaned
    assert "origin: https://music.youtube.com" in cleaned


def test_client_variations_removal():
    """Ensure the giant Decoded ClientVariations block is stripped out."""
    raw = (
        "x-client-data\n"
        "CLO1yQEIlbbJA\n"
        "Decoded:\n"
        "message ClientVariations {\n"
        "  repeated int32 variation_id = [3300019];\n"
        "}\n"
        "x-goog-authuser\n"
        "0"
    )
    cleaned = HeaderCleanup.cleanup_headers(raw)

    assert "Decoded:" not in cleaned
    assert "message ClientVariations" not in cleaned
    assert "x-client-data: CLO1yQEIlbbJA" in cleaned
    assert "x-goog-authuser: 0" in cleaned
