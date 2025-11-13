from read_excel_ckr import read_excel
import pandas as pd
import json
import numpy as np

from read_excel_bgr import read_excel

# Define the path to your Excel file
#file_path = 'GAJI NOV 2025.xlsx'


def check_excel(df_office, df_driver):
    # bikin fungsi untuk check admin
    uang_makan_total_OFFICE = df_office['n_hadir'] * df_office['UM_per_hadir']
    insentive_dealer_OFFICE = df_office['Insentif(unit)'] * df_office['Insentif(tarif)']

    ## Buat ngitung gaji total (sebelum kena potongan)
    df_office['Gaji_pokok'] = pd.to_numeric(df_office['Gaji_pokok'], errors='coerce')
    df_office['Tunj_hdr'] = pd.to_numeric(df_office['Tunj_hdr'], errors='coerce')
    df_office['Tunj_komunikasi'] = pd.to_numeric(df_office['Tunj_komunikasi'], errors='coerce')
    df_office['Tunj_jab'] = pd.to_numeric(df_office['Tunj_jab'], errors='coerce')
    df_office['instv_lembur'] = pd.to_numeric(df_office['instv_lembur'], errors='coerce')
   

    uang_makan_total_OFFICE = pd.to_numeric(uang_makan_total_OFFICE, errors='coerce')
    insentive_dealer_OFFICE = pd.to_numeric(insentive_dealer_OFFICE, errors='coerce')

    #print(df_office['Insentif(unit)'])
    gajiTotal_OFFICE = (df_office['Gaji_pokok'].fillna(0) + 
                df_office['Tunj_hdr'].fillna(0) + 
                uang_makan_total_OFFICE.fillna(0) + 
                df_office['Tunj_komunikasi'].fillna(0) + 
                df_office['Tunj_jab'].fillna(0) + 
                insentive_dealer_OFFICE.fillna(0) + 
                df_office['instv_lembur'].fillna(0))
                


    # buat ngitung gaji diterima (setelah kena potongan)
    df_office['potong_BPJS'] = pd.to_numeric(df_office['potong_BPJS'], errors='coerce')
    df_office['potong_BON'] = pd.to_numeric(df_office['potong_BON'], errors='coerce')
    df_office['potong_telat'] = pd.to_numeric(df_office['potong_telat'], errors='coerce')

    gaji_diterima_OFFICE = (gajiTotal_OFFICE.fillna(0) -
                    df_office['potong_BON'].fillna(0) -
                    df_office['potong_telat'].fillna(0) -
                    df_office['potong_BPJS'].fillna(0)
                    )


    # Replace all NaN/inf values with None (which becomes JSON null)
    #
    # vvvvvv ADD THESE LINES HERE vvvvvv
    uang_makan_total_OFFICE.replace([np.nan, np.inf, -np.inf], 0, inplace=True)
    insentive_dealer_OFFICE.replace([np.nan, np.inf, -np.inf], 0, inplace=True)
    gajiTotal_OFFICE.replace([np.nan, np.inf, -np.inf], 0, inplace=True)
    gaji_diterima_OFFICE.replace([np.nan, np.inf, -np.inf], 0, inplace=True)
    # ^^^^^^ END OF NEW LINES ^^^^^^


    # bikin fungsi untuk check driver
    uang_makan_total_DRIVER = df_driver['n_hadir'] * df_driver['UM_per_hadir']
    insentive_dealer_DRIVER = (df_driver['Insentif(unit)_kirim_cust'] * df_driver['Insentif(tarif)_kirim_cust'] + 
                            df_driver['Insentif(unit)_kirim_post'] * df_driver['Insentif(tarif)_kirim_post'])


    ## Buat ngitung gaji total (sebelum kena potongan)
    df_driver['Gaji_pokok'] = pd.to_numeric(df_driver['Gaji_pokok'], errors='coerce')
    df_driver['Tunj_hdr'] = pd.to_numeric(df_driver['Tunj_hdr'], errors='coerce')
    df_driver['Tunj_komunikasi'] = pd.to_numeric(df_driver['Tunj_komunikasi'], errors='coerce')
    df_driver['Tunj_jab'] = pd.to_numeric(df_driver['Tunj_jab'], errors='coerce')
    df_driver['instv_lembur'] = pd.to_numeric(df_driver['instv_lembur'], errors='coerce')
   

    uang_makan_total_DRIVER = pd.to_numeric(uang_makan_total_DRIVER, errors='coerce')
    insentive_dealer_DRIVER = pd.to_numeric(insentive_dealer_DRIVER, errors='coerce')

    #print(df_office['Insentif(unit)'])
    gajiTotal_DRIVER = (df_driver['Gaji_pokok'].fillna(0) + 
                df_driver['Tunj_hdr'].fillna(0) + 
                uang_makan_total_DRIVER.fillna(0) + 
                df_driver['Tunj_komunikasi'].fillna(0) + 
                df_driver['Tunj_jab'].fillna(0) + 
                insentive_dealer_DRIVER.fillna(0) + 
                df_driver['instv_lembur'].fillna(0) 
                )


    # buat ngitung gaji diterima (setelah kena potongan)
    df_driver['potong_BPJS'] = pd.to_numeric(df_driver['potong_BPJS'], errors='coerce')
    df_driver['potong_BON'] = pd.to_numeric(df_driver['potong_BON'], errors='coerce')
    df_driver['potong_telat'] = pd.to_numeric(df_driver['potong_telat'], errors='coerce')

    gaji_diterima_DRIVER = (gajiTotal_DRIVER.fillna(0) -
                    df_driver['potong_BON'].fillna(0) -
                    df_driver['potong_telat'].fillna(0) -
                    df_driver['potong_BPJS'].fillna(0)
                    )

    # --- (Alternative Fix) ---
    # Replace all NaN/inf values with None (which becomes JSON null)
    #
    # vvvvvv ADD THESE LINES HERE vVvvvv
    uang_makan_total_DRIVER.replace([np.nan, np.inf, -np.inf], 0, inplace=True)
    insentive_dealer_DRIVER.replace([np.nan, np.inf, -np.inf], 0, inplace=True)
    #gaji_pokok_DRIVER.replace([np.nan, np.inf, -np.inf], 0, inplace=True)
    gajiTotal_DRIVER.replace([np.nan, np.inf, -np.inf], 0, inplace=True)
    gaji_diterima_DRIVER.replace([np.nan, np.inf, -np.inf], 0, inplace=True)
    # ^^^^^^ END OF NEW LINES ^^^^^^

    final_refrence_dict = {
        "office" : [],
        "driver" : []
    }


    for x in range(len(df_office)):
        
        add_office = {
            'Nama' : df_office['Nama'][x],
            'UM_Total': uang_makan_total_OFFICE[x],
            'instv_DLR' : insentive_dealer_OFFICE[x],
            'Gaji_pokok': df_office['Gaji_pokok'][x],
            'Gaji_total' : gajiTotal_OFFICE[x],
            'Gaji_diterima' : gaji_diterima_OFFICE[x]
        }

        final_refrence_dict['office'].append(add_office)
        

    for x in range(0, len(df_driver) * 2, 2):

        add_driver = {
            'Nama' : df_driver['Nama'][x],
            'UM_Total': uang_makan_total_DRIVER[x],
            'instv_DLR' : insentive_dealer_DRIVER[x],
            'Gaji_pokok': df_driver['Gaji_pokok'][x],
            'Gaji_total' : gajiTotal_DRIVER[x],
            'Gaji_diterima' : gaji_diterima_DRIVER[x]
        }

        final_refrence_dict['driver'].append(add_driver)
        
    class NumpyEncoder(json.JSONEncoder):
        """Custom JSON encoder to handle NumPy types."""
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                # Check for NaN and return None (which serializes to JSON null)
                if np.isnan(obj):
                    return None
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            

            # # --- THIS IS THE FIX ---
            # # Add a check for standard Python float NaN
            # elif isinstance(obj, float) and np.isnan(obj):
            #     return None
            # # -----------------------
            
            return json.JSONEncoder.default(self, obj)
        

    # Convert the Python dictionary to a JSON string
    final_refrence_json = json.dumps(final_refrence_dict, indent=4, cls=NumpyEncoder)

    return final_refrence_json
