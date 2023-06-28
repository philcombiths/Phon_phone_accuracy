"""
Created on Tue June 22, 2021

@author: Philip

Aggregates output from a phones query in Phon 3.0+ to generate an aggregate 
accuracy value for each unique phone/phone sequence. Useful for generating 
output similar to Phon 2.2 accuracy queries.

Uses test_func.py to batch run this process on multiple files in a folder and
its subdirectories

Use case:
# Given a single file to convert. User will be asked to paste directory path 
# containing file. 
# Revised file will be created in same directory.

phone_accuracy(csv_to_pd()[0])

# Given a folder with subfolders of files to convert

result = test_func(phone_accuracy, csv_to_pd())

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
        filepathList = [os.path.join(f_tuple[0], f_tuple[1]) for f_tuple in files_in_subdirectories]
    return filepathList
            
# Open appropriate CSV files from folder and import as pandas df
# By default gets folder of input folder_input()
def csv_to_pd(fileList=folder_input(), delete_original=False):
    """
    Generates DataFrames from csv files in a directory.

    Parameters
    ----------
    fileList : LIST, optional
        List of csv filepaths. The default is generated with folder_input().

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
    for f in fileList:
        # f[0] = path to file directory
        # f[1] = filename
        if f[1].endswith('.csv'):
            with change_dir(f[0]):
                df = pd.read_csv(f[1], encoding='utf-8')
                # Add file directory path as a column so it stays with
                # dataframe for later use
                df['file_dir'] = f[0]
                df_list.append(df)
                # WARNING: deletes original file
                if delete_original:
                    os.remove(f[1])

        
    
    return df_list

# Preview dataframe
# def df_preview(df):
#     """
    
#     Opens a pandas DataFrame in browser window.
    
#     Parameters
#     ----------
#     df : DATAFRAME

#     """
#     d = dtale.show(df)
#     d.open_browser()
#     return
  
# Combine rows with same IPA Target
def phone_accuracy(df):
    """
    Generates a new DataFrame with aggregated accuracy values.

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
    df.rename(columns={session_name:'Total'}, inplace=True)
    accurate_mask = df['IPA Target'] == df['IPA Actual']
    inaccurate_mask = df['IPA Target'] != df['IPA Actual']
    
    accuracy_df = df.groupby(df['IPA Target']).sum()
    accurate_df = df[accurate_mask].rename(columns={'Total':'Accurate'})
    inaccurate_df = df[inaccurate_mask].rename(columns={'Total':'Inaccurate'})
    accurate_df = accurate_df.groupby(accurate_df['IPA Target']).sum()
    inaccurate_df = inaccurate_df.groupby(inaccurate_df['IPA Target']).sum()
    
    accuracy_df = pd.concat([accurate_df, inaccurate_df, accuracy_df], axis=1)
    accuracy_df = accuracy_df.replace(np.nan, 0)
    accuracy_df['Accuracy'] = accuracy_df['Accurate']/accuracy_df['Total']
    accuracy_df['session'] = session_name
    
    dir_path = df['file_dir'].iloc[0]
    accuracy_df.to_csv(os.path.join(dir_path, session_name+'_Accuracy.csv'), 
                       columns=['Total', 'Accurate', 'Inaccurate', 'session'],
                       encoding='utf-8', index=True)
    
    # accuracy_df.to_csv()
    return accuracy_df

## Convert single file
# phone_accuracy(csv_to_pd()[0])

## Convert directory + subdirectories
result = test_func(phone_accuracy, csv_to_pd())

## WARNING: deletes original files
# result = test_func(phone_accuracy, csv_to_pd(delete_original=True))


