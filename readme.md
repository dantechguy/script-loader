# Script loader

*Create config files with preconfigured commands to quickly setup a server*

#### Usage

1. Create a `*.json` config file.

The largest object are "groups", here we have the groups `"clonegithubrepos"` and `"dockerfiles"`.

Within each group are "tasks". A task has a `"description"` of its function, and a list of `"commands"` to execute within the given `"path"`.

Tasks can have the optional `"mods"` attribute, to specify special functioning when executing:
- `"ignoreerror"` will continue execution even if one of the commands in the task throws an error
- `"verbose"` will override global level and output max verbose debug info
- `"skip"` will skip the entire task and not execute any commands 

```json
{
    
  "clonegithubrepos": 
    [ 
        
      {
        "description": "remove demo directory",
        "path": "./",
        "mods": ["ignoreerror"],
        "commands": [
          "rm -rf demo"
        ]
      },
      
      {
        "description": "make demo directory",
        "path": "./",
        "commands": [
          "mkdir demo"
        ]
      },
      
      {
        "description": "clone demo github repo",
        "path": "./demo",
        "commands": [
          "git clone https://github.com/shekhargulati/python-flask-docker-hello-world.git"
        ]
      }
      
    ],
  
  "dockerfiles": 
  [ 
    {
      "description": "setup docker files",
      "path": "./demo",
      "commands": [
          "docker build -t simple-flask-app:latest .",
          "docker run -d -p 5000:5000 simple-flask-app"
      ]
    }
  ]
  
}

```

Run as a normal python file from a terminal. It searches the current directory for config files by default.

The following flags can be used:
- `-v`, `-vv`, for more verbose debug info
- `-m` to disable *all* `"mods"` attributes in tasks
- `-f` list of config files to select from
- `-d` list of directories to shallow search for config files to select from
- `-r` list of directories to recursively search for config files to select from

```bash
# plain
$ py main.py

# maximum verbosity
$ py main.py -vv

# search recursively in "./demo" for config files, 
# and include "./test.json" and "./data/config.json" as config file options too
$ py main.py -r ./demo -f ./test.json ./data/config.json

# run with no "mods", and search the entire file system for config files
$ py main.py -m -r /
```
