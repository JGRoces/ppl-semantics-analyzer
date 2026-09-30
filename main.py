"""Start Paradigm Diagnostics in one persistent native window.

Application owns the only Tk root and event loop. Entry and workspace are child
pages, so opening the workspace never closes or recreates the native window.
"""

from ui.application import Application


def main() -> None:
    """Run the entry page and workspace through one application event loop.

    Args:
        None.
    Returns:
        None after the user closes the application.
    """
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
