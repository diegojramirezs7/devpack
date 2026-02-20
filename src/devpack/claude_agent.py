import os
from pathlib import Path

from dotenv import load_dotenv
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

load_dotenv()

from devpack.models import StackDetectionResult
from devpack.registry.known_ids import KNOWN_TECHNOLOGY_IDS


def _build_detection_prompt() -> str:
    known_ids_formatted = ", ".join(KNOWN_TECHNOLOGY_IDS)
    return f"""
    Analyze the repository and identify the technologies, frameworks, and tools used.

    Use the Read, Glob, and Grep tools to inspect:
    - Package manifests: package.json, requirements.txt, pyproject.toml, Gemfile, go.mod, Cargo.toml, composer.json
    - Config files: tsconfig.json, docker-compose.yml, .env*, *.config.js
    - Key source files to confirm actual usage, not just listed dependencies

    Only report technologies clearly present in the project.

    You MUST use ONLY the following technology IDs — do not invent new ones:
    {known_ids_formatted}

    For is_frontend, set true for: javascript, typescript, react, vue, nextjs, vite, angular.

    In the summary field, write 1-2 sentences describing the project's stack \
    (e.g. "A Django REST API backed by PostgreSQL, containerized with Docker.").
    """


def _build_json_schema() -> dict:
    schema = StackDetectionResult.model_json_schema()

    def add_no_additional_properties(obj: dict) -> None:
        if isinstance(obj, dict):
            if obj.get("type") == "object":
                obj["additionalProperties"] = False
            for value in obj.values():
                if isinstance(value, dict):
                    add_no_additional_properties(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            add_no_additional_properties(item)

    add_no_additional_properties(schema)
    return schema


async def detect_tech_stack(repo_path: Path) -> StackDetectionResult:
    """Run a Claude agent against repo_path and return a validated StackDetectionResult."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. Add it to a .env file or export it:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-..."
        )

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        cwd=str(repo_path),
        output_format={
            "type": "json_schema",
            "schema": _build_json_schema(),
        },
    )

    structured_output = None
    result_subtype = None

    async for message in query(prompt=_build_detection_prompt(), options=options):
        if isinstance(message, ResultMessage):
            structured_output = message.structured_output
            result_subtype = message.subtype

    if result_subtype == "error_max_structured_output_retries":
        raise ValueError(
            "Claude could not produce a valid stack detection response after multiple attempts. "
            "Check that the repository is accessible and try again."
        )

    if structured_output is None:
        raise ValueError(
            f"Claude did not return structured output (subtype: {result_subtype}). "
            "Ensure the repository path is correct and the API key is valid."
        )

    return StackDetectionResult.model_validate(structured_output)
