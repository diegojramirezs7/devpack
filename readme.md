## Dev Pack
Tool that helps developers add appropriate agent skills to an existing repo based on the detected tech stack.

Eventually, it will also help developers start new projects providing different tech stack options.
It helps you integrate your personal or organizational best practices and preferred tools seamlessly.

It will help developers enforce framework specific best practices.

## Setup

### 1. Install

```bash
uv sync
```

### 2. Configure your API key

Copy the example env file and add your Anthropic API key:

```bash
cp .env.example .env
```

Then edit `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

You can get an API key at [console.anthropic.com](https://console.anthropic.com).

### 3. Run

```bash
devpack add-skills /path/to/your/repo
```

DevPack will analyze your repo with Claude and prompt you to select matching agent skills to install.
