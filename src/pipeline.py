"""
pipeline.py
Pipeline ETL buat beres-beresin automobileEDA_dirty_training.csv
Tugas AI Engineering Bootcamp - Data Engineering: Pipeline & Preparation
Jalanin dengan: python src/pipeline.py (dari root folder project)
"""

import pandas as pd
import numpy as np

RAW_PATH = "data/raw/automobileEDA_dirty_training.csv"
PROCESSED_PATH = "data/processed/automobileEDA_processed.csv"


# ---------------------------------------------------------------------------
# EXTRACT
# ---------------------------------------------------------------------------
def load_data(path):
    df = pd.read_csv(path)
    print(f"[LOAD] Baca '{path}' -> {df.shape[0]} baris, {df.shape[1]} kolom")
    return df


# ---------------------------------------------------------------------------
# INSPECT
# ---------------------------------------------------------------------------
def inspect_data(df):
    print("\n" + "=" * 60)
    print("INSPEKSI DATA")
    print("=" * 60)

    print("\n--- 5 baris pertama ---")
    print(df.head())

    print("\n--- Ukuran dataset ---")
    print(df.shape)

    print("\n--- Nama kolom & tipe data ---")
    print(df.dtypes)

    print("\n--- Missing values per kolom ---")
    missing = df.isnull().sum()
    print(missing[missing > 0])

    print("\n--- Baris duplikat ---")
    print(df.duplicated().sum())

    print("\n--- Nilai unik di kolom kategorikal utama ---")
    cat_cols = ["make", "body-style", "drive-wheels", "fuel-system",
                "num-of-doors", "num-of-cylinders"]
    for col in cat_cols:
        print(f"{col}: {sorted(df[col].dropna().unique().tolist())}")


# ---------------------------------------------------------------------------
# CLEAN
# ---------------------------------------------------------------------------
def clean_data(df):
    df = df.copy()

    before_rows = df.shape[0]
    before_missing = df.isnull().sum().sum()

    #
    text_cols_to_normalize = ["make", "body-style", "drive-wheels", "fuel-system"]
    for col in text_cols_to_normalize:
        is_null = df[col].isnull()
        df[col] = df[col].astype(str).str.strip().str.lower()
        df.loc[is_null, col] = np.nan  # balikin NaN asli (astype(str) bikin NaN jadi teks "nan")

    
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], format="mixed", dayfirst=True, errors="coerce"
    )

 
    duplicates_removed = int(df.duplicated().sum())
    df = df.drop_duplicates()

   
    numeric_fill_cols = ["stroke", "horsepower", "price"]
    for col in numeric_fill_cols:
        df[col] = df[col].fillna(df[col].median())

    
    categorical_fill_cols = ["make", "num-of-doors", "horsepower-binned"]
    for col in categorical_fill_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

   

    after_rows = df.shape[0]
    after_missing = int(df.isnull().sum().sum())

    print("\n" + "=" * 60)
    print("RINGKASAN CLEANING")
    print("=" * 60)
    print(f"Jumlah baris sebelum/sesudah: {before_rows} -> {after_rows}")
    print(f"Baris duplikat yang dihapus: {duplicates_removed}")
    print(f"Total missing values sebelum/sesudah: {int(before_missing)} -> {after_missing}")
    changed_cols = text_cols_to_normalize + ["transaction_date"] + numeric_fill_cols + categorical_fill_cols
    print(f"Kolom yang berubah: {changed_cols}")

    return df


# ---------------------------------------------------------------------------
# TRANSFORM
# ---------------------------------------------------------------------------
def transform_data(df):
    df = df.copy()

  
    hp = df["horsepower"]
    df["horsepower_scaled"] = (hp - hp.min()) / (hp.max() - hp.min())

   
    word_to_num = {
        "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "eight": 8, "twelve": 12,
    }
    df["num-of-doors_encoded"] = df["num-of-doors"].map(word_to_num)
    df["num-of-cylinders_encoded"] = df["num-of-cylinders"].map(word_to_num)

    print("\n" + "=" * 60)
    print("RINGKASAN TRANSFORMASI (contoh sebelum vs sesudah)")
    print("=" * 60)
    print(df[["horsepower", "horsepower_scaled",
              "num-of-doors", "num-of-doors_encoded",
              "num-of-cylinders", "num-of-cylinders_encoded"]].head())

    return df


# ---------------------------------------------------------------------------
# LOAD (simpan hasil)
# ---------------------------------------------------------------------------
def save_data(df, path):
    df.to_csv(path, index=False)
    print(f"\n[SAVE] Hasil disimpan ke '{path}' "
          f"({df.shape[0]} baris, {df.shape[1]} kolom)")


# ---------------------------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------------------------
def run_pipeline():
    df_raw = load_data(RAW_PATH)
    inspect_data(df_raw)
    df_clean = clean_data(df_raw)
    df_final = transform_data(df_clean)
    save_data(df_final, PROCESSED_PATH)


if __name__ == "__main__":
    run_pipeline()
