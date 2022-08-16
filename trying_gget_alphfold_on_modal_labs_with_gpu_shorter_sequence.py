#!/usr/bin/env python
# trying_gget_alphfold_on_modal_labs_with_gpu_shorter_sequence.py
# based on modal_labs_blender_gpu_script.py from https://modal.com/api/raw-examples/blender_video.py and https://modal.com/api/raw-examples/fetch_stock_prices.py 
# for passing data back
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
# Plus need git and for gpu to be accessible suggested to install cuda,
# see https://gist.github.com/aksh-at/6dc792c9e8002399ea4f386e60bdb025
stub = modal.Stub(image=modal.Conda().conda_install(["git", "openmm=7.5.1", 
    "cudatoolkit=11.2", "cudnn=8.1.0"]).pip_install(["gget", "tensorflow"]))


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
    import tensorflow as tf
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
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
    # Need back the results in the directory *_gget_alphafold_prediction from 
    # remote (the asterisk is a time date stamp like 
    # '2022_08_12-1901_gget_alphafold_prediction').
    # Process will be based on https://modal.com/api/raw-examples/fetch_stock_prices.py
    # where bytes based back.
    # Will pass zipped files back by combining that with 
    # https://stackoverflow.com/a/53880817/8508004
    import os
    from io import BytesIO
    import zipfile
    import glob
    in_memory_zip_buf = BytesIO()
    results_directory_suffix = '_gget_alphafold_prediction' # based on 
    # https://twitter.com/NeuroLuebbert/status/1557090698003767296
    results_directory = glob.glob(f'*{results_directory_suffix}')[0] 
    results_datetime_stamp = results_directory.split(
        "results_directory_suffix")[0]
    with zipfile.ZipFile(in_memory_zip_buf, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("./"+results_directory, topdown=True):
            # Skipping hidden files based on 
            # https://stackoverflow.com/a/13454267/8508004
            files = [f for f in files if not f[0] == '.']
            dirs[:] = [d for d in dirs if not d[0] == '.']
            for file in files:
                print(f"File in results on remote: {os.path.join(root, file)}")
                zipf.write(os.path.join(root, file))
            for name in dirs:
                print(
                    f"Directory in results on "
                    "remote: {os.path.join(root, name)}"
                    )
    # After all files placed in there, reset the pointer back to beginning of 
    # the buffer (comment adapted from 
    # https://stackoverflow.com/a/54202259/8508004).
    in_memory_zip_buf.seek(0)
    return results_datetime_stamp, in_memory_zip_buf.getvalue()



# ## Entrypoint
OUTPUT_DIR = "/tmp/gget_alphafold_results"
results_directory_suffix = '_gget_alphafold_prediction'
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with stub.run():
        datetime_stamp, results_zipped_bytes = run_alphafold()
        filename = os.path.join(
            OUTPUT_DIR,  f"zipped_"
            f"{datetime_stamp}{results_directory_suffix}.zip")
        print(f"Saving gget_alphafold results to {filename}")
        with open(filename, "wb") as f:
            f.write(results_zipped_bytes)