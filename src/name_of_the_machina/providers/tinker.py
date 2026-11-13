# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import json
import urllib.request
import urllib.error
from os import environ


api_key = environ.get("TINKER_API_KEY", '')
default_model = environ.get("TINKER_DEFAULT_MODEL", 'thinkingmachines/Inkling')
api_base_oai = environ.get("TINKER_OAI_API_BASE", 'https://tinker.thinkingmachines.dev/services/tinker-prod/oai/api/v1')
api_base_ant = environ.get("TINKER_ANT_API_BASE", 'https://tinker.thinkingmachines.dev/services/tinker-prod/anthropic/api/v1')


# Set the mandatory headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "User-Agent": "machine-thinking"
}


def get_function(func_name):
    # Look up tool by name in globals
    func = globals().get(func_name)
    # Look up in the caller frames
    if not func:
        import inspect
        frame = inspect.currentframe().f_back
        while frame:
            if func_name in frame.f_globals:
                func = frame.f_globals[func_name]
                break
            frame = frame.f_back

    return func


def get_func_args(func_args_def):
    try:
        if isinstance(func_args_def, str):
            func_args = json.loads(func_args_def)
        else:
            func_args = func_args_def
    except Exception as e:
        func_args = {}
        print(f"Error parsing tool arguments: {e}")

    return func_args


def call_function(func, func_args):
    if func and callable(func):
        try:
            tool_result = func(**func_args)
            if isinstance(tool_result, (dict, list)):
                result = json.dumps(tool_result)
            else:
                result = str(tool_result)
        except Exception as e:
            result = f"Error executing tool: {str(e)}"
            print(result)
    else:
        result = f"Error: Tool function not callable."
        print(result)

    return result


def query(payload, url_suffix, url_prefix=None):
    # Convert data dictionary to JSON and encode it to bytes
    if url_prefix:
        api_base = url_prefix
    else:
        api_base= api_base_oai
    data_bytes = json.dumps(payload).encode('utf-8')
    # Create the Request object
    req = urllib.request.Request(
        f'{api_base}{url_suffix}',
        data=data_bytes,
        headers=headers,
        method="POST")
    # Try to query
    try:
        # Execute the request
        with urllib.request.urlopen(req, timeout=3000) as response:
            response_data = response.read().decode('utf-8')
            output = json.loads(response_data)
        return output

    except urllib.error.HTTPError as e:
        # Handle HTTP errors (e.g., 401 Unauthorized, 400 Bad Request)
        error_info = e.read().decode('utf-8', errors='ignore')
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Error Details: {error_info}")
        return {}

    except urllib.error.URLError as e:
        # Handle network/connection errors
        print(f"Failed to reach the server: {e.reason}")
        return {}


def decode(output):
    text = ''
    thoughts = ''
    for chunk in output:
        chunk_type = chunk.get('type', '')
        if chunk_type == 'text':
            addition = chunk.get('text', '')
            if addition not in ('\n\n', '\n'):
                text += addition

        elif chunk_type == 'thinking':
            thoughts += chunk.get('thinking', '')
    function_calls = [part for part in output if part['type'] == 'tool_use']

    return thoughts, text, function_calls


def decode_output(output):
    # Parse the result
    text = ''; thoughts = ''
    for part in output:
        part_type = part.get('type', None)
        if part_type == 'message':
            text = " ".join([chunk['text'] for chunk in part['content'] if chunk['type'] == 'output_text'])
        elif part_type == 'reasoning':
            thoughts = " ".join([chunk['text'] for chunk in part['summary'] if chunk['type'] == 'summary_text'])
    function_calls = [part for part in output if part['type'] == 'function_call']
    return thoughts, text, function_calls


def respond(messages=None, instructions=None, tools=None, **kwargs):
    """
    """
    instruction         = kwargs.get('system_instruction', instructions)
    first_message       = [dict(role='system', content=instruction)] if instruction else []

    # contents can come in kwards or as an argument
    messages            = kwargs.get('messages', messages)

    first_message.extend(messages)
    instruction_and_contents = first_message

    payload = {
        'model': kwargs.get('model', default_model),
        'messages': instruction_and_contents,
        # 'response_format':          kwargs.get('response_format',{'type': 'text'}),
        'temperature': kwargs.get('temperature', 1),  # 0.0 to 2.0
        'max_tokens': kwargs.get('max_tokens', 4096),
        'top_p': kwargs.get('top_p', 0.9),
        'separate_reasoning': True,
        'reasoning_effort': kwargs.get('reasoning_effort', 'high'),  # 'low', 'medium', 'high'
        'stream': False
    }
    if tools:
        payload['tools'] = tools
        payload['parallel_tool_calls'] = True
        payload['tool_choice'] = 'auto'

    while True:
        result = query(payload, '/chat/completions')
        completion_message = result['choices'][0]['message']
        instruction_and_contents.append(completion_message)
        thoughts = completion_message.get('reasoning_content', '')
        text = completion_message.get('content', '')
        function_calls = completion_message.get('tool_calls', [])

        if function_calls:
            # Call all requested functions and create response messages.
            for function_call in function_calls:
                call_id = function_call.get('id')
                func_def = function_call.get('function')
                func_name = func_def.get('name', '')
                func_args_str = func_def.get('arguments', {})
                # Look up tool by name in globals and caller frames
                func = get_function(func_name)
                func_args = get_func_args(func_args_str)
                result = call_function(func, func_args)

                tool_message = {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": result
                }
                instruction_and_contents.append(tool_message)
        else:
            break

    return thoughts, text


if __name__ == '__main__':
   ...
