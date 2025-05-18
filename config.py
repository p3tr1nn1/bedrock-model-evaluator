"""
Configuration file for Bedrock model testing.
This file contains all configurable parameters for the testing framework.
"""

import os

# Directory configurations
# source_dir: Directory where your input text files are located
source_dir = "source-files"

# output_dir: Directory where the results will be saved
output_dir = "outputs-summary"

# Output file configuration
# output_prefix: Prefix added to all output filenames before the random string
output_prefix = "bedrock_result_"

# AWS Bedrock configuration
# default_model_id: The model to use if none is specified
default_model_id = "anthropic.claude-3-haiku-20240307-v1:0"

# aws_region: AWS region where Bedrock is available
aws_region = "us-east-1"

# Testing parameters
# max_tokens: Maximum number of tokens to generate in the response
max_tokens = 2048

# temperature: Controls randomness (0.0-1.0). Lower is more deterministic
temperature = 0.7

# top_p: Controls diversity via nucleus sampling
top_p = 0.9

# timeout_seconds: Maximum time to wait for API response
timeout_seconds = 30

# model_ids: List of available Bedrock models to test
# These are loaded from model_ids.txt
model_ids = [
    "amazon.titan-text-premier-v1:0",
    "amazon.nova-pro-v1:0",
    "amazon.nova-lite-v1:0",
    "amazon.nova-micro-v1:0",
    "amazon.titan-text-lite-v1",
    "amazon.titan-text-express-v1",
    "ai21.jamba-1-5-large-v1:0",
    "ai21.jamba-1-5-mini-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "cohere.command-text-v14",
    "cohere.command-r-v1:0",
    "cohere.command-r-plus-v1:0",
    "cohere.command-light-text-v14",
    "meta.llama3-8b-instruct-v1:0",
    "meta.llama3-70b-instruct-v1:0",
    "mistral.mistral-7b-instruct-v0:2",
    "mistral.mixtral-8x7b-instruct-v0:1",
    "mistral.mistral-large-2402-v1:0",
    "mistral.mistral-small-2402-v1:0"
]

# default_prompt_name: Name of the default prompt to use
default_prompt_name = "default_summary"
