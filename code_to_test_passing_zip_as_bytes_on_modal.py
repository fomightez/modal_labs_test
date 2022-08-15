#!/usr/bin/env python
# code_to_test_passing_zip_as_byteson_modal.py
__author__ = "Wayne Decatur"  # fomightez on GitHub
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

#Use Modal's pre-built Conda base image, see 
# https://modal.com/docs/guide/custom-container, so is like where will use this 
# approach to pass a directory of files back soon.
# Add the packages I ended up using to make creating a bunch of files quick.
stub = modal.Stub(image=modal.Conda().conda_install(["pandas","matplotlib"]))



# ## Make fake files and send the entire directory back as zipped bytes
@stub.function()
def make_files_and_make_zipped_bytes():
    results_directory = "results"

    # make files in the 'results' directory
    # Doesn't matter what they are, just need a few files with content to test
    # collecting the directory
    import os
    os.makedirs(results_directory, exist_ok=True)
    import pandas as pd
    import numpy as np
    # Create a DataFrame from a Python dictionary
    df = pd.DataFrame({ 'Id' : ["Charger","Ram","Pacer","Elantra","Camaro","Porsche 911"],
        'Speed':[30,35,31,20,25,80]
        })
    df.to_pickle(os.path.join(results_directory, "file_name1.pkl"))
    df.to_csv(os.path.join(results_directory, "file_name1.tsv"), sep='\t')
    ax = df.plot.hist(ec=(0.3,0.3,0.3,0.65),legend=False)
    ax.figure.savefig("test.png")
    # When making Dataframe from dictionary, you can change order of columns by providing columns list in order, such as 
    # `, columns = ['Speed', 'Id']` between the dictionary closing curly bracket and the DataFrame method closing parantheses
    df = pd.DataFrame({'A': 'foo bar one123 bar foo one324 foo 0'.split(),
                       'B': 'one546 one765 twosde three twowef two234 onedfr three'.split(),
                       'C': np.arange(8), 'D': np.arange(8) * 2})
    df.to_pickle(os.path.join(results_directory, "file_name2.pkl"))
    df.to_csv(os.path.join(results_directory, "file_name2.tsv"), sep='\t')
    ax = df.plot.hist(ec=(0.3,0.3,0.3,0.65),legend=False)
    ax.figure.savefig("test2.png")
    a_dictionary = {"April":"Grass", "May":"Flowers","June":"Corn"}
    df = pd.DataFrame(list(a_dictionary.items()), columns = ['column1', 'column2']) # BUT IS THIS LIMITED TO TWO COLUMNS SINCE USING KEY-VALUE PAIRS??
    df.to_pickle(os.path.join(results_directory, "file_name3.pkl"))
    df.to_csv(os.path.join(results_directory, "file_name3.tsv"), sep='\t')



    # collect files in the 'results' directory
    from io import BytesIO
    import zipfile
    import glob
    import os

    in_memory_zip_buf = BytesIO()
    # files_collecting_suffix = '_to_test.txt'
    
    with zipfile.ZipFile(in_memory_zip_buf, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("./" + results_directory, topdown=True):
            # Skipping hidden files based on
            # https://stackoverflow.com/a/13454267/8508004
            files = [f for f in files if not f[0] == "."]
            dirs[:] = [d for d in dirs if not d[0] == "."]
            for file in files:
                print(f"File in results on remote: {os.path.join(root, file)}")
                zipf.write(os.path.join(root, file))
            for name in dirs:
                print(
                    f"Directory in results "
                    "on remote: {os.path.join(root, name)}"
                )
    # After all files placed in there, reset the pointer back to beginning of
    # the buffer (comment adapted from
    # https://stackoverflow.com/a/54202259/8508004).
    in_memory_zip_buf.seek(0)
    return in_memory_zip_buf.getvalue()


# ## Entrypoint
OUTPUT_DIR = "/tmp/test_results"
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with stub.run():
        results_zipped_bytes = make_files_and_make_zipped_bytes()
        datetime_stamp = "now"
        filename = os.path.join(OUTPUT_DIR, f"{datetime_stamp}_results.zip")
        print(f"Saving results to {filename}")
        with open(filename, "wb") as f:
            f.write(results_zipped_bytes)