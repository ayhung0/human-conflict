# human-conflict
Exploring and advancing human interaction strategies by simulating conversations between language models. Discovering and optimizing effective strategies for improved conflict resolution and interaction quality.

## Overview
The project includes two main components:

Matrix Game Simulation: This component models a strategic decision-making scenario where two agents, Gopher and Bob, choose actions to maximize their rewards according to a payoff matrix. The simulation provides insights into optimal strategies for reward maximization.

Conflict Resolution Simulation: Building on the matrix game framework, this component simulates and evaluates conflict resolution strategies between two virtual agents. The system roleplays conflicts based on predefined scenarios and strategies, refining agent interactions to enhance conflict resolution effectiveness.

## Components

### Matrix Game Simulation (matrix_game.py)
This component involves a game where two players (Gopher and Bob) choose actions to maximize their rewards based on a payoff matrix. The system helps the player (Gopher) to determine the best action to achieve the highest reward.

Classes:

MatrixGame: Defines the game and calculates rewards based on actions.

Student: Provides instructions to the agent for choosing the best action.

Opponent: Randomly chooses an action.

Teacher: Generates instructions for the student agent.

### Conflict Resolution Simulation (conflict.py)
This part of the code models a conversation between two agents (student and opponent) in a conflict scenario. The agents use various strategies to resolve the conflict, and their interactions are evaluated based on predefined rules.

Classes:

Student: Represents the student agent, which follows instructions to resolve conflicts.

Opponent: Represents the opposing agent, which responds based on the current state of the conversation.

Teacher: Generates strategies for the student agent to resolve the conflict.

Judge: Evaluates the outcome of the conflict resolution based on the conversation history.
