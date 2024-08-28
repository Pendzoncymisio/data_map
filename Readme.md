# Data Map

Data Map is a user-friendly WYSIWYG documentation-as-code solution for data pipelines.

## Installation

To install Data Map, you can use pip and the provided requirements file.

1. Clone the repository:

    ```shell
    git clone git@github.com:Pendzoncymisio/data_map.git
    ```

2. Navigate to the project directory:

    ```shell
    cd project-name
    ```

3. Install the required dependencies using pip:

    ```shell
    pip install -r requirements.txt
    ```

Bugfixes for installation

1. `AttributeError: module 'sipbuild.api' has no attribute 'prepare_metadata_for_build_wheel'`
Fix: `pip install --upgrade pip setuptools wheel`

## GUI Usage

Simply run main.py with Python.

## CLI Usage

You can run main.py from console with the following additional arguments:

- `--export`: Exports visualization into jpg without opening GUI.
- `--group`: Loads only elements of group for visualization.

## Output file structure

Documentation is saved in JSON objects of objects. Plural, as documentation can be split into multiple files, that will be read as long as they have common root catalog.\

Data Map cares about those fields within objects:
- `icon`: Path to the icon
- `group`: Parent group.
- `sources`: List of IDs of data sources. Will create arrow from each source node.
- `link`: So you can open it in browser with one click.
- `viz`: Object of coordinates relative to parent group (or window for root nodes).

## Contributing

# Compile with Nuitka

`nuitka main.py --onefile --standalone --static-libpython=no --plugin-enable=pyqt6`

## License

...

## Contact

...
