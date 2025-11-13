import pandas as pd

# # 1. Set the option to display a high number of columns (e.g., 50)
# #pd.set_option('display.max_columns', 50)

# # OR, set it to None to display ALL columns, regardless of count
pd.set_option('display.max_columns', None)

import numpy as np
from pathlib import Path

# Define the path to your Excel file
file_path = 'GAJI NOV 2025.xlsx'

#def read_excel(file_path: Path):
def read_excel(file_path):
    df_full = pd.read_excel(file_path, header=None, sheet_name="BGR")


    # 2. Find the row index for the start of each table's data
    try:
        # We use pd.to_numeric to safely find the *number* 1
        # errors='coerce' turns text (like "NO") into NaN, which is ignored
        data_start_indices = df_full[pd.to_numeric(df_full[0], errors='coerce') == 1].index
        
        # Get the index for the first row of data in each table
        data_office_start_idx = data_start_indices[0]  # e.g., index 5
        data_driver_start_idx = data_start_indices[1]  # e.g., index 25
        
    except IndexError:
        print("Error: Could not find two data rows starting with the number 1.")
        # You can add more error handling here
        exit()


    print(data_start_indices)



    # 3. Find the header row index for each table
    # Based on your file, the header is 2 rows *before* the data starts
    header_office_idx = data_office_start_idx - 2  # e.g., 5 - 2 = 3
    header_driver_idx = data_driver_start_idx - 1  # e.g., 25 - 2 = 23


    # --- 4. Create DataFrame 1 (Office) ---

    # Get the column names from the first header row
    df_office_columns = df_full.iloc[header_office_idx]

    def get_end_row_office(df):
        df_office_data = df.iloc[data_office_start_idx:]
        # 1. Create a boolean mask to identify where the 'No' column is NaN.
        nan_mask = df_office_data.iloc[:, 0].isna()

        # 3. Find the index where the stop condition is first met.
        #    We only proceed if the condition is actually found.
        if nan_mask.any():
            # Get the index label of the first row that is NaN
            first_nan_label = df_office_data[nan_mask].index[0]
            
            # Get the positional index (integer) of that label
            stop_position = df_office_data.index.get_loc(first_nan_label)
            
            # Slice the DataFrame up to (but NOT including) the stop position
            df_office_data = df_office_data.iloc[:stop_position]
            
        else:
            # If two NaNs in a row are never found, keep the whole DataFrame
            df_office_data = df_office_data.copy()

        return df_office_data


    # Get the data for df1
    # It starts at data1_start_idx until the end 
    df_office_data = get_end_row_office(df_full)

    # Create the final, clean DataFrame 1
    # This also resets the index automatically
    df_office = pd.DataFrame(df_office_data.values, columns=df_office_columns)

    # ngebenerin nama kolomnya
    new_column_names = [
        'No', 'Nama', 'Jabatan', 'No_rek', 'n_hadir', 'UM_per_hadir', 'Insentif(unit)', 'Insentif(tarif)', 
        'Gaji_pokok', 'Tunj_hdr', 'UM_total', 'Tunj_komunikasi', 'Tunj_jab', 'instv_DLR', 'instv_lembur',
        'Gaji_total', 'potong_BON', 'potong_telat', 'potong_BPJS', 'gaji_diterima'
        
    ]

    # Check length first to be safe
    if len(df_office.columns) == len(new_column_names):
        df_office.columns = new_column_names
        
    else:
        print(f"Error: DataFrame has {len(df_office.columns)} columns, but list has {len(new_column_names)} names.")


    # --- 5. Create DataFrame 2 (Driver) ---

    # Get the column names from the first header row
    df_driver_columns = df_full.iloc[header_office_idx]

    def get_end_row_driver(df):
        df_driver_data = df.iloc[data_driver_start_idx:]
        # 1. Create a boolean mask to identify where the 'No' column is NaN.
        nan_mask = df_driver_data.iloc[:, 0].isna()

        # 2. Create a double-NaN mask.
        #    We check if the current row (nan_mask) AND the previous row (nan_mask.shift(1)) are both True (NaN).
        double_nan_mask = nan_mask & nan_mask.shift(1)

        # 3. Find the index where the stop condition is first met.
        #    We only proceed if the condition is actually found.
        if double_nan_mask.any():
            # Get the index label of the first row that is the *second* NaN in the sequence
            first_stop_label = df_driver_data[double_nan_mask].index[0]
            
            # Get the positional index (integer) of that label
            stop_position = df_driver_data.index.get_loc(first_stop_label)
            
            # Slice the DataFrame up to (but NOT including) the stop position
            df_driver_data = df_driver_data.iloc[:stop_position]
            
        else:
            # If two NaNs in a row are never found, keep the whole DataFrame
            df_driver_data = df_driver_data.copy()

        return df_driver_data

    # Get the data for df1
    # It starts at data1_start_idx until the last record
    df_driver_data = get_end_row_driver(df_full)

    # Create the final, clean DataFrame 1
    # This also resets the index automatically
    df_driver = pd.DataFrame(df_driver_data.values, columns=df_driver_columns)

    new_column_names = [
        'No', 'Nama', 'Jabatan', 'No_rek', 'n_hadir', 'UM_per_hadir', 'Insentif(unit)_kirim_cust', 'Insentif(tarif)_kirim_cust', 
        'Gaji_pokok', 'Tunj_hdr', 'UM_total', 'Tunj_komunikasi', 'Tunj_jab', 'instv_DLR', 'instv_lembur',
        'Gaji_total', 'potong_BON', 'potong_telat', 'potong_BPJS', 'gaji_diterima'
    ]

    # ngebenerin nama kolomnya
    if len(df_driver.columns) == len(new_column_names):
        df_driver.columns = new_column_names
        
    else:
        print(f"Error: DataFrame has {len(df_driver.columns)} columns, but list has {len(new_column_names)} names.")


    # menyiapkan yang mau di insert jadi kolom baru
    insentif_tarif_kirim_post = np.array(df_driver['Insentif(tarif)_kirim_cust'][1::2])
    #print(insentif_tarif_kirim_post)

    insentif_unit_kirim_post = np.array(df_driver['Insentif(unit)_kirim_cust'][1::2])
    #print(insentif_unit_kirim_post)

    # hapus baris yang longkap2
    df_driver = df_driver.dropna(subset=['No'], axis=0)

    # insert kolom baru untuk unit dan tarif post
    df_driver.insert(
        loc=df_driver.columns.get_loc('Insentif(unit)_kirim_cust') + 2, 
        column='Insentif(unit)_kirim_post', 
        value=insentif_unit_kirim_post
    )

    df_driver.insert(
        loc=df_driver.columns.get_loc('Insentif(tarif)_kirim_cust') + 2, 
        column='Insentif(tarif)_kirim_post', 
        value=insentif_tarif_kirim_post
    )

    return df_office, df_driver


df_office, df_driver = read_excel(file_path=file_path)
print(df_driver.columns)
print(df_driver['UM_total'])


# # --- 6. Check your results ---
# print("--- DataFrame 1 (First 5 Rows) ---")
# print(df_office.head())
# print(f"\nTotal rows in df_office: {len(df_office)}")

# print("\n" + "---" * 10 + "\n")

# print("--- DataFrame 2 (First 5 Rows) ---")
# print(df_driver.head())
# print(f"\nTotal rows in df_driver: {len(df_driver)}")
