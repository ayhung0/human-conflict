from crfm import crfmChatLLM

from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
from langchain.schema import (
    HumanMessage,
    SystemMessage,
)
import random

class MatrixGame:
   def __init__(self, payoff_matrix) -> None:
      self.matrix = payoff_matrix

   def get_question(self):
      payoff_str = "Q: Gopher and Bob are playing a game. Gopher and Bob get rewards according to these rules:\n\n"

      for i, (gopher_reward, bob_reward) in enumerate(self.matrix):
            gopher_action = 'a1' if i // 2 == 0 else 'a2'
            bob_action = 'a1' if i % 2 == 0 else 'a2'
            payoff_str += f"{i+1}. If Gopher chooses action {gopher_action} and Bob chooses action {bob_action}, then Gopher's reward is {gopher_reward} and Bob's reward is {bob_reward}\n"

      payoff_str += "Gopher and Bob can play either a1 or a2. They play their actions simultaneously."
      payoff_str += "What action should Gopher play if it wants to gain the highest reward?"

      return payoff_str

   def get_reward(self, gopher_action, bob_action):
      payoff_matrix = self.matrix
      action_map = {'a1': 0, 'a2': 1}

      gopher_index = action_map[gopher_action]
      bob_index = action_map[bob_action]

      # Retrieve the rewards from the payoff matrix
      gopher_reward, bob_reward = payoff_matrix[gopher_index * 2 + bob_index]

      return gopher_reward, bob_reward

class Student:
   def  __init__(self) -> None:
      pass 

   def parse_actions(self, response):
         answer = response.split("Answer: ")[-1].strip()
         digits = [char for char in answer if char.isdigit()]
         action = int(digits[-1]) - 1  
         if action == 0:
            return 'a1'
         else:
            return 'a2'

   def get_action(self, instruction, question) -> str: 
      # Calls language model with instruction, returns action 
      system_template = """Follow the instruction from the teacher and respond in the following format:
Thought:<thought>
Answer:<answer>
For example:
Thought: <thought>
Answer: a1

Instruction from teacher: {instruction}"""
      user_template = f"{question}\nInstruction to follow: {instruction}"
      system_message = system_template.format(instruction=instruction)
      user_message = user_template.format(instruction=instruction, question=question)
      messages = [SystemMessage(content=system_message), HumanMessage(user_message)]
      response = llm.generate([messages], stop=["Q:"]).generations[0][0].text
      action = self.parse_actions(response)
      return action

class Opponent:
   def  __init__(self) -> None:
      pass 
   def get_action(self) -> str:
      return random.choice(['a1', 'a2'])
   
class Teacher:
   def  __init__(self, question) -> None:
      self.thinking_style = ""
      self.problem = question 
      self.mutation_prompt = """Help the student agent get the maximum reward for the above problem.
Write possible instructions or strategies that the agent should follow.
Respond in the following format:
Instructions:
1. 
...
n. 
""" 

   def parse_instructions(self, response):
      instructions = response.split("Instuctions:")[-1]
      instructions = [instruction.strip() for instruction in instructions.split('\n')]
      return instructions

   def get_instructions(self):
      # Generate a list of instructions 
      system_template = "You are trying to help Gopher get the maximum reward. The problem that Gopher sees is this: {problem}"
      system_message = system_template.format(problem=self.problem)
      messages = [SystemMessage(content=system_message), HumanMessage(content=self.mutation_prompt)]
      instructions = llm.generate([messages], stop=["Q:"]).generations[0][0].text
      instructions = self.parse_instructions(instructions)
      return instructions
      
def maximize_player_reward(payoff_matrix, player):
   max_reward = float('-inf')
   best_action = None

   for action, rewards in enumerate(payoff_matrix):
      reward = rewards[player]
      if reward > max_reward:
          max_reward = reward
          best_action = action

   return best_action

# Example payoff matrix
payoff_matrix = [
  (-3, 2),
  (-1, -4),
  (1, 2),
  (3, 4)
]

llm = crfmChatLLM(model_name=f"openai/gpt-4-0613")

# Initialize task
matrix_game = MatrixGame(payoff_matrix)

# Initialize opponent agent
opponent = Opponent()

# Initialize student agent
student = Student()

# Initialize teacher agent
question = matrix_game.get_question()
teacher = Teacher(question)


# Get instuction prompts
candidate_instructions = teacher.get_instructions()

instruction_fitness = []
for instruction in candidate_instructions:
   action = student.get_action(instruction, question)
   opp_action = opponent.get_action()
   reward = matrix_game.get_reward(action, opp_action)
   instruction_fitness.append(reward)
   print(instruction, reward[0])
