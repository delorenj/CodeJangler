# CodeJangler

CodeJangler is a CLI tool that uses AI to optimize large GitHub pull requests by intelligently splitting them into smaller, more manageable pieces. It leverages CrewAI to orchestrate a team of specialized AI agents that analyze, split, and validate the PR splits.

## Features

- 🔍 Intelligent PR analysis to identify logical split points
- 🔀 Automated PR splitting based on code dependencies
- ✅ Quality validation of split PRs
- 🤖 AI-powered decision making for optimal splits
- 🔄 Maintains git history and commit integrity
- 📊 Dependency-aware split sequencing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/codejangler.git
cd codejangler
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

## Configuration

1. Set up required environment variables:
```bash
export GITHUB_TOKEN=your_github_token
export OPENAI_API_KEY=your_openai_key
```

2. (Optional) Create a custom configuration file:
```yaml
# config.yaml
name: Custom PR Optimizer
description: Custom configuration for PR optimization
# ... additional configuration
```

## Usage

### Basic Usage

Optimize a pull request:
```bash
codejangler optimize https://github.com/user/repo/pull/123
```

### Advanced Usage

Run in async mode:
```bash
codejangler optimize https://github.com/user/repo/pull/123 --async
```

Use custom configuration:
```bash
codejangler optimize https://github.com/user/repo/pull/123 --config custom_config.yaml
```

## How It Works

CodeJangler uses a team of specialized AI agents:

1. **PR Analyzer**
   - Analyzes code changes and dependencies
   - Identifies logical boundaries for splits
   - Considers test coverage and risks

2. **PR Splitter**
   - Creates optimal split strategy
   - Executes git operations
   - Maintains commit history

3. **PR Reviewer**
   - Validates split quality
   - Ensures maintainability
   - Verifies test coverage

## Development

### Setup Development Environment

1. Clone and install dependencies:
```bash
git clone https://github.com/yourusername/codejangler.git
cd codejangler
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

2. Run tests:
```bash
pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) for the AI agent orchestration framework
- The open source community for various tools and libraries used in this project

## Support

- 📚 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/codejangler/issues)
- 💬 [Discussions](https://github.com/yourusername/codejangler/discussions)
