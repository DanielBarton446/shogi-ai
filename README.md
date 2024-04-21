# shogi-ai


# Usage

Currently, you simply can watch an Agent play against random moves
locally. This is done with:
`python3 -m venv .venv`
`source .venv/bin/activate`
`pip install -r requirements.txt`
`python3 main.py`

If you plan on developing at all with this, ensure you install the dev
requirements to use formatters, linters, and performance analysis tools.
`pip install -r dev_requirements.txt`

# Integrations

Currently, there are no integrations with any websites for playing shogi. 
There is a goal to have an integration with Lishogi to allow for using
these agents to play online.

# Goals

- Lishogi Integration
- MCTS Agent
- Alpha-Beta Pruning Agent
- Reinforcement learning based Agent
