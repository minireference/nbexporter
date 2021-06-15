# nbexporter
Tools for exporing [archiving, diffing] Jupyter notebooks stored in gdrive to a git repo.


## Features
- export notebooks from google drive (requires google oauth client setup, and provide secrets as ENV vars)
- (optional) process notebooks to create learner version (no solutions) and coach versions (with solutoins):
  see https://github.com/NeuromatchAcademy/course-content/blob/master/ci/process_notebooks.py#L7-L8


## Install

```bash
pip install nbexporter
```

You can now run the command line script `nbexporter`.


## Usage

```bash
nbexporter export --src <url> --dest <path>

# save to archives/YYYY-MM-DD/filenme.ipynb
nbexporter archive --src <path or url> [--name filename]

# export multiple notebooks specified in a "manifest" file
nbexporter export --manifest <path>
# or if you do this often...
export EXPORT_MANIFEST="exercises.yaml"; nbexporter export 

# diffs for y'all!
nbexporter diff --old <path or url>  --new <path or url>

```



TODOs
-----

- [ ] make export manifest an external .yaml file
- [ ] package as a reusable CLI program
- [ ] add `archive` and `diff` commands

 



Roadmap
-------
- export to ordinary .py scripts (see https://github.com/minireference/noBSLAnotebooks/blob/master/util/makepynb.sh )
- diffs on text-based .py scripts
- export to MyST, see https://jupyterbook.org/intro.html





