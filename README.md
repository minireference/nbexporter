# nbexporter
Tools for exporting Google Colab notebooks from gdrive to `.ipynb` files in a git repo.


## Features
- export notebooks from google drive (requires google oauth client setup, and provide secrets as ENV vars)


<!--
## Install

```bash
pip install nbexporter
```

You can now run the command line script `nbexporter`.

Future ideas...
```
nbexporter diff --old <path or url>  --new <path or url>
nbexporter archive --src <path or url> [--name filename]
```
-->

## Usage

```bash
# export multiple notebooks specified in a YTML manifest file
./nbexporter.py --manifest <path>

# same as above but also writes a README.md with binder and colab links
./nbexporter.py --manifest <path> --readme
```


TODOs
-----
- [ ] package as a reusable CLI program
- [ ] implement `archive` and `diff` commands



Roadmap
-------
- export to ordinary .py scripts (see https://github.com/minireference/noBSLAnotebooks/blob/master/util/makepynb.sh )
- diffs on text-based .py scripts
- export to MyST, see https://jupyterbook.org/intro.html


Stretch goals
-------------
- process notebooks to create learner version (no solutions) and solutions version
  see https://github.com/NeuromatchAcademy/nmaci/blob/main/scripts/process_notebooks.py#L226-L298
