from __future__ import annotations

import os
from uagents import Bureau

# Import all 5 agents
from agents.concierge import agent as concierge_agent
from agents.researcher import agent as researcher_agent
from agents.drafter import agent as drafter_agent
from agents.dispatcher import agent as dispatcher_agent
from agents.watcher import agent as watcher_agent
from common.db import init_db

if __name__ == "__main__":
    init_db()

    print("=" * 70)
    print("🚀 Starting ReclaimAI Multi-Agent Bureau (Fetch-A-Thon 3.0)")
    print("=" * 70)
    print(f"1. Concierge Agent:  {concierge_agent.address}")
    print(f"2. Researcher Agent: {researcher_agent.address}")
    print(f"3. Drafter Agent:    {drafter_agent.address}")
    print(f"4. Dispatcher Agent: {dispatcher_agent.address}")
    print(f"5. Watcher Agent:    {watcher_agent.address}")
    print("=" * 70)
    print("All agents are live and discoverable on Agentverse and ASI:One!")
    print("=" * 70)

    # Initialize Bureau to run all agents concurrently
    bureau = Bureau(port=8000, endpoint=["http://127.0.0.1:8000/submit"])
    bureau.add(concierge_agent)
    bureau.add(researcher_agent)
    bureau.add(drafter_agent)
    bureau.add(dispatcher_agent)
    bureau.add(watcher_agent)

    bureau.run()
