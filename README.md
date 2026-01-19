# File Organizer

A Python GUI application to organize files in a directory by their types into categorized subfolders.

## Features

- **Graphical User Interface**: Easy-to-use Tkinter-based GUI with modern styling.
- **Configurable Categories**: Customize file categories and extensions via the GUI.
- **Dry Run Mode**: Preview organization without moving files.
- **Ignore List**: Automatically skips system files and hidden files.
- **Error Handling**: Robust handling of file move errors.
- **Menu Bar**: Keyboard shortcuts for common actions.

## Requirements

- Python 3.x
- Standard libraries: `os`, `shutil`, `tkinter`, `json`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/file-organizer.git
   cd file-organizer
   ```

2. Run the script:
   ```
   python File_organizer.py
   ```

## Usage

1. Launch the application.
2. Select a directory to organize using File > Select Directory or Ctrl+O.
3. (Optional) Configure categories via Edit > Configure Categories or Ctrl+C.
4. Check "Dry Run" for preview mode.
5. Click "Organize Files" to sort files into subfolders.

## Configuration

- Categories and extensions are stored in `config.json`.
- Edit this file or use the GUI to customize.

## Contributing

Feel free to fork and submit pull requests!

## License

MIT License