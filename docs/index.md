# SpikeForest topics

## Codepod

The SpikeForest development environment can be opened in a docker container using [codepod](https://github.com/magland/codepod). Inspired by [gitpod](https://www.gitpod.io/), codepod allows users and co-developers to obtain identical development environments simply by cloning the repository and then running:

```
cd spikeforest2
./codepod_run.sh
```

Here are the prerequisites:

1. docker
2. codepod -- a python3 package (`pip install --upgrade codepod`)
3. a good internet connection -- the first time you run it, it will download the docker image which is several hundred MiB.


After running the above command, you should find yourself in a terminal within the container. At this point you can open vscode via:

```
code .
```

VSCode is a powerful yet lightweight IDE. It is written in typescript and supports a large collection of community-contributed plugins for syntax highlighting (many languages), code completion, debugging, previews. It has a nice file browser and terminal emulators. You can make quite a lot of headway within vscode. For example, you can even run jupyter notebooks (both client and server) from within the IDE.

Here are some important points to understand about using SpikeForest via codepod:

* The working directory (where you cloned SpikeForest) lives on the host machine but is also mounted in the container at `/home/project`. This means you can edit the sources files from either inside the codepod container (vscode) or outside the container, using your preferred editors on the host. Since the .git directory lives at the root of the project directory, you can also perform push/pull/commit operations either inside or outside the container and they will both take effect.
* The `/tmp` directory is by default also shared between the container and the host. In particular, the kbucket cache files (in `/tmp/sha1-cache`) are shared between the two and therefore persist between codepod sessions. If you set the KBUCKET_CACHE_DIR environment variable to something outside the /tmp directory, `codepod_run.sh` will handle that nicely as well.
* For convenience the `~/.gitconfig` (and other files with your user git preferences) will be mounted into the container as well. This enables git operations to work inside the container without needing to reconfigure every time you open a new codepod session. (See the `-g` option for `codepod`.)
* The `/tmp/.X11-unix` file is mounted and the display is forwarded so that GUI windows opened in the container appear like native windows on your host system.
* The user inside the codepod container matches the non-root user on the host. This is helpful because it is not always easy to accomplish using docker on Linux.
* You can also use and/or develop SpikeForest without docker and codepod. But, depending on which features you would like to use, you will need to set up the environment on your machine. In the simplest case, you can use python3 (>=3.6) and install the required packages via `./setup_python.sh`. To run the spike sorters in their containers you will also need to install [singularity](https://singularity-hub.org/). To see the complete list of packages included in the docker image, see the following two docker files: [magland/codepod](https://github.com/magland/codepod/tree/master/docker) and [magland/codepod_spikeforest2](https://github.com/flatironinstitute/spikeforest2/tree/master/devel/docker/codepod_spikeforest2). Also see .codepod.yml within the spikeforest repository.

## Unit tests

Unit tests are present in `unittests/` directories at various locations in the SpikeForest project. Some of these are fast (lightweight) tests. These can be run via the following command in the root project directory.

```
pytest
```

Pytest will recursively search the directories and find the appropriate tests to run, and then report which tests passed or failed. The configuration for this utilities is in `pytest.ini`. You will notice that tests marked as "slow" will not run by default. To perform more thorough tests that run an entire analysis pipeline, you can run:

```
pytest -m slow -s
```

The `-m slow` option runs all tests that are marked as `slow` and the `-s` flag causes the console output for the individual tests to be shown. Various spike sorters are tested for some toy examples and the processing takes place in singularity containers, which are automatically downloaded the first time they are needed.

We are following a continuous integration development strategy where new features can be often merged into the master branch with the guarantee that the unit tests will continue to pass. Therefore if a breaking change is introduced, it means that the unit tests need to be expanded to cover that case.

## SpikeForest raw data

The raw data for SpikeForest is hosted on a kbucket share (called `sf_raw`). It is simply a directory tree of recordings in the MountainSort format (`raw.mda`, `params.json`, `geom.csv`). The data are organized into studies and study sets. These are registered into the system by the scripts contained in `spikeforest2/working/prepare_recordings`. Once in the system, they may be browsed using GUIs and included in processing batches.

## Cairio, KBucket, and the cairio python client

KBucket is a distributed content-addressable storage database that enables referring to and retrieving files based on `sha1://` or `kbucket://` urls. Cairio is a key/value storage system that complements kbucket. 

## Hosting kbucket shares and hubs

## KBUCKET_CACHE_DIR

## Mountainlab python processors (MLProcessors)

Here is an example of the processor that wraps the MountainSort4 spike sorting algorithm (see spikeforest2/spikesorters/mountainsort4):

```
import mlprocessors as mlpr
import os

class MountainSort4(mlpr.Processor):
    NAME = 'MountainSort4'
    VERSION = '4.2.0'
    ENVIRONMENT_VARIABLES = [
        'NUM_WORKERS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'OMP_NUM_THREADS']
    CONTAINER = 'sha1://009406add7a55687cec176be912bc7685c2a4b1d/02-12-2019/mountainsort4.simg'
    CONTAINER_SHARE_ID = '69432e9201d0'  # place to look for container

    recording_dir = mlpr.Input('Directory of recording', directory=True)
    firings_out = mlpr.Output('Output firings file')

    detect_sign = mlpr.IntegerParameter(
        'Use -1, 0, or 1, depending on the sign of the spikes in the recording')
    adjacency_radius = mlpr.FloatParameter(
        'Use -1 to include all channels in every neighborhood')
    freq_min = mlpr.FloatParameter(
        optional=True, default=300, description='Use 0 for no bandpass filtering')
    freq_max = mlpr.FloatParameter(
        optional=True, default=6000, description='Use 0 for no bandpass filtering')
    whiten = mlpr.BoolParameter(optional=True, default=True,
                                description='Whether to do channel whitening as part of preprocessing')
    clip_size = mlpr.IntegerParameter(
        optional=True, default=50, description='')
    detect_threshold = mlpr.FloatParameter(
        optional=True, default=3, description='')
    detect_interval = mlpr.IntegerParameter(
        optional=True, default=10, description='Minimum number of timepoints between events detected on the same channel')
    noise_overlap_threshold = mlpr.FloatParameter(
        optional=True, default=0.15, description='Use None for no automated curation')

    def run(self):
        import spikeextractors as se
        import spiketoolkit as st
        import ml_ms4alg

        print('MountainSort4......')
        recording = se.MdaRecordingExtractor(self.recording_dir)
        num_workers = os.environ.get('NUM_WORKERS', None)
        if num_workers:
            num_workers = int(num_workers)

        # Bandpass filter
        if self.freq_min or self.freq_max:
            recording = st.preprocessing.bandpass_filter(
                recording=recording, freq_min=self.freq_min, freq_max=self.freq_max)

        # Whiten
        if self.whiten:
            recording = st.preprocessing.whiten(recording=recording)

        # Sort
        sorting = ml_ms4alg.mountainsort4(
            recording=recording,
            detect_sign=self.detect_sign,
            adjacency_radius=self.adjacency_radius,
            clip_size=self.clip_size,
            detect_threshold=self.detect_threshold,
            detect_interval=self.detect_interval,
            num_workers=num_workers
        )

        se.MdaSortingExtractor.writeSorting(
            sorting=sorting, save_path=self.firings_out)

```

Once a piece of python code is wrapped in a MLProcessor class, it can be executed in various ways:

* Directly on the local machine (without a container) via

```
MountainSort4.execute(recording_dir='/some/path', firings_out='/output/path/firings_out.mda', detect_sign=-1, ...)
```

* Inside a singularity container via the `_container` parameter, e.g., `_container='default'` or `_container='sha1://009406add7a55687cec176be912bc7685c2a4b1d/02-12-2019/mountainsort4.simg'`

* Creating a batch job for execution as part of a batch, either locally or on the remote server, by using `.createJob()` in place of `.execute()`. See below for more details.

The `.execute()` method ultimately calls the `.run()` function of the processor, but it handles a lot of other details including:

* Automatically resolves kbucket paths of the inputs.
* Stores runtime information such as console output, run times, CPU usage, etc.
* Caches results of processing based on the signature of the execution determined from the processor name, version, parameters, and the SHA-1 of the input files. Subsequent calls to the same processor job, even from a different computer, will not need to execute.
* Automatically handles details of running the processor within a singularity container.
* Optionally returns output file paths or urls without needing to specify the specific location of the outputs.
* Facilitates running processing jobs on remote compute resources.

## Spike Sorters

Each spike sorting algorithm registered in SpikeForest is completely specified in a subdirectory of spikeforest2/spikesorters. This includes the python wrapper code for calling the algorithm (as a MLProcessor) as well as the Dockerfile used to create the appropriate singularity container to provide the OS environment needed to run the processing. For example, the Spyking Circus docker file installs a particular version of spyking circus.

There are two spike sorters that use MATLAB and have not yet been wrapped in a singularity container. However, we have done proof-of-principle tests that this can be accomplished using the MATLAB compiler and including the appropriate MATLAB runtime inside the singularity container. Alternatively, for development purposes, it may be possible to mount the MATLAB license files inside the container. For now we are just running these codes outside containers and using environment variables to point to the MATLAB source codes for these algorithms.

## Local vs remote processing

Processing scripts are written in python and can be run locally with no need to connect to the internet except for one-time automatic downloads of raw data and singularity containers. Scripts may also be configured to send processing jobs to remote compute resources.

## Compute resources

Any computer or compute cluster may be used as a compute resource. To utilize a compute resource (call it the "server"), you just need to run a script on the server and then send jobs to it from a processing script running on any computer. Here is an example compute resource script running on the server (it is found in spikeforest2/working/compute_resources/ccmlin008-default):

```
#!/bin/bash
set -e

export NUM_WORKERS=2
export MKL_NUM_THREADS=$NUM_WORKERS
export NUMEXPR_NUM_THREADS=$NUM_WORKERS
export OMP_NUM_THREADS=$NUM_WORKERS

export DISPLAY=""

# Use the following to connect to spikeforest2
export CAIRIO_CONFIG=spikeforest.spikeforest2-readwrite
export CAIRIO_CONFIG_PASSWORD=$SPIKEFOREST_PASSWORD

# find containers (look in spikeforest2)
export CAIRIO_ALTERNATE_SHARE_IDS=69432e9201d0

../../../bin/batcho_listen ccmlin008-default --allow_uncontainerized --parallel=10
```

The SPIKEFOREST_PASSWORD environment variable needs to be set so that the system will connect into the spikeforest2 kbucket share with read/write access. The compute resource will be listening as name on this kbucket share "ccmlin008-default", and is configured to run 10 jobs in parallel (`--parallel=10`). The `--allow_uncontainerized` flag permits the resource to process jobs that do not run inside a singularity container.

The CAIRIO_ALTERNATE_SHARE_IDS environment variable is used provide the location to search for singularity containers, for automatic download if needed. Note: in the future this will not be needed, because the MLProcessor classes will provide this information.

## Processing batches

Processing batches are simply collections of jobs that may be run in parallel. Jobs are created by wrapping python code in MLProcessor classes and then by calling the `.createJob()` function. Jobs may be assembled into batches and then either executed locally, or on remote compute resources. Results of processing jobs are stored via kbucket, either locally or on a remote kbucket share.

## SpikeForest analysis scripts

The top-level analysis scripts are found in the `spikeforest2/working/main_analysis` directory. These use python functions defined in the `spikeforest2/spikeforest_analysis` module.

## VDOMR - GUI components

[Show examples]

