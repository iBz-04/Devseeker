# Using Open or Local Models

DevSeeker supports OpenAI's hosted models by default. You can also integrate open-source or local LLMs through an OpenAI-compatible API.

## Local Models with llama.cpp

Install and serve models locally using llama.cpp:

### Install Dependencies

```bash
pip install llama-cpp-python
pip install llama-cpp-python[server]
```

### Download Model Weights

Obtain a GGUF model file (e.g., CodeLlama-13B-GGUF) and place it on your machine.

### Start the Local API Server

```bash
python -m llama_cpp.server --model /path/to/model.gguf --n_batch 256 --n_gpu_layers 30
```

### Configure DevSeeker

```bash
export OPENAI_API_BASE="http://localhost:8000/v1"
export OPENAI_API_KEY="sk-your_local_key"
export MODEL_NAME="CodeLlama"
export LOCAL_MODEL=true
```

### Run DevSeeker

```bash
devseeker my-project
```

## Hosted Open Router Models

To use Open Router models:

```bash
export OPENAI_API_BASE="https://openrouter.ai/api/v1"
export OPENAI_API_KEY="your_openrouter_key"
export MODEL_NAME="meta-llama/llama-3-8b-instruct:extended"
export LOCAL_MODEL=true

devseeker my-project
```

## Azure OpenAI Models

To use Azure OpenAI:

```bash
export OPENAI_API_BASE="https://<your-resource-name>.openai.azure.com"
export OPENAI_API_KEY="your_azure_api_key"
export LOCAL_MODEL=false

devseeker --azure https://<your-resource-name>.openai.azure.com my-project <deployment_name>
``` 