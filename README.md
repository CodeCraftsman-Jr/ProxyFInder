# ProxyFinder 🔍

A Python script that automatically fetches proxy lists from the [TheSpeedX/PROXY-List](https://github.com/TheSpeedX/PROXY-List) repository, tests them against Google sites, and stores only the working proxies.

## Features

- 🚀 **Multi-threaded Testing**: Tests multiple proxies concurrently for faster results
- 🎯 **Google Site Testing**: Validates proxies against Google sites to ensure they work
- 📁 **Multiple Output Formats**: Saves results in both JSON (detailed) and TXT (simple) formats
- 🔄 **Daily Updates**: Source repository updates daily with fresh proxies
- ⚙️ **Configurable**: Customizable timeout, thread count, and test URLs
- 📊 **Detailed Reports**: Generates summary reports with statistics and fastest proxies
- 🏃 **Quick Mode**: Fast testing option for quicker results

## Supported Proxy Types

- **HTTP** proxies
- **SOCKS4** proxies
- **SOCKS5** proxies

## Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/your-username/ProxyFinder.git
   cd ProxyFinder
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the main script to test all proxy types:
```bash
python proxy_finder.py
```

### Windows Users

Double-click the `run_proxy_finder.bat` file or run it from command prompt:
```cmd
run_proxy_finder.bat
```

### Advanced Usage

Use the quick proxy finder with options:

```bash
# Test only HTTP proxies
python quick_proxy_finder.py --type http

# Test only SOCKS5 proxies
python quick_proxy_finder.py --type socks5

# Quick mode (faster, less thorough)
python quick_proxy_finder.py --quick

# Custom settings
python quick_proxy_finder.py --workers 100 --timeout 15

# Help
python quick_proxy_finder.py --help
```

### Command Line Options

- `--type` or `-t`: Proxy type to test (`http`, `socks4`, `socks5`, `all`)
- `--workers` or `-w`: Number of concurrent workers (default: 50)
- `--timeout`: Timeout in seconds for each proxy test (default: 10)
- `--quick` or `-q`: Quick mode for faster results

## Output

The script creates a `working_proxies` folder with the following files:

### For each proxy type:
- `working_[type]_[timestamp].txt` - Simple list of working proxies
- `working_[type]_[timestamp].json` - Detailed information including response times
- `working_[type]_latest.txt` - Latest working proxies (overwritten each run)
- `working_[type]_latest.json` - Latest detailed results (overwritten each run)

### Summary:
- `summary_[timestamp].json` - Overall statistics and fastest proxies

### Example Output Structure:
```
working_proxies/
├── working_http_20250817_143022.txt
├── working_http_20250817_143022.json
├── working_http_latest.txt
├── working_http_latest.json
├── working_socks4_20250817_143022.txt
├── working_socks4_20250817_143022.json
├── working_socks4_latest.txt
├── working_socks4_latest.json
├── working_socks5_20250817_143022.txt
├── working_socks5_20250817_143022.json
├── working_socks5_latest.txt
├── working_socks5_latest.json
└── summary_20250817_143022.json
```

## Configuration

Edit `config.json` to customize settings:

```json
{
  "settings": {
    "timeout": 10,
    "max_workers": 50,
    "test_urls": [
      "https://www.google.com",
      "https://google.com"
    ],
    "output_directory": "working_proxies"
  }
}
```

## Example JSON Output

```json
[
  {
    "proxy": "192.168.1.1:8080",
    "type": "http",
    "response_time": 1.23,
    "tested_at": "2025-08-17T14:30:22.123456"
  }
]
```

## Performance Tips

1. **Adjust Worker Count**: Increase `--workers` for faster testing (but don't exceed your system's capabilities)
2. **Use Quick Mode**: Use `--quick` flag for faster results when you need proxies quickly
3. **Specific Proxy Types**: Test only the proxy type you need (e.g., `--type http`)
4. **Timeout Settings**: Lower timeout for faster testing, higher for more thorough testing

## Requirements

- Python 3.7+
- `requests` library
- `concurrent.futures` (included in Python 3.2+)

## Source

Proxy lists are fetched from:
- **Repository**: [TheSpeedX/PROXY-List](https://github.com/TheSpeedX/PROXY-List)
- **Updates**: Daily
- **Total Proxies**: 40,000+ (varies daily)

## Legal Notice

This tool is for educational purposes only. The proxies are publicly available and sourced from the internet. Users are responsible for complying with their local laws and the terms of service of the websites they access through these proxies.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source. Please give credit if you use this code.

## Troubleshooting

### Common Issues:

1. **"No working proxies found"**
   - Try increasing the timeout value
   - Check your internet connection
   - The proxy list might be temporarily unavailable

2. **"Slow performance"**
   - Reduce the number of workers
   - Use quick mode
   - Test specific proxy types instead of all

3. **"Connection errors"**
   - Check if the source repository is accessible
   - Verify your internet connection
   - Try running with fewer concurrent workers

## Statistics

The script typically finds:
- **HTTP Proxies**: 5-15% working rate
- **SOCKS4 Proxies**: 3-10% working rate  
- **SOCKS5 Proxies**: 2-8% working rate

*Note: Working rates vary based on the freshness of the proxy list and testing conditions.*