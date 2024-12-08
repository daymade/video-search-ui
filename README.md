# Video Search UI

A FastAPI-based web application providing a clean interface for video content search.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/daymade/video-search-ui.git
cd video-search-ui
```

## Project Structure

```
video-search-ui/
├── main.py           # Main FastAPI application
├── environment.yml   # Conda environment configuration
├── requirements.txt  # Python package dependencies
├── LICENSE          # MIT License
└── .gitignore       # Git ignore rules

Note: The `static` directory will be automatically generated when running the application.
```

## Setup

1. Create and activate conda environment:
```bash
conda env create -f environment.yml
conda activate video-search-ui-env
```

2. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:8000`

## Dependencies

The project uses the following core dependencies:
- `fastapi` - Web framework for building APIs
- `uvicorn` - ASGI server for running the application
- `httpx` - Modern HTTP client

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
