"""
Filesystem tools for agents.

Wraps FileSystemAdapter methods as ADK FunctionTool instances so agents
can read, write, and list files in the article workspace.
"""

from dime.adapters.protocols import FileSystemAdapter


def make_read_tool(fs: FileSystemAdapter) -> object:
    """Create a tool that reads a file from the article workspace."""

    def read_file(path: str) -> str:
        """Read a file from the article workspace.

        Args:
            path: Relative path within the workspace (e.g. "research.md").

        Returns:
            The file contents as a string, or an error message if not found.
        """
        if not fs.exists(path):
            return f"Error: file '{path}' does not exist."
        return fs.read(path)

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
        fs.write(path, content)
        return f"Successfully wrote {len(content)} characters to '{path}'."

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
        files = fs.list(prefix)
        if not files:
            return f"No files found under '{prefix}'."
        return "\n".join(files)

    return list_files
