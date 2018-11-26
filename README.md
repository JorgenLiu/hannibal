# hannibal

A light-weighted, distributed crawler implemented based on asyncio, aiohttp and redis.

For commemorating genneral Hannibal Barca.

### Collecting

Two application design modes supported:

1. Single node contains both collecting and parsing functionality.
2. Distribute structure contains lots of collecting nodes and parsing nodes, interacts with reds-based queue and URL pool.

Two collecting modes supported:

1. Collecting for a list of task.
2. Increasing collection.

### Parsing

Only basic parsing schedule is implemented in parser module, you need to overide the Parser class and implemented the page parsing function by yourself.  Multiple parser modules are supported, beautiful soup, pyquery or regular expression are available.

### Queue and Pool

Both of the two brokers mentioned above are implemented in memory based mode and redis based mode. For memory based queue and pool, basic storage mechanism also implemented.