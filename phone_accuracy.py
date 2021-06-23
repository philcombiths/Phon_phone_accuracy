"""
Created on Tue June 22, 2021

@author: Philip

Aggregates output from a phones query in Phon to generate an aggregate 
accuracy value for each unique phone/phone sequence.

"""
import os
import pandas as pd
import numpy as np
from contextlib import contextmanager
import dtale
from test_func import test_func
        
@contextmanager
def change_dir(newdir):
    prevdir = os.getcwd()
    try:
        yield os.chdir(os.path.expanduser(newdir))
    finally:
        os.chdir(prevdir)

# Specify folder containing Phon output
def folder_input(subdirectories=True, separate_file_path=True):
    """

    Parameters
    ----------
    subdirectories : BOOL, optional
        Searches subdirectories if True. The default is True.
    separate_file_path : BOOL, optional
        Returns tuple (FILEPATH, FILENAME) if True. The default is True.

    Returns
    -------
    filepathList : LIST
        List of filepaths, either STRs or TUPLEs, depending on parameter set.

    """
    directory = input("Enter directory containing Phon output files (csv): ")
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
def csv_to_pd(fileList=folder_input()):
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
    df_list = []
    for f in fileList:
        if f[1].endswith('.csv'):
            with change_dir(f[0]):
                df = pd.read_csv(f[1], encoding='utf-8')
                df_list.append(df)
    return df_list

# Preview dataframe
def df_preview(df):
    """
    
    Opens a pandas DataFrame in browser window.
    
    Parameters
    ----------
    df : DATAFRAME

    """
    d = dtale.show(df)
    d.open_browser()
    return

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
    
    return accuracy_df
     
### Script to convert dataframes to csv


result = test_func(phone_accuracy, csv_to_pd())
