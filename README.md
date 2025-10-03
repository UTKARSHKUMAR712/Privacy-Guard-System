# Privacy Guard System 🛡️

A Python-based privacy protection system that uses camera motion detection to automatically close applications when someone approaches your computer.

## Features

- 📷 **Multi-Camera Support**: Switch between laptop and phone cameras
- 🎯 **Smart Motion Detection**: Advanced OpenCV-based detection
- 🔒 **Application Control**: Safely close or minimize applications
- ⚙️ **Configurable**: Adjustable sensitivity and settings
- 🚀 **Auto-Start**: Windows startup integration
- 📊 **Logging**: Detailed activity logs
- 🧪 **Testing Tools**: Built-in camera testing utilities

## Quick Start

1.  **Ensure Python 3.8+ is installed**:
    ```bash
    python --version
    ```
2.  **Run Setup**:
    ```bash
    python setup.py
    ```
    This will install all necessary Python packages and create required directories.
3.  **Connect your phone (Optional)**: If using a phone camera, connect it via Windows Phone Link.
4.  **Test your camera(s)**:
    ```bash
    python test_camera.py
    ```
5.  **Start Privacy Guard**:
    ```bash
    python privacy_guard.py
    ```

## Installation

### Prerequisites

-   Python 3.8 or higher (Python 3.12+ is supported with special `setuptools` handling).
-   Windows operating system (for `pywin32` and application control features).

### Steps

1.  **Clone the repository (or download the source code)**:
    ```bash
    git clone https://github.com/UTKARSHKUMAR712/Privacy-Guard-System.git
    cd Privacy-Guard-System
    ```
2.  **Run the setup script**:
    ```bash
    python setup.py
    ```
    This script will:
    -   Check your Python version.
    -   Install required Python packages (`opencv-python`, `psutil`, `pywin32`, `numpy`).
    -   Create `logs/` and `config/` directories.

## Configuration

Settings are stored in `config/settings.json`. If the file doesn't exist, it will be created with default values on first run.

| Setting                | Description                                                              | Default Value |
| :--------------------- | :----------------------------------------------------------------------- | :------------ |
| `camera_index`         | Index of the camera to use (0 for laptop, 1+ for phone/external).        | `1`           |
| `motion_sensitivity`   | Threshold for motion detection (500-5000). Higher value means less sensitive. | `1500`        |
| `detection_delay`      | Minimum seconds between privacy breach detections to prevent spam.       | `5`           |
| `auto_close_apps`      | If `True`, applications will be closed/minimized on detection.           | `True`        |
| `show_camera_feed`     | If `True`, displays the camera feed with detection status.               | `True`        |
| `enable_notifications` | If `True`, enables system notifications (not yet implemented).           | `True`        |
| `log_level`            | Logging level (`INFO`, `DEBUG`, `WARNING`, `ERROR`).                     | `INFO`        |
| `protected_processes`  | List of processes that will NOT be closed or minimized.                  | (System processes) |
| `target_applications`  | List of applications to be considered for closing/minimizing.            | (Common browsers/apps) |
| `force_close_list`     | List of applications to always force close (not just minimize).          | (Specific games/apps) |

## Phone Camera Setup (Windows Phone Link)

1.  Install the "Phone Link" app on both your Windows PC and Android phone.
2.  Pair your devices through the Phone Link app.
3.  Enable camera sharing in the Phone Link settings.
4.  Your phone camera will typically appear as camera index `1` or `2` in the Privacy Guard system.

## Usage

### Running Privacy Guard

```bash
python privacy_guard.py
```

### Command Line Options

-   **Run with default settings**:
    ```bash
    python privacy_guard.py
    ```
-   **Use a specific camera**:
    ```bash
    python privacy_guard.py --camera [INDEX] May change order
    # Example: python privacy_guard.py --camera 0 (for laptop camera)
    # Example: python privacy_guard.py --camera 1 (for phone/external camera)
    ```
-   **Test cameras interactively**:
    ```bash
    python privacy_guard.py --test
    ```
    This will run `test_camera.py` for an interactive camera test.
-   **Show help message**:
    ```bash
    python privacy_guard.py --help
    ```

### Runtime Controls (when Privacy Guard is running)

-   `q` - Quit the application.
-   `c` - Change the active camera source.
-   `s` - Adjust the motion detection sensitivity.
-   `t` - Toggle test mode (shows detection status without taking action).
-   `h` - Hide/Show the camera feed window.

## Troubleshooting

-   **Python 3.12+ issues**: If you encounter issues, try running `pip install setuptools` and `pip install --upgrade pip` before `python setup.py`.
-   **Missing dependencies**: Ensure all packages from `requirements.txt` are installed. Run `python setup.py` again.
-   **Camera not found**: Verify your camera index. Use `python privacy_guard.py --test` to find available cameras.
-   **`pywin32` errors**: This project is designed for Windows. `pywin32` is a Windows-specific library.

## Contributing

Feel free to fork the repository, open issues, or submit pull requests.

## License

This project is licensed under the [LICENSE](LICENSE) file.
