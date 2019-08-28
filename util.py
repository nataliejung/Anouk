import os
import pandas as pd
import xlsxwriter




#Delete any exisitng file
def clean_file(file_name):
  if os.path.exists(file_name):
    print("removed the exisiting excel file")
    os.remove(file_name)
  else:
    print("The file does not exist")
    

# Convert pdf to excel name
def file_decoder(song):           
    song = song.upper()
    song = (" ".join(song.replace("PDF", "xlsx").split()))
    return song


# Set Excel file witdth
def file_width(dataframe, writer, sheet_name):
    print("sheet name: "+ sheet_name)
    workbook = writer.book  # Access the workbook
    worksheet = writer.sheets[sheet_name]  # Access the Worksheet   
    for i, width in enumerate(get_col_widths(dataframe)):
       worksheet.set_column(i, i, width)
     
    

def get_col_widths(dataframe):
    # First we find the maximum length of the index column   
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]


