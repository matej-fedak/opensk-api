from scripts.check_docs import check_file, heading_anchors, markdown_files


def test_repository_markdown_links():
    errors = [issue for path in markdown_files() for issue in check_file(path)[1]]
    assert not errors, "\n".join(errors)


def test_heading_anchors_preserve_unicode_and_duplicate_suffixes():
    assert heading_anchors("# ŠÚ SR\n## Hello `world`\n## Hello world\n") == {
        "šú-sr", "hello-world", "hello-world-1",
    }


def test_empty_targets_and_missing_anchors_are_reported(tmp_path):
    path = tmp_path / "guide.md"
    path.write_text("# Guide\n[empty]()\n[missing](absent.md)\n[anchor](#absent)\n", encoding="utf-8")
    _, errors = check_file(path)
    assert len(errors) == 3


def test_fenced_and_comment_examples_are_not_links(tmp_path):
    path = tmp_path / "guide.md"
    path.write_text("# Guide\n```md\n[example]()\n```\n<!-- [hidden]() -->\n[valid](#guide)\n", encoding="utf-8")
    assert check_file(path) == (1, [])
