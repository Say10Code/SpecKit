#!/usr/bin/env python3
"""Auto-apply F1 fix to docling page_preprocessing_model.py.
Run after: uv tool install --reinstall 3gpp-crawler
The fix wraps page.get_image() calls in try/except to survive
std::bad_alloc from pypdfium2 on pages with complex diagrams.
"""
import sys
from pathlib import Path


def find_docling_preprocessing() -> Path | None:
    """Locate the installed docling page_preprocessing_model.py."""
    import shutil

    # Check uv tool environments
    uv_tools = Path.home() / ".local" / "share" / "uv" / "tools"
    candidates = [
        Path.home() / "AppData" / "Roaming" / "uv" / "tools",  # Windows
        uv_tools,
        Path.home() / ".local" / "pipx" / "venvs",
    ]

    for base in candidates:
        if not base.exists():
            continue
        for tool_dir in base.iterdir():
            target = (
                tool_dir
                / "Lib" / "site-packages"
                / "docling" / "models" / "stages"
                / "page_preprocessing" / "page_preprocessing_model.py"
            )
            if target.exists():
                return target

    # Fallback: try import
    try:
        import docling

        return (
            Path(docling.__file__).parent
            / "models" / "stages" / "page_preprocessing"
            / "page_preprocessing_model.py"
        )
    except ImportError:
        return None


def is_patched(filepath: Path) -> bool:
    """Check if the try/except is already present."""
    text = filepath.read_text(encoding="utf-8")
    return "except Exception" in text and "page.get_image(" in text


def apply_patch(filepath: Path) -> bool:
    """Wrap page.get_image() calls in try/except Exception."""
    text = filepath.read_text(encoding="utf-8")
    original = text

    # Pattern 1: page.get_image(scale=1.0) without try/except
    # Pattern 2: page.get_image(scale=images_scale) without try/except

    # Replace the _populate_page_images method
    old_method = '''    def _populate_page_images(self, page: Page) -> Page:
        # default scale
        page.get_image(
            scale=1.0
        )  # puts the page image on the image cache at default scale

        images_scale = self.options.images_scale
        # user requested scales
        if images_scale is not None:
            page._default_image_scale = images_scale
            page.get_image(
                scale=images_scale
            )  # this will trigger storing the image in the internal cache

        return page'''

    new_method = '''    def _populate_page_images(self, page: Page) -> Page:
        # default scale
        try:
            page.get_image(
                scale=1.0
            )  # puts the page image on the image cache at default scale
        except Exception:
            pass

        images_scale = self.options.images_scale
        # user requested scales
        if images_scale is not None:
            page._default_image_scale = images_scale
            try:
                page.get_image(
                    scale=images_scale
                )  # this will trigger storing the image in the internal cache
            except Exception:
                pass

        return page'''

    if old_method in text:
        text = text.replace(old_method, new_method)
        filepath.write_text(text, encoding="utf-8")
        return True

    # Maybe already partially patched — check if we need to patch
    if "try:" not in text.split("def _populate_page_images")[1].split("def _")[0]:
        print("  WARNING: _populate_page_images signature changed — manual check needed")
        return False

    return False


def main():
    target = find_docling_preprocessing()
    if target is None:
        print("ERROR: Could not find docling installation.")
        print("Install 3gpp-crawler first: uv tool install 3gpp-crawler")
        sys.exit(1)

    print(f"Target: {target}")

    if is_patched(target):
        print("F1 fix already applied — nothing to do.")
        sys.exit(0)

    print("F1 fix NOT found. Applying...")
    if apply_patch(target):
        print("F1 fix applied successfully.")
    else:
        print("WARNING: Could not auto-apply F1 fix (method signature may have changed).")
        print("Manual fix: wrap page.get_image() calls in try/except Exception in _populate_page_images().")
        sys.exit(1)


if __name__ == "__main__":
    main()
