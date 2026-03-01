# Publishing Capability

**Status:** active

Content pipeline (draft → review → approved → published) with mandatory review gate, and zo.space page helper for generating page/API route configurations.

## Components

- `pipelines/content_pipeline.py` — State machine for content lifecycle
- `pipelines/zo_space.py` — zo.space page and API route generator
- `config.yaml` — Review requirements, visibility defaults

## API Surface

### Content Pipeline

```python
from Zoffice.capabilities.publishing.pipelines.content_pipeline import ContentPipeline

p = ContentPipeline()
item_id = p.create_item(content, slug, author=None) -> str
new_state = p.advance(item_id, event) -> str  # Raises ValueError on invalid transition
item = p.get_item(item_id) -> dict
items = p.list_items(state=None) -> list[dict]
```

Events: submit_for_review, approve, reject, publish, archive

### zo.space Helper

```python
from Zoffice.capabilities.publishing.pipelines.zo_space import prepare_page, prepare_api_route

page = prepare_page(path, title, content, public=False) -> dict
route = prepare_api_route(path, handler_description) -> dict
```
