from utils.openai_utils import openai_call
import json
from copy import deepcopy


async def generate_dag(messages: list, tools: list):
    messages = deepcopy(messages)
    tools = deepcopy(tools)
    tools = [json.dumps(tool) for tool in tools]
    tool_string = "# TOOL LIST #:\n"
    tool_string += "\n".join(tools)

    system_prompt = ("You are an expert in understanding any task flow and "
                     "creating a defined structured format for its execution")

    prompt = tool_string + """

    The above conversation describes how the user achieves a particular task using an example. We need to create a defined flow taking any generic example as input.
    ENSURE ALL TASK_STEPS in latest TASK_STEPS are used to create task_steps. Length must be the same
    # GOAL #:
    Based on the above tools and the above conversation, I want you generate task steps, task nodes and task links to capture the complete flow that the user describes.
    The format must be a strict JSON, like: 
    {
        "task_name": "name of the task",
        "input": "comma separated unique input args required for executing the task_steps",
        "task_steps": [ "concrete steps, format as Step x: Call xxx tool with xxx: 'xxx' and xxx: 'xxx'" ], 
        "task_nodes": [{"task_id":"TASK_ followed by unique identifier for this task, follow 1-indexing", "task": "task name must be from # TOOL LIST #", "name": "define a unique name for this task", "arguments": [ {"name": "parameter name", "value": "parameter value, either a placeholder to be filled by user defined by curly braces or the exact task_id of the tool whose result is required by this node"} ]}], 
        "task_links": [{"source": "source task i task_id", "target": "target task j task_id"}]
    }
    """

    prompt += """
    # REQUIREMENTS #: 
    1. the generated task steps and task nodes can resolve for the given user input. Task name must be selected from # TOOL LIST #; 
    2. the task steps should strictly aligned with the task nodes, and the number of task steps should be same with the task nodes; 
    3. the dependencies among task steps should align with the argument dependencies of the task nodes.
    4. ensure all the steps are covered.
    5. make the first task step take in general input instead of a particular usecase.
    6. avoid using execute_python_code unless it is for mathematical reasoning.
    7. only respond the json, say nothing else
    8. the task nodes and task steps when connected should create only one connected graph."""

    if messages[0]["role"] != "system":
        messages = [{"role": "system", "content": system_prompt}] + messages
    messages += [{"role": "user", "content": prompt}]

    _response, _ = await openai_call(system_prompt, messages)
    dag_string = _response["results"]
    if dag_string.startswith("```json"):
        dag_string = dag_string[len("```json"):-3]
    dag_json = json.loads(dag_string)
    return dag_json
