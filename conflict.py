from crfm import crfmChatLLM
# import openai
from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
from langchain.schema import (
    HumanMessage,
    SystemMessage,
)
import random

llm = crfmChatLLM(model_name=f"openai/gpt-4-0613")

problems = ["Conflict: A conversation between a customer and employee. The blender is not working and the customer wants to return."]
roles = [["employee", "customer"]]

random_problem = random.choice(problems)

curr_problem = random_problem
curr_roles = roles[0]
curr_student = curr_roles[0]
curr_opponent = curr_roles[1]

student_details = "Resolve the conflict and be helpful"
opponent_details = "Be adversarial and aggressive in problem solving"

context_student = """
Prompt:
You are a chatbot that realistically roleplays a virtual conflict.

Each message must use only one of the following strategies:

The following positive strategies increase cooperativeness:
- Interests
- Positive Expectations
- Proposal

The following neutral strategies do not change cooperativeness:
- Concession
- Facts

The following negative strategies decrease cooperativeness:
- Rights
- Power

You will roleplay as {curr_student}. 

Your opponent will also have a cooperativeness level from 1 (very uncooperative) - 5 (very cooperative).

These are the rules for your opponent:

Cooperativeness score rules:
- If cooperativeness is low, negative strategies are used.
- If cooperativeness is high, positive strategies are used.
- If several positive strategies are used, {curr_opponent} slowly becomes more cooperative.
- Continuing to repeatedly use positive expectations without proposing something will not increase cooperativeness
- {curr_opponent} will not use positive strategies or try to solve the problem (e.g. ask questions) until cooperativeness is 3 or greater.
- If negative strategies are used, {curr_opponent} will retaliate with a negative strategy.
- Otherwise, {curr_opponent}'s cooperativeness will stay the same.

Do NOT assume anything about the conversation. Only make inferences based on the summary of {curr_opponent} and the prior messages.

Messages must only use one strategy at a time.

Format your message as follows. Only complete the <fill in> fields. Copy all fields that do not have a <fill in> value.

Thoughts: <fill in>
Message: <fill in>
"""

context_opponent = """
Prompt:
You are a chatbot that realistically roleplays a virtual conflict.

Each message must use only one of the following strategies:

The following positive strategies increase cooperativeness:
- Interests
- Positive Expectations
- Proposal

The following neutral strategies do not change cooperativeness:
- Concession
- Facts

The following negative strategies decrease cooperativeness:
- Rights
- Power

You will roleplay as {curr_opponent}:

You will have a cooperativeness level from 1 (very uncooperative) - 5 (very cooperative).

Cooperativeness score rules:
- If cooperativeness is low, negative strategies are used.
- If cooperativeness is high, positive strategies are used.
- If several positive strategies are used, you become more cooperative.
- Continuing to repeatedly use positive expectations without proposing something will not increase cooperativeness
- You must not use positive strategies or try to solve the problem (e.g. ask questions) until cooperativeness is 3 or greater.
- If negative strategies are used, You will retaliate with a negative strategy.
- Otherwise, your cooperativeness will stay the same.

Summary of your role: 
{curr_opponent} : {opponent_details}

Do NOT assume anything about the conversation. Only make inferences based on the summary of yourself, and the prior messages.

Messages must only use one strategy at a time.

Format your message as follows. Only complete the <fill in> fields. Copy all fields that do not have a <fill in> value.

Thoughts: <fill in>
Message: <fill in>
"""

problem_description = random_problem + context_student.format(
    curr_student=curr_student,
    curr_opponent=curr_opponent,
    opponent_details=opponent_details
)

problem_description_opponent = random_problem + context_opponent.format(
    curr_opponent=curr_opponent,
    opponent_details=opponent_details
)

class Student:
    def __init__(self, role, student_details) -> None:
        self.role = role
        self.student_details = student_details

    def get_response(self, instruction, conversation_history) -> str:
        system_template = """
        Use the conversation history and the instruction from teacher to respond. You are the {role}, 
        and you have the following details: {student_details}. 
        Instruction from teacher: {instruction}. Follow the instruction from the teacher and respond in the following format:
        Thought:<thought>
        Message:<answer>
        For example:
        Thought: <fill in>
        Message: <fill in>
        """

        user_template = f"{problem_description}\n{conversation_history}\nInstruction to follow: {instruction}"
        system_message = system_template.format(role=self.role, student_details=self.student_details, instruction=instruction)
        user_message = user_template.format(problem_description=problem_description, conversation_history=conversation_history, instruction=instruction)
        messages = [SystemMessage(content=system_message), HumanMessage(content=user_message)]
        response = llm.generate([messages], stop=["Q:"]).generations[0][0].text
        return response

