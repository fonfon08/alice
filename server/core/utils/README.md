# Overview

Various logic, such as IOC collection, help messages (armory, lolbins, etc), queue helpers, and the AliceScript worker bridge. querys.py is the queue line helpers (create, read, delete) and agent history lines, validation.py waits for the AliceScript worker to approve or reject a ready queue line, and lolbins.json is the catalog of host binary paths, tags, and sometimes placeholders.

## Directories

- `/iocs`: IOC collection from terminal commands and file server transfers
- `/messages`: Help message texts (commands, armory tools, lolbins, etc)
- `/alicescripts`: Logic that starts the AliceScript worker and the calls it makes back into the server
