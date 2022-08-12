#!/usr/bin/env python
# trying_gget_alphfold_on_modal_labs_with_gpu.py
# based on modal_labs_blender_gpu_script.py from https://modal.com/api/raw-examples/blender_video.py
__author__ = "Wayne Decatur" #fomightez on GitHub
__license__ = "MIT"
__version__ = "0.1.0"

# ## Basic setup

import os
import tempfile

import modal
import modal.image

# ## Defining the image
#
# gget requires a very custom image in order to run properly.
# In order to save you some time, we have precompiled the Python packages
# and stored them in a Dockerhub image.

#Need  equivalent of `conda install -c conda-forge openmm=7.5.1`
the_commands = [
    "conda install -c conda-forge openmm=7.5.1",
    "pip install gget",
]
stub = modal.Stub(image=modal.Conda().conda_install(["git"]).run_commands(the_commands))


# ## Setting things up in the containers
#
# We need various global configuration that we want to happen inside the containers (but not locally), such as
# enabling the GPU device.
# To do this, we use the `stub.is_inside()` conditional, which will evaluate to `False` when the script runs
# locally, but to `True` when imported in the cloud.

if stub.is_inside():
    import gget
    gget.setup("alphafold")



# ## Use a GPU from a Modal function
#
# Now, let's define the function that renders each frame in parallel.
# Note the `gpu=True` argument which tells Modal to use GPU workers.


@stub.function(gpu=True)
def run_alphafold():
    return gget.alphafold("MAAHKGAEHHHKAAEHHEQAAKHHHAAAEHHEKGEHEQAAHHADTAYAHHKHAEEHAAQAAKHDAEHHAPKPH")


# ## Entrypoint
if __name__ == "__main__":
    with stub.run():
        run_alphafold()