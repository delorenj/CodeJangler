# CodeJangler

An AI-powered tool for optimizing and splitting large pull requests into smaller, more manageable pieces while maintaining logical coherence and proper dependency ordering.

## Features

- Intelligent PR analysis and split recommendations
- Automated dependency tracking and management
- Test coverage validation
- GitHub integration for seamless workflow
- Async processing support for large PRs

## Installation

```bash
pip install codejangler
```

## Usage

### Basic Usage

```bash
# Analyze and optimize a PR
codejangler optimize https://github.com/user/repo/pull/123

# Process asynchronously for large PRs
codejangler optimize --async https://github.com/user/repo/pull/123
```

### Advanced Features

```bash
# Train the model with example PRs
codejangler train https://github.com/user/repo/pull/123 -n 5 -o training_data.json

# Test optimization strategies
codejangler test https://github.com/user/repo/pull/123 --model gemini-1.5-pro
```

## Configuration

Set up your environment variables:

```bash
export GITHUB_TOKEN=your_github_token
export GEMINI_API_KEY=your_gemini_key
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/codejangler/codejangler.git
cd codejangler

# Install development dependencies
pip install -e ".[dev]"
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=pr_optimizer
```

### Code Style

```bash
# Format code
black .
isort .

# Lint code
ruff check .

# Type checking
mypy .
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
