import pandas as pd

t2i_df = pd.read_parquet('s2orc_titles2ids_251117.parquet', engine='pyarrow')

all_df = pd.read_parquet('all_title_list_valid_v2_251117.parquet', engine='pyarrow')

card_df = pd.read_parquet('modelcard_step3_dedup_v2_251117.parquet', engine='pyarrow')

print("---- TITLES TO IDS ----")
#print(t2i_df.shape)
#print(t2i_df.columns)
#print(t2i_df['corpusId'].head().to_string())


print("---- MODEL CARD STEP 3 ----")
print(all_df.shape)
print(all_df.columns)
print(all_df.head().to_string())


#print("---- ALL TITLE LIST ----")
#print(card_df.shape)
#print(card_df.columns)