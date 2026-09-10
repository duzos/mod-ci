import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "readme_to_markdown.py")


def run(text, module_dir=None, env=None):
    full_env = dict(os.environ)
    full_env.pop("README_RAW_BASE", None)
    full_env["GITHUB_REPOSITORY"] = "duzos/example"
    full_env["GITHUB_REF_NAME"] = "main"
    if env:
        full_env.update(env)
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "in.md")
        dst = os.path.join(d, "out.md")
        with open(src, "w", encoding="utf-8") as f:
            f.write(text)
        args = [sys.executable, SCRIPT, src, dst]
        if module_dir is not None:
            args.append(module_dir)
        subprocess.run(args, check=True, env=full_env)
        with open(dst, encoding="utf-8") as f:
            return f.read()


class TestConvert(unittest.TestCase):
    def test_raw_base_derived_from_github_env(self):
        out = run('<img src="img/logo.png" alt="logo">')
        self.assertIn(
            "![logo](https://raw.githubusercontent.com/duzos/example/main/img/logo.png)", out
        )

    def test_raw_base_env_override_wins(self):
        out = run(
            '<img src="img/logo.png" alt="logo">',
            env={"README_RAW_BASE": "https://example.test/base"},
        )
        self.assertIn("![logo](https://example.test/base/img/logo.png)", out)

    def test_module_dir_prefixes_bare_paths(self):
        out = run('<img src="img/logo.png" alt="logo">', module_dir="core")
        self.assertIn(
            "![logo](https://raw.githubusercontent.com/duzos/example/main/core/img/logo.png)", out
        )

    def test_parent_prefix_resolves_against_repo_root(self):
        out = run('<img src="../img/shared.png" alt="s">', module_dir="core")
        self.assertIn(
            "![s](https://raw.githubusercontent.com/duzos/example/main/img/shared.png)", out
        )

    def test_absolute_urls_untouched(self):
        out = run('<img src="https://cdn.test/x.svg" alt="x">')
        self.assertIn("![x](https://cdn.test/x.svg)", out)

    def test_youtube_anchor_becomes_iframe(self):
        out = run(
            '<a href="https://www.youtube.com/watch?v=abc123XYZ_-">'
            '<img src="https://img.youtube.com/vi/abc123XYZ_-/hqdefault.jpg" alt="v"></a>'
        )
        self.assertIn(
            '<iframe allowfullscreen="allowfullscreen" '
            'src="https://www.youtube.com/embed/abc123XYZ_-" height="358" width="638"></iframe>',
            out,
        )

    def test_badge_link_becomes_markdown_badge(self):
        out = run('[<img alt="fabric" src="https://cdn.test/f.svg">](https://fabricmc.net/)')
        self.assertIn("[![fabric](https://cdn.test/f.svg)](https://fabricmc.net/)", out)

    def test_layout_tags_dropped_and_emphasis_lowered(self):
        out = run("<div align=\"center\"><b>bold</b><br><sub>small</sub></div>")
        self.assertNotIn("<div", out)
        self.assertNotIn("<sub", out)
        self.assertIn("**bold**", out)

    def test_no_em_dashes_introduced(self):
        out = run("plain text\n")
        self.assertNotIn("\u2014", out)


if __name__ == "__main__":
    unittest.main()
