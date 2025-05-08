# Tracing and Debugging with Weights & Biases

DevSeeker can integrate with Weights & Biases (W&B) to capture prompt inputs, model outputs, and execution traces of your LLM chains for comprehensive analysis.

## Setup W&B

Sign up for free at https://wandb.ai and retrieve your API key.

```bash
export WANDB_API_KEY=your_wandb_api_key
export LANGCHAIN_WANDB_TRACING=true
```

## Running DevSeeker with W&B

Run DevSeeker in your project directory:

```bash
devseeker my-project
```

W&B will automatically log your runs. Visit https://wandb.ai to view prompts, responses, and trace visualizations. 