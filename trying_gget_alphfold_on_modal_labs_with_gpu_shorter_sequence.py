#!/usr/bin/env python
# trying_gget_alphfold_on_modal_labs_with_gpu_shorter_sequence.py
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
    p_seq = "EMHGPEGLRVGFYESD" # I thought that 'CHRISAVERY 'should work here since 
    # https://twitter.com/qc_punk/status/1460785886421938183 reported a prediction
    # using Alphafold.
    # Just wanted a short sequence in hopes could test how to get back results 
    # without huge wait to test. However, had to lengthen as when I ran
    # `gget.alphafold(p_seq)` with `p_seq = "CHRISAVERY"` I got 
    # `ValueError: Input sequence is too short: 10 amino acids, while the 
    # minimum is 16` So switched to 16 amino acid peptide (696–777 of the human 
    # a2-macroglobulin) from 
    # https://pubmed.ncbi.nlm.nih.gov/11106172/ that I found by searching 
    # '16 amino acid peptide'

    gget.alphafold(p_seq)
    return os.listdir()


# ## Entrypoint
if __name__ == "__main__":
    with stub.run():
        run_alphafold()