class Opponent:
    def  __init__(self, problem, role, opponent_details) -> None:
        self.problem = problem
        self.role = role
        self.opponent_details = opponent_details
    
    def get_response(self, conversation_history) -> str:
        system_template = '''
        Use the conversation history and the context to respond. You are the {role}. 
        and you have the following details: {opponent_details}. 
        Respond in the following format:
        Thought:<thought>
        Message:<answer>
        For example:
        Thought: <fill in>
        Message: <fill in>
        '''
        system_message_content =  f"\n Context: {problem_description_opponent}\nConversation History: {conversation_history}\n"
        messages = [
            SystemMessage(content=system_message_content),
            HumanMessage(content="\n".join(conversation_history))
        ]
        response = llm.generate([messages], stop=["Q:"]).generations[0][0].text

        return response

class Teacher:
    def  __init__(self, problem) -> None:
        self.problem = problem
        self.mutation_prompt = """Help the agent resolve the conflict in the best way possible for the above problem.
            Come up with a number of unique strategies for the agent to test out in each iteration of conflict. 
            These strategies should all be unique from one another, an example would be "be aggressive, and do not back down, until the opponent becomes more cooperative"
            or "employ neutral strategies for 3 iterations until the tone cools down", but more specific to what you assume would be useful. 
            Come up with ten of these strategies that you think would be the most helpful for us to test out. Make sure they are complete and comprehensive.
            Respond in the following format:
            Instructions:
            1. 
            ...
            10. 
            """ 
    def parse_instructions(self, response):
        instructions = response.split("Instuctions:")[-1]
        instructions = [instruction.strip() for instruction in instructions.split('\n')]
        return instructions

    def get_instructions(self):
        system_template = "You are trying to help the agent resolve the conflict. You must come up with strategies to help resolve the conflict. The problem they see is this: {problem}."
        system_message = system_template.format(problem=self.problem)
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=self.mutation_prompt)
        ]            
        instructions = llm.generate([messages], stop=["Q:"]).generations[0][0].text
        instructions = self.parse_instructions(instructions)
        return instructions

class Judge: 
    def  __init__(self):
        self.prompt = """Two agents are having a conflict, this will be passed in in the form of a list. 

        Your job is to rate on a scale from 1 to 10 how well they resolved the conflict.

        You should also add a qualitative descriptor of what they did well.

        This is the conversation: 
        
        """
    def generate_response(self, context):
        messages = [
            SystemMessage(content=self.prompt),
            HumanMessage(content="\n".join(context))
        ]
        response = llm.generate([messages], stop=["Q:"]).generations[0][0].text
        return response.strip()

def parse_responses(role, response):
    answer = response.split("Message: ")[-1].strip()
    return role + ": " + answer

def parse_thoughts(role, response):
    thought = response.split("Thought: ")[-1].strip()
    return role + ": " + thought

teacher = Teacher(problem_description)
teacher_instructions = teacher.get_instructions()

student = Student(curr_student, student_details)
opponent = Opponent(problem_description, curr_opponent, opponent_details)
judge = Judge()

cleaned_list = [item for item in teacher_instructions if item]
cleaned_list = cleaned_list[1:]
teacher_instructions = [item.split('. ', 1)[1].strip() for item in cleaned_list]

instruction_dict = {}

num_instruction = 0
for instruction in teacher_instructions:
    num_instruction+=1
    print(f"Instruction Number {num_instruction}")
    print(instruction)
    for i in range(5):
        print(f"Conversation {i}")
        # if len(instruction) <3:
        #     continue

        conversation_history = []
        # instruction = teacher_instructions[0]

        strategy_history = []

        for i in range(5):
            student_response = student.get_response(conversation_history, instruction)
            parsed_response = parse_responses(curr_student, student_response)
            parsed_strategy = parse_thoughts(curr_student, student_response)
            conversation_history.append(parsed_response)
            strategy_history.append(parsed_strategy)

            opponent_response = opponent.get_response(conversation_history)
            conversation_history.append(parse_responses(curr_opponent, opponent_response))
            parsed_strategy = parse_thoughts(curr_opponent, opponent_response)
            strategy_history.append(parsed_strategy)
        print(instruction)
        num = 1
        for line in conversation_history:
            print(f'{num}\n')
            print(line)
            num += 1
        final = judge.generate_response(conversation_history)
        final_judge_response = final.split("\n\n")
        instruction_dict[instruction] = final_judge_response
        print('\n')
        print(final_judge_response)
        

# print(instruction_dict)
