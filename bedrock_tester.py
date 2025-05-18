"""
Main script for testing Bedrock models with various prompts and input files.
"""

import os
import json
import uuid
import boto3
import datetime
from typing import List, Dict, Any
import config
from prompts import PROMPTS

def get_input_files() -> List[str]:
    """
    Get all text files from the source directory.
    
    Returns:
        List[str]: List of file paths
    """
    files = []
    for file in os.listdir(config.source_dir):
        if file.endswith('.txt'):
            files.append(os.path.join(config.source_dir, file))
    return files

def read_file_content(file_path: str) -> str:
    """
    Read content from a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Content of the file
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def invoke_bedrock_model(model_id: str, prompt: str) -> Dict[str, Any]:
    """
    Invoke a Bedrock model with the given prompt.
    
    Args:
        model_id (str): ID of the Bedrock model
        prompt (str): Prompt to send to the model
        
    Returns:
        Dict[str, Any]: Model response
    """
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=config.aws_region
    )
    
    # Different models have different request formats
    if model_id.startswith('anthropic.claude'):
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    elif model_id.startswith('amazon.nova'):
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    elif model_id.startswith('amazon.'):
        request_body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": config.max_tokens,
                "temperature": config.temperature,
                "topP": config.top_p
            }
        }
    elif model_id.startswith('ai21.'):
        request_body = {
            "prompt": prompt,
            "maxTokens": config.max_tokens,
            "temperature": config.temperature,
            "topP": config.top_p
        }
    elif model_id.startswith('cohere.'):
        request_body = {
            "prompt": prompt,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "p": config.top_p
        }
    elif model_id.startswith('meta.'):
        request_body = {
            "prompt": prompt,
            "max_gen_len": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p
        }
    elif model_id.startswith('mistral.'):
        request_body = {
            "prompt": prompt,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p
        }
    else:
        raise ValueError(f"Unsupported model ID: {model_id}")
    
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body)
    )
    
    response_body = json.loads(response.get('body').read())
    return response_body

def extract_model_response(model_id: str, response: Dict[str, Any]) -> str:
    """
    Extract the text response from the model's response object.
    
    Args:
        model_id (str): ID of the Bedrock model
        response (Dict[str, Any]): Model response
        
    Returns:
        str: Extracted text response
    """
    if model_id.startswith('anthropic.claude'):
        return response.get('content', [{}])[0].get('text', '')
    elif model_id.startswith('amazon.nova'):
        return response.get('content', [{}])[0].get('text', '')
    elif model_id.startswith('amazon.'):
        return response.get('results', [{}])[0].get('outputText', '')
    elif model_id.startswith('ai21.'):
        return response.get('completions', [{}])[0].get('data', {}).get('text', '')
    elif model_id.startswith('cohere.'):
        return response.get('generations', [{}])[0].get('text', '')
    elif model_id.startswith('meta.'):
        return response.get('generation', '')
    elif model_id.startswith('mistral.'):
        return response.get('outputs', [{}])[0].get('text', '')
    else:
        return str(response)

def save_result(input_file: str, model_id: str, prompt_name: str, 
                input_text: str, prompt: str, response: str, error_message: str = None,
                processing_time: float = None) -> str:
    """
    Save the test result to an output file. All results for the same input file
    are consolidated into a single output file.
    
    Args:
        input_file (str): Path to the input file
        model_id (str): ID of the Bedrock model
        prompt_name (str): Name of the prompt used
        input_text (str): Original input text
        prompt (str): Full prompt sent to the model
        response (str): Model's response
        error_message (str, optional): Error message if the model failed
        processing_time (float, optional): Time taken to process the request in seconds
        
    Returns:
        str: Path to the output file
    """
    # Create a filename based on the input file
    input_filename = os.path.basename(input_file).replace('.txt', '')
    output_filename = f"{config.output_prefix}{input_filename}_{prompt_name}.json"
    output_path = os.path.join(config.output_dir, output_filename)
    
    # Create or update the result object
    result = {}
    
    # If the file already exists, load its content
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            try:
                result = json.load(f)
            except json.JSONDecodeError:
                # If the file exists but is not valid JSON, start fresh
                result = {}
    
    # Initialize the structure if this is the first write
    if not result:
        result = {
            "input_file": input_file,
            "prompt_name": prompt_name,
            "input_text": input_text,
            "full_prompt": prompt,
            "responses": {},
            "errors": {},
            "processing_times": {},
            "metadata": {
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "last_updated": str(datetime.datetime.now())
            }
        }
    
    # Add or update this model's response or error
    if error_message is not None:
        result["errors"][model_id] = error_message
    else:
        result["responses"][model_id] = response
    
    # Add processing time if available
    if processing_time is not None:
        result["processing_times"][model_id] = processing_time
    
    result["metadata"]["last_updated"] = str(datetime.datetime.now())
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return output_path

def run_test(input_file: str, model_id: str = None, prompt_name: str = None) -> str:
    """
    Run a test with the given input file, model, and prompt.
    
    Args:
        input_file (str): Path to the input file
        model_id (str, optional): ID of the Bedrock model. Defaults to config.default_model_id.
        prompt_name (str, optional): Name of the prompt to use. Defaults to config.default_prompt_name.
        
    Returns:
        str: Path to the output file
    """
    # Use defaults if not specified
    model_id = model_id or config.default_model_id
    prompt_name = prompt_name or config.default_prompt_name
    
    # Get the prompt function
    if prompt_name not in PROMPTS:
        raise ValueError(f"Prompt '{prompt_name}' not found in prompts.py")
    prompt_func = PROMPTS[prompt_name]
    
    # Read the input file
    input_text = read_file_content(input_file)
    
    # Generate the prompt
    prompt = prompt_func(input_text)
    
    # Invoke the model
    print(f"Testing {model_id} with prompt '{prompt_name}' on file {os.path.basename(input_file)}...")
    
    try:
        # Start timing
        start_time = datetime.datetime.now()
        
        # Invoke model
        response_obj = invoke_bedrock_model(model_id, prompt)
        response_text = extract_model_response(model_id, response_obj)
        
        # End timing
        end_time = datetime.datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        error_message = None
    except Exception as e:
        print(f"Error testing {model_id} on {os.path.basename(input_file)}: {str(e)}")
        response_text = None
        error_message = str(e)
        processing_time = None
    
    # Save the result (even if there was an error)
    output_path = save_result(input_file, model_id, prompt_name, input_text, prompt, 
                             response_text, error_message, processing_time)
    
    if error_message is None:
        print(f"Result saved to {output_path} (processing time: {processing_time:.2f} seconds)")
    else:
        print(f"Error saved to {output_path}")
    
    return output_path

def run_all_tests():
    """
    Run tests for all input files using all models defined in config.model_ids.
    """
    # Ensure output directory exists
    os.makedirs(config.output_dir, exist_ok=True)
    
    # Get all input files
    input_files = get_input_files()
    
    if not input_files:
        print(f"No .txt files found in {config.source_dir}")
        return
    
    # Run tests for each file with each model
    for input_file in input_files:
        for model_id in config.model_ids:
            try:
                run_test(input_file, model_id=model_id)
            except Exception as e:
                print(f"Error testing {model_id} on {os.path.basename(input_file)}: {str(e)}")
                continue

def run_test_with_specific_model(model_id: str):
    """
    Run tests for all input files using a specific model.
    
    Args:
        model_id (str): ID of the Bedrock model to test
    """
    # Ensure output directory exists
    os.makedirs(config.output_dir, exist_ok=True)
    
    # Get all input files
    input_files = get_input_files()
    
    if not input_files:
        print(f"No .txt files found in {config.source_dir}")
        return
    
    # Run tests for each file with the specified model
    for input_file in input_files:
        try:
            run_test(input_file, model_id=model_id)
        except Exception as e:
            print(f"Error testing {model_id} on {os.path.basename(input_file)}: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Bedrock models with various prompts and input files')
    parser.add_argument('--model', type=str, help='Specific model ID to test')
    parser.add_argument('--all', action='store_true', help='Test all models')
    
    args = parser.parse_args()
    
    if args.model:
        if args.model in config.model_ids:
            print(f"Testing with specific model: {args.model}")
            run_test_with_specific_model(args.model)
        else:
            print(f"Model {args.model} not found in config.model_ids")
    elif args.all:
        print(f"Testing with all {len(config.model_ids)} models")
        run_all_tests()
    else:
        print(f"Testing with default model: {config.default_model_id}")
        run_test_with_specific_model(config.default_model_id)
