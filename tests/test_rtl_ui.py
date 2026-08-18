from shamaran.ui.console import contains_rtl, rtl_display


def test_detects_persian_text() -> None:
    assert contains_rtl("وضعیت پروژه")
    assert not contains_rtl("project status")


def test_rtl_display_shapes_and_reorders_persian() -> None:
    logical = "شاخه main با origin هماهنگ است"
    visual = rtl_display(logical)
    assert visual != logical
    assert "main" in visual
    assert "origin" in visual


def test_rtl_display_removes_basic_markdown_markers() -> None:
    visual = rtl_display("**وضعیت** `main`")
    assert "**" not in visual
    assert "`" not in visual
    assert "main" in visual
