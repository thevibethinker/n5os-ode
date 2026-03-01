# Communication Templates

Templates use `{{variable}}` syntax for substitution.

## Available Variables

- `{{name}}` — Recipient or contact name
- `{{topic}}` — Subject or topic of the communication
- `{{content}}` — Main content body
- `{{employee_or_human}}` — The person/employee being escalated to

## Usage

```python
from Zoffice.capabilities.communication.channels.dispatch import render_template

rendered = render_template("acknowledgment", {"name": "Jane", "topic": "your inquiry"})
```
