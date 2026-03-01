"""
Publishing — zo.space Page Helper

Generates page and API route configurations for zo.space.
Does NOT call update_space_route — prepares the config for rice-integration.
"""


def prepare_page(
    path: str,
    title: str,
    content: str,
    public: bool = False,
    style: str = "default",
) -> dict:
    """
    Generate a zo.space page configuration.

    Returns:
        dict with: path, route_type, code (TSX string), public
    """
    code = f"""export default function Page() {{
  return (
    <div style={{{{ maxWidth: '800px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui' }}}}>
      <h1>{title}</h1>
      <div>{content}</div>
    </div>
  );
}}"""

    return {
        "path": path,
        "route_type": "page",
        "code": code,
        "public": public,
        "title": title,
    }


def prepare_api_route(path: str, handler_description: str) -> dict:
    """
    Generate a zo.space API route configuration.

    Returns:
        dict with: path, route_type, code (handler string), public
    """
    code = f"""// API Route: {path}
// {handler_description}
export default async function handler(req: Request) {{
  return new Response(JSON.stringify({{ status: 'ok', path: '{path}' }}), {{
    headers: {{ 'Content-Type': 'application/json' }}
  }});
}}"""

    return {
        "path": path,
        "route_type": "api",
        "code": code,
        "public": True,
        "description": handler_description,
    }
