# nbexporter
Tools for exporing and diffing Jupyter notebooks stored in gdrive to a git repo.



## Install

```bash
pip install -r requirements.txt
pip install jupyter
pip install jedi==0.17.2
```


## Usage

Edit the info in `EXPORT_MANIFEST` inside `./nbexporter.py` to set the file list
to export and `destdir` where to export the files.

```bash
./nbexporter.py
```


TODOs
-----

- [ ] make export manifest an external .yaml file
- [ ] package as a reusable CLI program
- [ ] add `archive` and `diff` commands

 
