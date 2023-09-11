"""
Created on Tue June 22, 2021
Updated: 2023-06-25
@author: Philip Combiths

Aggregate output from a phones query in Phon 3.0+. Specified for use with:
- Queries_v3_aggregate-accuracy.xml 
- Queries_v3_aggregate-accuracy.xml-by-participant 
Use the appropriate function for the type of query output.

Details: gGnerate an aggregate accuracy value for each unique phone/phone sequence. 
Useful for generating utput similar to Phon 2.2 accuracy queries from Phon 3.0 
phone queries.

Uses test_func.py to batch run this process on multiple files in a folder and
its subdirectories. User will be prompted for source directory.

Use cases:
## Convert a single file:
phone_accuracy(csv_to_pd()[0])
# OR
phone_accuracy_by_participant(csv_to_pd()[0])

## Convert directory + subdirectories (original)
result = test_func(phone_accuracy, csv_to_pd(overwrite_original=False))

## Convert directory + subdirectories (by-participant query)
result = test_func(phone_accuracy_by_participant, csv_to_pd(overwrite_original=False))

## WARNING: deletes original files
result = test_func(phone_accuracy, csv_to_pd(delete_original=True))
## OR
result = test_func(phone_accuracy_participant, csv_to_pd(delete_original=True))

"""
import os
import sys
from contextlib import contextmanager

import numpy as np
import pandas as pd

# import dtale
from test_func import test_func


@contextmanager
def change_dir(newdir):
    prevdir = os.getcwd()
    try:
        yield os.chdir(os.path.expanduser(newdir))
    finally:
        os.chdir(prevdir)


# Specify folder containing Phon output
def folder_input(subdirectories=True, separate_file_path=True, path=False):
    """
    Get file list from csv files in subdirectories.
    Should work with by-participant query.

    Parameters
    ----------
    subdirectories : BOOL, optional
        Searches subdirectories if True. The default is True.
    separate_file_path : BOOL, optional
        Returns tuple (FILEPATH, FILENAME) if True. The default is True.
    path : STR (BOOL), optional
        Provide directory path for input folder, else leave as False to be
        prompted for path. The default is False.

    Returns
    -------
    filepathList : LIST
        List of filepaths, either STRs or TUPLEs, depending on parameter set.

    """
    if not path:
        directory = input("Enter directory containing Phon output files (csv): ")
    elif path:
        directory = os.path.normpath(path)
    with change_dir(os.path.normpath(directory)):
        files_in_subdirectories = []
        if subdirectories:
            for dirName, subdirList, fileList in os.walk(os.getcwd()):
                for f in fileList:
                    files_in_subdirectories.append((dirName, f))
        else:
            for f in os.listdir(os.getcwd()):
                files_in_subdirectories.append((os.getcwd(), f))
    if separate_file_path:
        filepathList = files_in_subdirectories
    else:
        filepathList = [
            os.path.join(f_tuple[0], f_tuple[1]) for f_tuple in files_in_subdirectories
        ]
    return filepathList


# Open appropriate CSV files from folder and import as pandas df
# By default gets folder of input folder_input()
def csv_to_pd(fileList=folder_input(), delete_original=False, overwrite_original=False):
    """
    Generate DataFrames from csv files in a directory.

    Parameters
    ----------
    fileList : LIST, optional
        List of csv filepaths. The default is generated with folder_input().
    delete_original : BOOL, optional
        Set to True to delete original source files and leave only converted files.
    overwrite_original : BOOL, optional
        Set to True to overwrite existing converted files, if present.

    Returns
    -------
    df : DATAFRAME

    """
    if delete_original:
        print("*************************WARNING*************************")
        print("Original files will be PERMANENTLY DELETED.")
        permission = input("Type OK to proceed. Anything else to cancel:")
        if permission == "OK":
            pass
        else:
            sys.exit()
    df_list = []
    overwrite_accepted = False
    for f in fileList:
        # f[0] = path to file directory
        # f[1] = filename
        # Skip existing converted files
        if f[1].endswith("_Accuracy.csv"):
            # Exit with warning if overwrite_original==False
            if not overwrite_original:
                print("**********************************************************")
                print(
                    "WARNING: converted files already present. Set csv_to_pd(overwrite_existing=True) to overwrite"
                )
                sys.exit()
            elif overwrite_original:
                if overwrite_accepted:
                    pass
                else:
                    overwrite_warning = input(
                        "WARNING: existing converted files are present. These WILL be erased. Type overwrite to proceed. Anything else to exit: "
                    )
                    if overwrite_warning != "overwrite":
                        print("Exiting script. Existing converted files present.")
                        sys.exit()
                    elif overwrite_warning == "overwrite":
                        overwrite_accepted = True
                        print("Existing files overwritten.")
        # For every remaining csv file:
        elif f[1].endswith(".csv"):
            # Change to directory of file:
            with change_dir(f[0]):
                # Read csv to dataframe df
                df = pd.read_csv(f[1], encoding="utf-8")
                # Add file directory path as a column so it stays with df for later use
                df["file_dir"] = f[0]
                df["session"] = f[1].split(".")[0]  # Added for by-participant queries.
                # Add df to df_list
                df_list.append(df)
                # WARNING: deletes original file
                if delete_original:
                    os.remove(f[1])
    return df_list


