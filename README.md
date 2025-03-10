# AutoTestCase Generator

An intelligent agent for automatically generating test cases and exporting them to Excel or XMind formats.

## Features

- Automatically generate test cases from requirement descriptions
- Support multiple export formats (Excel, XMind)
- Intelligent analysis of requirements
- Generate both positive and negative test scenarios
- Priority-based test case organization

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file with your OpenAI API key
```

## Usage

```python
from src.core.test_generator import TestGenerator
from src.exporters.excel_exporter import ExcelExporter
from src.core.llm_engine import LLMEngine

# Initialize components
llm_engine = LLMEngine()
test_generator = TestGenerator(llm_engine)
excel_exporter = ExcelExporter()

# Generate test cases
requirements = """
Your requirement description here
"""

test_cases = test_generator.generate_test_cases(requirements)

# Export to Excel
excel_exporter.export(test_cases, "test_cases.xlsx")
```

## Project Structure

```
AutoTestCase/
├── README.md
├── requirements.txt
├── src/
│   ├── core/           # Core functionality
│   ├── exporters/      # Export handlers
│   └── utils/          # Utility functions
└── tests/              # Unit tests
```

## Contributing

Feel free to submit issues and enhancement requests.

## License

MIT License 