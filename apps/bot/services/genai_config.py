from google import genai
from google.genai import types


tools = [
    types.Tool(url_context=types.UrlContext),
    types.Tool(google_search=types.GoogleSearch)
]

safety_settings = [
    types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="BLOCK_ONLY_HIGH",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_ONLY_HIGH",
    ),
]

config = types.GenerateContentConfig(
    max_output_tokens=None,
    top_k=2,
    top_p=0.5,
    temperature=0.5,
    seed=None,
    tools=tools,
    safety_settings=safety_settings,
    response_modalities=['TEXT'],
    response_mime_type="application/json",
)