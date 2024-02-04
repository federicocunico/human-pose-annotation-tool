# Human pose annotation tool

## Requirements
1. Install [Node.js](https://nodejs.org/en/download/). If you want you can use `nvm` to manage multiple versions of Node.js. The project has been tested with **Node.js v21**, and **npm version 10.**

2. Install [Python3](https://www.python.org/downloads/). If you want you can use [miniconda3](https://docs.conda.io/en/latest/miniconda.html) to create a virtual environment. The project uses the new type-checking syntax, so you will need **Python 3.9** or later.

3. Install the python dependencies by executing `pip install -r requirements.txt` in the root directory of the project.

## Installation
1. Execute `npm install` in the root directory of the project to download the node modules.
2. Execute `npm run build` to build the project. This will create a `backend/dist` directory with the compiled files.

## Main server run
1. (Optional) Set your port in the script `backend/cfg.py` (default=51100).
2. Execute `python backend/server.py` to start the server. The server will be running on `http://localhost:51100`.

## Custom dataset support

The project supports custom datasets. To add a new dataset, you need to:

1. Create a new dataloader class that inherits from `backend.dataset.definition.AnnotationDataset` and implement all the abstract methods. 

2. Create a configuration yaml file. The configuration file should be placed in the `backend/configs/` directory. The configuration file should contain the following fields:

```yaml
name: "<dataset name (no spaces)>"
data_root: "<data root directory>"
dataloader_script: "<location of the dataloader>"
dataloader_class: "<name of the dataloader python class>"
joints_number: <integer, number of the joints to annotate per each image>
joints_links: <list of lists, each list contains the indexes of the joints that are connected. (Optional)>
joints_names: <list of strings, each string is the name of the joint. (Optional)>
```

## What if I don't have the 3D joints? Can I still use this tool to annotate my images?
Yes. Just provide the 3D data joints as empty lists. The tool will still work.


## Where are my annotations?

Each video file or image is annotated with a `<name>_annotation.pkl>` file, where `<name>` is the source file name. The file is a dictionary with the following fields:

