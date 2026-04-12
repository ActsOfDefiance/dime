"""
Filesystem tools for agents.

Wraps FileSystemAdapter methods as ADK FunctionTool instances so agents
can read, write, and list files in the article workspace.
"""

import posixpath

from dime.adapters.protocols import FileSystemAdapter


def _sanitize_path(path: str) -> str:
    """Sanitize a path to prevent traversal outside the workspace.

    Rejects absolute paths and paths containing '..' components.

    Raises:
        ValueError: If the path attempts directory traversal.
    """
    normalized = posixpath.normpath(path)
    if normalized.startswith("/") or normalized.startswith(".."):
        raise ValueError(f"Invalid path: '{path}' escapes the workspace.")
    return normalized


def make_read_tool(fs: FileSystemAdapter) -> object:
    """Create a tool that reads a file from the article workspace."""

    def read_file(path: str) -> str:
        """Read a file from the article workspace.

        Args:
            path: Relative path within the workspace (e.g. "research.md").

        Returns:
            The file contents as a string, or an error message if not found.
        """
        try:
            safe_path = _sanitize_path(path)
        except ValueError as e:
            return f"Error: {e}"
        if not fs.exists(safe_path):
            return f"Error: file '{safe_path}' does not exist."
        return fs.read(safe_path)

    return read_file


def make_write_tool(fs: FileSystemAdapter) -> object:
    """Create a tool that writes a file to the article workspace."""

    def write_file(path: str, content: str) -> str:
        """Write content to a file in the article workspace.

        Args:
            path: Relative path within the workspace (e.g. "research.md").
            content: The text content to write.

        Returns:
            Confirmation message.
        """
        try:
            safe_path = _sanitize_path(path)
        except ValueError as e:
            return f"Error: {e}"
        fs.write(safe_path, content)
        return f"Successfully wrote {len(content)} characters to '{safe_path}'."

    return write_file


def make_list_tool(fs: FileSystemAdapter) -> object:
    """Create a tool that lists files in the article workspace."""

    def list_files(prefix: str) -> str:
        """List files in the article workspace under a given prefix.

        Args:
            prefix: Directory prefix to list (e.g. "art/" or "").

        Returns:
            Newline-separated list of file paths, or a message if empty.
        """
        try:
            safe_prefix = _sanitize_path(prefix) if prefix else ""
        except ValueError as e:
            return f"Error: {e}"
        files = fs.list(safe_prefix)
        if not files:
            return f"No files found under '{safe_prefix}'."
        return "\n".join(files)

    return list_files
