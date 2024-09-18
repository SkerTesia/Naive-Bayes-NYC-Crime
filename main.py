import pandas as pd
from itertools import product

pd.set_option('display.max_colwidth', None)
dataset = "NYPD.csv"
df = pd.read_csv(dataset) #dataframe
df = df[["CMPLNT_FR_TM", "PD_DESC", "BORO_NM", "PREM_TYP_DESC"]]

'''
print(df["CMPLNT_FR_TM"].head())
print()
print(df["PD_DESC"].head())
print()
print(df["BORO_NM"].head())
print()
print(df[ "PREM_TYP_DESC"].head())

print(df["CMPLNT_FR_TM"].unique())
print()
print(df["PD_DESC"].unique())
print()
print(df["BORO_NM"].unique())
print()
print(df["PREM_TYP_DESC"].unique())

print("time", df["CMPLNT_FR_TM"].size, df["CMPLNT_FR_TM"].unique().size)
print("time", df["PD_DESC"].size, df["PD_DESC"].unique().size)
print("time", df["BORO_NM"].size, df["BORO_NM"].unique().size)
print("time", df[ "PREM_TYP_DESC"].size, df[ "PREM_TYP_DESC"].unique().size)
'''

def get_hour(cas):
    p = cas.find(":")
    return cas[:p]
df["CMPLNT_FR_TM"] = df["CMPLNT_FR_TM"].apply(get_hour)

def prob_of_crime(crime):
    this_crime = df[df["PD_DESC"] == crime].size
    all_crime = df.size
    return this_crime/all_crime
df_PD_DESC = pd.DataFrame(df["PD_DESC"].unique())
df_PD_DESC["probability"] = df_PD_DESC[0].apply(prob_of_crime)
df_PD_DESC.rename(columns = {0: "crime", "probability": "probability"}, inplace = True)
df_crime = df_PD_DESC

def prob_of_param_bycrime(column, value, crime):
    this_location = df[(df[column] == value) & (df["PD_DESC"] == crime)].size
    all_location = df[(df[column] == value)].size
    return this_location / all_location if all_location > 0 else 0

def generate_prob_bycrime(column, crime):
    df_col_bycrime = pd.DataFrame(df[column].unique())
    df_col_bycrime.rename(columns={0: column}, inplace=True)
    df_col_bycrime["probability"] = df_col_bycrime[column].apply(lambda x: prob_of_param_bycrime(column, x, crime))
    return df_col_bycrime
def prob_of_param(column,value):
    this_value = df[df[column] == value].size
    all_values = df.size
    return this_value/all_values if all_values > 0 else 0
def generate_prob(column):
    gen_df = pd.DataFrame(df[column].unique())
    gen_df.rename(columns = {0: column}, inplace = True)
    gen_df["probability"] = gen_df[column].apply(lambda x: prob_of_param(column,x)) #apply vzame 1 parameter in ga da v funkcijo (tu pretvorimo prob_of_c v ;ambda funkcijo, ki dobi en argument x
    return gen_df
print("Generating Probabilities...")
df_time = generate_prob("CMPLNT_FR_TM")
df_area = generate_prob("BORO_NM")
df_loc = generate_prob("PREM_TYP_DESC")

# crime | time area loc | probability --> (P(c) x product P(xi|c))/ product P(xi)
c_unique = df["PD_DESC"].unique()
t_unique = df["CMPLNT_FR_TM"].unique()
a_unique = df["BORO_NM"].unique()
l_unique = df["PREM_TYP_DESC"].unique()

df_final_prob = pd.DataFrame(columns = ["crime", "time", "area", "location"])

print("Enter time of the event, name of NY City borough, specific location (street/appartment/...)")
x = input("Hour:").strip()
y = input("Area:").upper().strip()
z = input("Location:").upper().strip()
print("Calculating Crime Probability for Your Input...")

combinations = list(product(c_unique, [x], [y], [z]))
df_final_prob = pd.DataFrame(combinations, columns=['c', 't', 'a', 'l'])

i = 0
size = len(df_final_prob)
def final_prob(row):
    global i
    if i % 50 == 0:
        print(int(i/size*100),"%")
    i = i + 1
    c = row["c"]
    x1 = row["t"]
    x2 = row["a"]
    x3 = row["l"]

    pc = prob_of_param("PD_DESC", value = c)+1
    px1 = prob_of_param("CMPLNT_FR_TM", value=x1)+1
    px2 = prob_of_param("BORO_NM", value=x2)+1
    px3 = prob_of_param("PREM_TYP_DESC", value=x3)+1

    px1c= prob_of_param_bycrime("CMPLNT_FR_TM", value = x1, crime = c)+1
    px2c = prob_of_param_bycrime("BORO_NM", value= x2, crime = c)+1
    px3c = prob_of_param_bycrime("PREM_TYP_DESC", value= x3, crime = c)+1
    final_prob = (pc*px1c*px2c*px3c)/(px1*px2*px3)
    return final_prob if (px1*px2*px3) > 0 else 0

df_final_prob["prob"] = df_final_prob.apply(final_prob, axis = 1)
df_final_prob.rename(columns = {"c":"Crime Type", "t":"Time", "a":"Area", "l":"Location", "prob":"Probability"}, inplace = True)

print(df_final_prob.sort_values(by="Probability", ascending= False ).head())
