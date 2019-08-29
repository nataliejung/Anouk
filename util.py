import os
import openpyxl
import pandas as pd
import matplotlib.pyplot as plt
import PIL
import xlsxwriter




#Delete any exisitng files
def clean_file(file_name):
  if os.path.exists(file_name):
    print("removed the exisiting excel file")
    os.remove(file_name)
  else:
    print("The file does not exist")

  if os.path.exists("output.png"):
    os.remove("output.png")
  else:
    print("The output.png does not exist")
    

# Convert pdf to excel name
def file_decoder(song):           
    song = song.upper()
    song = (" ".join(song.replace("PDF", "xlsx").split()))
    return song


# Set Excel file witdth
def file_width(dataframe, writer, sheet_name):    
    workbook = writer.book  # Access the workbook
    worksheet = writer.sheets[sheet_name]  # Access the Worksheet    
    
    for i, width in enumerate(get_col_widths(dataframe)):
       worksheet.set_column(i, i, width)
     
    

def get_col_widths(dataframe):
    # First we find the maximum length of the index column   
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]


# Plot Changes in the Chart
def plotChanges(fdf, sheet_name, convertedFile):
    # Parameters for plotting
    plotKwargs = {
        "x": "Name",
        "figsize": (17, 12),
        "kind": "bar",
        "fontsize": 8,
    }

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax1 = ax.twinx()    
    def align_yaxis(ax1, v1, ax2, v2):        
        """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
        _, y1 = ax1.transData.transform((0, v1))
        _, y2 = ax2.transData.transform((0, v2))
        inv = ax2.transData.inverted()
        _, dy = inv.transform((0, 0)) - inv.transform((0, y1-y2))
        miny, maxy = ax2.get_ylim()
        ax2.set_ylim(miny+dy, maxy+dy)
        
    fdf.plot(y="% Change", ax=ax, **plotKwargs, position=0, color="red")
    fdf.plot(y="TL-Diff", ax=ax1, **plotKwargs, position=1, color="blue")         
    align_yaxis(ax, 0, ax1, 0)    
    plt.savefig('output.png')
    
    wb = openpyxl.load_workbook(convertedFile)
    ws = wb[sheet_name]
   
    img = openpyxl.drawing.image.Image('output.png')
    img.anchor = 'K1'
    ws.add_image(img)
    wb.save(convertedFile)

    #ws.save('KOC-HOLDING-2018-ANNUAL-REPORT.xlsx')
