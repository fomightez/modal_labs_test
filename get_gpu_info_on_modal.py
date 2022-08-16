#!/usr/bin/env python
# get_gpu_info_on_modal.py
# Can tensorflow see GPU?
# based on modal_labs_blender_gpu_script.py from https://modal.com/api/raw-examples/blender_video.py and https://gist.github.com/aksh-at/6dc792c9e8002399ea4f386e60bdb025
# plus help from meeting Erik at Modal where he provided me with 
# https://gist.github.com/aksh-at/6dc792c9e8002399ea4f386e60bdb025
__author__ = "Wayne Decatur" #fomightez on GitHub
__license__ = "MIT"
__version__ = "0.1.0"

# ## Basic setup

import os

import modal
import modal.image

# ## Defining the image
#
# gget requires a very custom image in order to run properly.
# In order to save you some time, we have precompiled the Python packages
# and stored them in a Dockerhub image.

#Need  equivalent of `conda install -c conda-forge openmm=7.5.1`
stub = modal.Stub(image=modal.Conda().conda_install(["git", "openmm=7.5.1", 
    "cudatoolkit=11.2", "cudnn=8.1.0"]).pip_install(["gget", "tensorflow"]))


# ## Setting things up in the containers
#
# We need various global configuration that we want to happen inside the containers (but not locally), such as
# enabling the GPU device.
# To do this, we use the `stub.is_inside()` conditional, which will evaluate to `False` when the script runs
# locally, but to `True` when imported in the cloud.
# Finding tensorflow import needs to be here to trigger gpu activation 
# behind-the-scenes (although it seems once it happens once in a recent run, I 
# can move this to the `@stub.function()` and it coninues to work to allow gpu
# to work if all fresh???) and and probaby the reason why in example provided 
# me, https://gist.github.com/aksh-at/6dc792c9e8002399ea4f386e60bdb025 , is
# in this portion.

if stub.is_inside():
    import tensorflow as tf
    print(tf.config.list_physical_devices('GPU'))
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    import gget
    gget.setup("alphafold")



# ## Use a GPU from a Modal function
#
# Now, let's define the function that renders each frame in parallel.
# Note the `gpu=True` argument which tells Modal to use GPU workers.


@stub.function(gpu=True)
def detect_gpu_test():
    import tensorflow as tf
    print(tf.config.list_physical_devices('GPU'))
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))



# ## Entrypoint
OUTPUT_DIR = "/tmp/gget_alphafold_results"
results_directory_suffix = '_gget_alphafold_prediction'
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with stub.run():
        detect_gpu_test()