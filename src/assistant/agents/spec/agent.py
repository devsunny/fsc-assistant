import click

from assistant.llm.client import llmclient

from .prompts import SPECT_PROMPT
from io import StringIO

from assistant.utils.cli.console import CLIConsole
from assistant.utils.path import find_spec_file, find_spec_folder, get_project_root


def create_software_development_spec(
    draft_requirement: str,
    programming_language: str = "python, typescript",
    tech_stack: str = "python, fastapi, vue3.js, fastmcp, openai",
    runtime: str = "docker",
    database: str = "postgresql",
    must_have: str = "None",
    persona: str = "regular user",
) -> str:
    """generate comprehensive software development spec by given basic informations"""
    print("start creating software spec")
    prompt = SPECT_PROMPT.format(
        draft_requirement=draft_requirement,
        programming_language=programming_language,
        tech_stack=tech_stack,
        runtime=runtime,
        database=database,
        must_have=must_have,
        persona=persona,
    )

    response = llmclient.invoke_model_stream_with_return(
        prompt=prompt, max_completion_tokens=30000
    )
    file_name = response.splitlines()[-1][13:].strip()
    spec_folder = find_spec_folder(get_project_root())
    file_path = spec_folder / file_name
    print(f"saving software spec to {file_path}")
    file_path.write_text(response, encoding="utf-8")

    return f"spec saved to {file_path}"


@click.command
@click.option("--draft-requirements", type=str, help="Draft requirements")
@click.option(
    "--programming-language", type=str, help="specify the programming language"
)
@click.option("--tech-stack", type=str, help="Tech Stack used in the implementation")
@click.option(
    "--runtime",
    type=str,
    help="runtime environment, docker, k8s, eks, serverless, bare metal, and aws ec2 etc.",
    default="docker",
)
@click.option(
    "--database",
    type=str,
    help="database backend, postgresql, mysql, ms sql server and oracle etc.",
    default=None,
)
@click.option(
    "--must-have",
    type=str,
    help="Must have functions, such as OAuth2, OpenID authentication with Google, Github etc.",
    default=None,
)
@click.option(
    "--persona", type=str, help="devops, regular user, and admin etc.", default=None
)
def generate_spec(
    draft_requirements: str,
    programming_language: str,
    tech_stack: str,
    runtime: str,
    database: str,
    must_have: str,
    persona: str,
):
    cli_console = CLIConsole()
    while not draft_requirements:
        draft_requirements = cli_console.get_multiline_input(
            "enter your requirement draft"
        )

    if not programming_language:
        programming_language = cli_console.prompt_input("Enter programming languages")

    if not tech_stack:
        tech_stack = cli_console.prompt_input(
            "What tech stacks? python, flask, vue3.js etc"
        )

    if not runtime:
        runtime = cli_console.prompt_input(
            "What runtime environemnt? docker k8s, serverless etc."
        )

    if not database:
        database = cli_console.prompt_input(
            "What backend database? postgresql, ms sql server, mysql etc."
        )

    if not must_have:
        must_have = cli_console.prompt_input("What must have in your mind?")

    if not persona:
        persona = cli_console.prompt_input("What persona is this feature for?")

    create_software_development_spec(
        draft_requirements,
        programming_language=programming_language,
        tech_stack=tech_stack,
        runtime=runtime,
        database=database,
        must_have=must_have,
        persona=persona,
    )
