"""The existing index answer shape, enforced during generation and validation."""

from index_common import require


def object_schema(properties):
    return {"type": "object", "properties": properties, "required": list(properties),
            "additionalProperties": False}


STRING = {"type": "string"}
REFS = {"type": "array", "items": STRING}
ENTRY = object_schema({
    "headword": STRING, "display": STRING, "see": {"type": ["string", "null"]},
    "pages": REFS, "subentries": {"type": "array", "items": object_schema({
        "text": STRING, "pages": REFS})}})
PARSE_SCHEMA = object_schema({"entries": {"type": "array", "items": ENTRY}})

# Request-local controls, not global reader/model configuration.
PARSE_CONTROLS = {"response_schema": PARSE_SCHEMA, "no_reasoning": True,
                  "temperature": 0.7, "top_p": 0.8, "presence_penalty": 1.5,
                  "timeout": 300}


def check_shape(answer):
    require(isinstance(answer, dict) and set(answer) == {"entries"},
            "index answer must contain only entries; stray top-level entry fields lose data")
    require(isinstance(answer["entries"], list), "entries must be a list")
    for row in answer["entries"]:
        require(isinstance(row, dict) and set(row) == set(ENTRY["properties"]),
                "index entry must have exactly the six schema fields")
