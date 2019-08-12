import pandas as pd 
import os 
import xlsxwriter 

def excel_columnname(len_):
    """ return excel column letter"""
    return  xlsxwriter.utility.xl_col_to_name(len_)

def df2chart(writer, sheetname="result", chartoption=None):
    """ create chart in the excel file
    """
    print(chartoption)
    workbook = writer.book
    worksheet = writer.sheets[sheetname]
    chart = workbook.add_chart({'type' : chartoption['type'], 'subtype' : "clustered"})
    datavalue = f"{sheetname}!{chartoption['values']}"
    print(datavalue)
    chart.add_series({'values' : f"={datavalue}"})
    worksheet.insert_chart(chartoption['location'], chart)
    

def df2excel(data, filename, sheetname="result", newfile=False, chartoption=None):
    if os.path.isfile(filename):
        old_data = pd.read_excel(filename,sheet_name=None)
    else:
        old_data = None
    
    if newfile:
        old_data = None
    writer = pd.ExcelWriter(filename, engine = 'xlsxwriter')
    if old_data:
        for ws_name, df_sheet in old_data.items():
            df_sheet.to_excel(writer,sheet_name=ws_name)
    
    data.to_excel(writer, sheet_name=sheetname)
    shape = data.shape
    print(shape)
    if chartoption:
        chartoption = {}
        # create default column chart 
        # the chart will be located at 2 rows below the last line
        # will use the data in the last row
        chartoption['type'] = "column"
        chartoption['values'] = f"$B${shape[0]+1}:${excel_columnname(shape[1])}:{shape[0]+1}"
        chartoption['location'] = f"D{shape[0]+3}"
        df2chart(writer, sheetname=sheetname, chartoption=chartoption)
    writer.save()
    writer.close()
