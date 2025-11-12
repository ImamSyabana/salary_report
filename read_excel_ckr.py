import pandas as pd

# # 1. Set the option to display a high number of columns (e.g., 50)
# #pd.set_option('display.max_columns', 50)

# # OR, set it to None to display ALL columns, regardless of count
# pd.set_option('display.max_columns', None)

import numpy as np
from pathlib import Path

# Define the path to your Excel file
file_path = 'GAJI NOV 2025.xlsx'

def read_excel(file_path: Path):
    
    df_full = pd.read_excel(file_path, header=None, sheet_name="ckr")


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
    header_driver_idx = data_driver_start_idx - 2  # e.g., 25 - 2 = 23


    # --- 4. Create DataFrame 1 (Office) ---

    # Get the column names from the first header row
    df_office_columns = df_full.iloc[header_office_idx]

    # Get the data for df1
    # It starts at data1_start_idx
    # It ends right before the second table's header (header2_idx)
    df_office_data = df_full.iloc[data_office_start_idx : header_driver_idx - 1]

    # Create the final, clean DataFrame 1
    # This also resets the index automatically
    df_office = pd.DataFrame(df_office_data.values, columns=df_office_columns)

    # ngebenerin nama kolomnya
    new_column_names = [
        'No', 'Nama', 'Jabatan', 'No_rek', 'n_hadir', 'UM_per_hadir', 'Insentif(unit)', 'Insentif(tarif)', 
        'Gaji_pokok', 'Tunj_hdr_komunikasi', 'UM_total', 'Tunj_jab', 'instv_DLR', 'instv_etc_scp_stock', 'kesehatan',
        'Gaji_total', 'potong_BPJS_sehat' , 'potong_BPJS_tng_kerja', 'potong_BON', 'potong_telat', 'gaji_diterima', 
        'misc'
    ]

    # Check length first to be safe
    if len(df_office.columns) == len(new_column_names):
        df_office.columns = new_column_names
        
    else:
        print(f"Error: DataFrame has {len(df_office.columns)} columns, but list has {len(new_column_names)} names.")


    # --- 5. Create DataFrame 2 (Driver) ---

    # Get the column names from the first header row
    df_driver_columns = df_full.iloc[header_office_idx]
    #print(df_driver_columns[:])

    # Get the data for df1
    # It starts at data1_start_idx
    # It ends right before the second table's header (header2_idx)
    df_driver_data = df_full.iloc[data_driver_start_idx : ]

    # Create the final, clean DataFrame 1
    # This also resets the index automatically
    df_driver = pd.DataFrame(df_driver_data.values, columns=df_office_columns)

    new_column_names = [
        'No', 'Nama', 'Jabatan', 'No_rek', 'n_hadir', 'UM_per_hadir', 'Insentif(unit)_kirim_cust', 'Insentif(tarif)_kirim_cust', 
        'Gaji_pokok', 'Tunj_hdr_komunikasi', 'UM_total', 'Tunj_jab', 'instv_DLR', 'instv_etc_scp_stock', 'kesehatan',
        'Gaji_total', 'potong_BPJS_sehat' , 'potong_BPJS_tng_kerja', 'potong_BON', 'potong_telat', 'gaji_diterima', 
        'misc'
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


# # --- 6. Check your results ---
# print("--- DataFrame 1 (First 5 Rows) ---")
# print(df_office.head())
# print(f"\nTotal rows in df_office: {len(df_office)}")

# print("\n" + "---" * 10 + "\n")

# print("--- DataFrame 2 (First 5 Rows) ---")
# print(df_driver.head())
# print(f"\nTotal rows in df_driver: {len(df_driver)}")
