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
    # Need back the results in the directory *_gget_alphafold_prediction from 
    # remote (the asterisk is a time date stamp like 
    # '2022_08_12-1901_gget_alphafold_prediction').
    # Process will be based on https://modal.com/api/raw-examples/fetch_stock_prices.py
    # where bytes based back.
    # Will pass zipped files back by combining that with 
    # https://stackoverflow.com/a/53880817/8508004
    from io import BytesIO
    import zipfile
    import glob
    import os
    memory_file = BytesIO()
    results_directory = glob.glob('*_gget_alphafold_prediction')[0] # based on 
    # https://twitter.com/NeuroLuebbert/status/1557090698003767296
    results_datetime_stamp = results_directory.split("_gget_alphafold_prediction")[0]
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("./"+results_directory, topdown=True):
            # skipping hidden files based on https://stackoverflow.com/a/13454267/8508004
            files = [f for f in files if not f[0] == '.']
            dirs[:] = [d for d in dirs if not d[0] == '.']
            for file in files:
                print(f"file in results on remote: {os.path.join(root, file)}")
                zipf.write(os.path.join(root, file))
            for name in dirs:
                print(f"directory in results on remote: {os.path.join(root, name)}")
    memory_file.seek(0)
    return results_datetime_stamp, memory_file.getvalue()


# ## Entrypoint
OUTPUT_DIR = /tmp/gget_alphafold_results
if __name__ == "__main__":
    with stub.run():
        datetime_stamp, results_zipped_bytes = run_alphafold()
        filename = os.path.join(OUTPUT_DIR,  f"{datetime_stamp}_results.zip")
        print(f"Saving gget_alphafold results to {filename}")
        with open(filename, "wb") as f:
            f.write(results_zipped_bytes)