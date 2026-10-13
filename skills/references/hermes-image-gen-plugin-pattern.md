# Hermes Image Generation Plugin Pattern

## How to create a new image_gen provider plugin

### 1. Directory structure

```
hermes-agent/plugins/image_gen/<name>/
├── __init__.py      # Plugin implementation
└── plugin.yaml      # Plugin manifest
```

### 2. plugin.yaml

```yaml
name: <name>
version: 1.0.0
description: "Description of the provider"
author: Hermes Agent
kind: backend
requires_env:
  - API_KEY_NAME
```

### 3. __init__.py — Minimum viable plugin

```python
from agent.image_gen_provider import (
    ImageGenProvider,
    success_response,
    error_response,
    save_url_image,
)

class MyProvider(ImageGenProvider):
    @property
    def name(self) -> str:
        return "myprovider"

    @property
    def display_name(self) -> str:
        return "My Provider"

    def is_available(self) -> bool:
        return bool(os.environ.get("MY_API_KEY"))

    def list_models(self):
        return [{"id": "model-1", "display": "Model 1"}]

    def default_model(self):
        return "model-1"

    def get_setup_schema(self):
        return {
            "name": "My Provider",
            "badge": "paid",
            "env_vars": [{"key": "MY_API_KEY", "prompt": "API key", "url": "..."}],
        }

    def generate(self, prompt, aspect_ratio="landscape", **kwargs):
        # 1. Call API
        # 2. Download result (use save_url_image for URL-based providers)
        # 3. Return success_response(image=path, model=..., prompt=..., ...)
        pass

def register(ctx):
    ctx.register_image_gen_provider(MyProvider())
```

### 4. Key details

- `save_url_image(url)` downloads and caches to `$HERMES_HOME/cache/images/`
- `save_b64_image(data)` decodes and caches base64 images
- Aspect ratios: `"landscape"` (16:9), `"square"` (1:1), `"portrait"` (9:16)
- Provider must return `success_response()` or `error_response()` dict
- Enable with `hermes plugins enable image_gen/<name>`
- Takes effect on next session (restart required)

### 5. Pitfalls

- `MINIMAX_CN_BASE_URL` has `/anthropic` suffix — strip it for non-Anthropic endpoints
- SSL issues on Windows: use `ssl.create_default_context()` with `check_hostname=False`
- Plugin changes require session restart to take effect
- `config.yaml` is write-protected — use `hermes config set` not `write_file`
