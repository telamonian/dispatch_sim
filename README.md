# Order-dispatch simulation
## a Ghost Kitchens coding interview by Max Klein ([@telamonian](https://github.com/telamonian) on github)

### License

- MIT

### Requirements

- python 3.7 or above recommended (tested with 3.7, 3.8, and 3.9)
- mac or linux recommended (tested on mac, windows users may run into issues)
- python dependencies:
    - `numpy`
    - `pytest` (for running the unittests)

### Install

- First, ensure that the python dependencies are installed and are of a recent version:

    ```bash
    pip install -U numpy pytest
    ```

- Next, untar the submitted tarball (`ghost_kitchens_code_interview_max_klein.tar.gz`) and go into the resulting dir:

    ```bash
    tar xzvf ghost_kitchens_code_interview_max_klein.tar.gz
    cd ghost_kitchens_code_interview_max_klein
    ```

### Running the simulation script

- Once you have navigated to the project root `ghost_kitchens_code_interview_max_klein` dir (as described in `Install` above), you can execute the main `dispatch_simulation.py` script directly:

    ```bash
    # run the order-dispatch simulation in real-time using the matched courier dispatch algorithm
    ./dispatch_simulation.py

    # run the order-dispatch simulation in real-time using the FIFO courier dispatch algorithm
    ./dispatch_simulation.py --fifo

    # run a quick test version of the order-dispatch simulation that skips over all wait times in-between events
    ./dispatch_simulation.py --test

    # other cmd-line flags are available for the purpose of facilitating testing; see built-in `--help` for full details
    ./dispatch_simulation.py --help
    ```

### Running the unittests

- Navigate to the project root `ghost_kitchens_code_interview_max_klein` dir and then just execute the `pytest` command:

    ```bash
    pytest
    ```

    and the unittests should all run automatically from there.

### Troubleshooting

- If the `python` cmd in your shell is still linked to an instance of python 2, instead of invoking the `dispatch_simulation.py` directly you'll have to run it via the `python3` cmd:

    ```bash
    # this assumes that the python3 cmd exists on your system
    python3 dispatch_simulation.py

    # OR, alternatively, you can use a minor version specific python cmd if you have one available, eg
    python3.9 dispatch_simulation.py
    ```

### Design notes
- the code in the main `dispatch_simulation.py` is split into two parts:
    - a collection of module level functions that handle the heavy mathematical/computational lifting. These
    functions all either return an ndarray as a result, take an ndarray as input parameter, or both. The most
    important of these functions are `getSimArr` and `getEventsFromSimArr`:
        - `getSimArr`: calculates all significant values required to fully describe a specification-compliant
        simulation. Leverages numpy in order to take advantage of a concise vectorization approach to performing
        the calculations over the entire set of input orders, instead of the more standard iterative approach.
        - `getEventsFromSimArr`: takes the output of `getSimArr` as input. Transcribes the simArr data into a
        complete linear list of every simulation event of interest.
    - a `RealTimeSim` class. Its constructor requires a simArr (ie the output of `getSimArr`) as input. Given
    that `sim` is an instance of `RealTimeSim`, calling `sim.run()` will "rehydrate" this simArr into a full
    real-time simulation, with event times synced with wall clock time (in terms of seconds since simulation start).
- the loosely coupled math code, and the loose coupling between the math code and the RealTimeSim instances,
helps to facilitate breaking the program as a whole up into testable units.
