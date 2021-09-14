# Order-dispatch simulation
## a Ghost Kitchens coding interview by Max Klein ([@telamonian](https://github.com/telamonian) on github)

### License

- MIT

### Requirements

- python 3.9 or above
- mac or linux recommended (tested on mac, windows users may run into issues)

### Install

- Unpack the project archive and then navigate to project root:

    ```bash
    tar xvzf dispatch_sim.tar.gz
    cd dispatch_sim
    ```

- Install the `dispatch_sim` pkg, including the test dependencies:

    ```bash
    # DO NOT USE `python setup.py install`
    pip install .[test]
    ```

### Running the simulation

- The `dispatch_sim` pkg will install the `run_dispatch_sim` entrypoint script to your shell's path:
    ```bash
    # run the order-dispatch simulation in real-time using the matched courier dispatch algorithm
    run_dispatch_sim

    # run the order-dispatch simulation in real-time using the FIFO courier dispatch algorithm
    run_dispatch_sim --fifo

    # run a quick test version of the order-dispatch simulation that skips over all wait times in-between events
    run_dispatch_sim --discrete --eta 9

    # other cmd-line flags are available for the purpose of facilitating testing; see built-in `--help` for full details
    run_dispatch_sim --help
    ```

### Usage

- For more information on usage and simulation details, see specification in `./Dispatch_Simulation_-_Homework.pdf` under the project root

### Running the unittests

- Navigate to the project root dir and run:

    ```bash
    python -m pytest
    ```

    The unittests (with coverage) should all run automatically from there.

### Run the static type checker

- The type correctness can be statically checked via mypy:

    ```bash
    python -m mypy -p dispatch_sim
    ```

    Almost every class, function, member, etc, in this pkg has been annotated with type hints using the latest typing syntax that became available as of Python 3.9.


### Troubleshooting

- If the `pip` cmd in your shell is associated with an instance of python <3.9, you can install using the pip supplied by a specific version of python:

    ```bash
    <path/to/python39> -m pip install .
    ```

### Dev

#### Design notes

- Commentary on code and program design decisions can be found in the associated docstrings in the source code

#### Export tarball of repo

```bash
git archive --output=./dispatch_sim.tar.gz --format=tar.gz --prefix=dispatch_sim/ HEAD
```