# Preview dataframe
# def df_preview(df):
#     """

#     Open a pandas DataFrame in browser window. Requires dtale.

#     Parameters
#     ----------
#     df : DATAFRAME

#     """
#     d = dtale.show(df)
#     d.open_browser()
#     return


# Combine rows with same IPA Target. Original aggregate_accuracy version.
def phone_accuracy(df):
    """
    Generates a new DataFrame with aggregated accuracy values
    for Queries_v3_aggregate-accuracy.xml.

    Parameters
    ----------
    df : DATAFRAME
        DataFrame from which to generate phone accuracy.

    Returns
    -------
    accuracy_df : DATAFRAME
        DataFrame with aggregated accuracy values.

    """
    session_name = df.columns[2]
    df.rename(columns={session_name: "Total"}, inplace=True)
    accurate_mask = df["IPA Target"] == df["IPA Actual"]
    inaccurate_mask = df["IPA Target"] != df["IPA Actual"]

    accuracy_df = df.groupby(df["IPA Target"]).sum()
    accurate_df = df[accurate_mask].rename(columns={"Total": "Accurate"})
    inaccurate_df = df[inaccurate_mask].rename(columns={"Total": "Inaccurate"})
    accurate_df = accurate_df.groupby(accurate_df["IPA Target"]).sum()
    inaccurate_df = inaccurate_df.groupby(inaccurate_df["IPA Target"]).sum()

    accuracy_df = pd.concat([accurate_df, inaccurate_df, accuracy_df], axis=1)
    accuracy_df = accuracy_df.replace(np.nan, 0)
    accuracy_df["Accuracy"] = accuracy_df["Accurate"] / accuracy_df["Total"]
    accuracy_df["session"] = session_name
    dir_path = df["file_dir"].iloc[0]
    accuracy_df.to_csv(
        os.path.join(dir_path, session_name + "_Accuracy.csv"),
        columns=["Total", "Accurate", "Inaccurate", "session"],
        encoding="utf-8",
        index=True,
    )

    # accuracy_df.to_csv()
    return accuracy_df


# Combine rows with same IPA Target. Revised version for query by particpant
# with 'Alignment' column
def phone_accuracy_by_participant(df):
    """
    Generate a new DataFrame with aggregated accuracy values
    for Queries_v3_aggregate-accuracy.xml.

    Parameters
    ----------
    df : DATAFRAME
        DataFrame from which to generate phone accuracy.

    Returns
    -------
    accuracy_df : DATAFRAME
        DataFrame with aggregated accuracy values by participant.

    """
    session_name = df["session"].iloc[0]  # Extract session name. Replaces line below
    # session_name = df.columns[2]
    df.rename(columns={"Unnamed: 3": "Total"}, inplace=True)  # Replaces line below
    # df.rename(columns={session_name: "Total"}, inplace=True)
    accurate_mask = df["IPA Target"] == df["IPA Actual"]
    inaccurate_mask = df["IPA Target"] != df["IPA Actual"]

    accuracy_df = df.groupby(df["IPA Target"]).sum()
    accurate_df = df[accurate_mask].rename(columns={"Total": "Accurate"})
    inaccurate_df = df[inaccurate_mask].rename(columns={"Total": "Inaccurate"})
    accurate_df = accurate_df.groupby(accurate_df["IPA Target"]).sum()
    inaccurate_df = inaccurate_df.groupby(inaccurate_df["IPA Target"]).sum()

    accuracy_df = pd.concat([accurate_df, inaccurate_df, accuracy_df], axis=1)
    accuracy_df = accuracy_df.replace(np.nan, 0)
    accuracy_df["Accuracy"] = accuracy_df["Accurate"] / accuracy_df["Total"]
    accuracy_df["session"] = session_name

    dir_path = df["file_dir"].iloc[0]
    accuracy_df.to_csv(
        os.path.join(dir_path, session_name + "_Accuracy.csv"),
        columns=["Total", "Accurate", "Inaccurate", "session"],
        encoding="utf-8",
        index=True,
    )
    return accuracy_df


### Script Executions
## Convert a single file:
# phone_accuracy(csv_to_pd()[0])
# OR
# phone_accuracy_by_participant(csv_to_pd()[0])

## Convert directory + subdirectories (original)
result = test_func(phone_accuracy, csv_to_pd(overwrite_original=False))

## Convert directory + subdirectories (by-participant query)
# result = test_func(phone_accuracy_by_participant, csv_to_pd(overwrite_original=False))

## WARNING: deletes original files
# result = test_func(phone_accuracy, csv_to_pd(delete_original=True))
## OR
# result = test_func(phone_accuracy_participant, csv_to_pd(delete_original=True))
