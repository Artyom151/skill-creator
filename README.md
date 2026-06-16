# skill-creator

Interactive CLI tool for generating SKILL.md files for AI agents. Uses the OpenRouter API to create structured instruction documents.

## Requirements

- Python 3.9+
- OpenRouter API key

## Installation

```bash
git clone https://github.com/Artyom151/skill-creator.git
cd skill-creator
```

## Usage

Run the script:

```bash
python3 main.py
```

The tool will guide you through an interactive prompt asking for:

- Skill topic and description
- Target AI agent (e.g., Claude, ChatGPT)
- Document language
- Writing style preferences
- Custom rules and constraints
- Usage examples
- Metadata (author, version)

After generation, you can preview the result, request edits, regenerate, or save directly to `SKILL.md`.

## Configuration

The following constants are set at the top of `main.py`:

| Variable    | Description                    | Default                          |
|-------------|--------------------------------|----------------------------------|
| `API_KEY`   | OpenRouter API key            | (set to a provided key)         |
| `API_URL`   | API endpoint                   | `https://openrouter.ai/api/v1/chat/completions` |
| `MODEL`     | Model identifier               | `openai/gpt-oss-120b:free`      |
| `MAX_TOKENS`| Maximum response length        | `3000`                          |

## Features

- Interactive question-and-answer flow
- RGB gradient terminal banner with ASCII art
- Live spinner during API generation
- Preview with edit/regenerate loop
- Direct save to SKILL.md
- Keyboard interrupt handling

## License

MIT
