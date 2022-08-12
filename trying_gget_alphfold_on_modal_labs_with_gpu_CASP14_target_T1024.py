#!/usr/bin/env python
# trying_gget_alphfold_on_modal_labs_with_gpu_CASP14_target_T1024.py
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
    "conda install -c conda-forge openmm=7.5.1 --yes",
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
    p_seq = "MAAHKGAEHHHKAAEHHEQAAKHHHAAAEHHEKGEHEQAAHHADTAYAHHKHAEEHAAQAAKHDAEHHAPKPH" # That
    # protein sequence is noted in 'gget_alphafold.ipynb' as ' CASP14 target T1024' and links to https://predictioncenter.org/casp14/target.cgi?id=8&view=all . 'gget_alphafold.ipynb' can be
    # found at https://twitter.com/NeuroLuebbert/status/1556168684799832064
    gget.alphafold(p_seq)


# ## Entrypoint
if __name__ == "__main__":
    with stub.run():
        run_alphafold()