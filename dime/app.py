"""
Dime Application Entry Point

Main application module for the Dime content creation system.
Provides basic startup functionality to test agent system.
"""

from typing import Dict, Any
from publisher.agent import root_agent, researcher, writer


def get_agent_health() -> Dict[str, Any]:
    """Get health status of all agents."""
    return {
        "status": "healthy",
        "agents": {
            "root_agent": {
                "name": root_agent.name,
                "model": root_agent.model,
                "status": "active",
            },
            "researcher": {
                "name": researcher.name,
                "model": researcher.model,
                "status": "active",
            },
            "writer": {"name": writer.name, "model": writer.model, "status": "active"},
        },
    }


def main() -> None:
    """Main application function."""
    print("🔄 Starting Dime content creation system...")

    try:
        # Test agent instantiation
        health = get_agent_health()
        print("✅ Agent system initialized successfully!")
        print(f"📊 Health check: {health['status']}")
        print(f"🤖 Active agents: {len(health['agents'])}")

        # Print agent details
        for agent_key, agent_info in health["agents"].items():
            print(
                f"   - {agent_info['name']} ({agent_info['model']}) - {agent_info['status']}"
            )

        print("\n🎉 System startup completed successfully!")
        print("💡 Next steps:")
        print("   - Implement ADK web interface")
        print("   - Add agent tools and capabilities")
        print("   - Create comprehensive testing")

    except Exception as e:
        print(f"❌ Error during startup: {e}")
        raise


if __name__ == "__main__":
    main()
