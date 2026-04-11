"""
Dime CLI Entry Point

Command-line interface for the Dime Content Creation System.
Provides simple commands to start the web server and check system health.
"""

import argparse
import uvicorn
from dime.app import create_app
from dime.config import get_settings


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Dime Content Creation System")
    parser.add_argument("--host", default=None, help="Host to bind to")
    parser.add_argument("--port", type=int, default=None, help="Port to bind to")
    parser.add_argument(
        "command",
        nargs="?",
        default="start",
        choices=["start", "health"],
        help="Command to run",
    )

    args = parser.parse_args()
    settings = get_settings()

    if args.command == "health":
        # Simple health check
        print("✅ Configuration loaded successfully")
        print(f"📁 Database: {settings.get_database_url(hide_password=True)}")
        print(f"🤖 Agent: {settings.AGENT_NAME}")
        print(f"🌍 Environment: {settings.APP_ENVIRONMENT}")
        return

    # Start FastAPI server
    app = create_app()
    uvicorn.run(
        app, host=args.host or settings.APP_HOST, port=args.port or settings.APP_PORT
    )


if __name__ == "__main__":
    main()
