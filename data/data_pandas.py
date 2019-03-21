import pandas as pd 
import os 

def df2excel(data, filename, sheetname="result", newfile=False):
    if os.path.isfile(filename):
        old_data = pd.read_excel(filenaem,sheet_name=None)
    else:
        old_data = None
    
    if newfile:
        old_data = None
    writer = pd.ExcelWriter(filename, engine = 'xlsxwriter')
    if old_data:
        for ws_name, df_sheet in old_data.items():
            df_sheet.to_excel(writer,sheet_name=ws_name)
    else:
        data.to_excel(writer,sheet_name=sheetname)
    
    writer.save()
    write.close()
