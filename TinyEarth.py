#!/usr/bin/env python
# coding: utf-8

# Initial TEPI sheet cleaning functions

# In[ ]:


#Cross validating names on sheets

import pandas as pd

def cross_validate_names(df1, df2):
    
    # read csv
    df1 = pd.read_csv(df1).dropna(subset=['FullName'])
    df2 = pd.read_csv(df2)
    
    # edit full names 1
    full_names_1 = []
    fn_lower_1 = []
    for name in list(df1['FullName']):
        full_names_1.append(name.strip())
        fn_lower_1.append(name.strip().lower())
        
    # edit full names 2
    full_names_2 = []
    fn_lower_2 = []
    for index, row in df2.iterrows():
        fn_string = str(row['First Name']) + " " + str(row['Last Name'])
        fn_string = fn_string.split()
        fn_string = ' '.join(fn_string)
        full_names_2.append(fn_string.strip())
        fn_lower_2.append(fn_string.strip().lower())
    df2['Full Name'] = full_names_2
    
    # find new names                           
    new = []
    for name in fn_lower_2:
        if name not in fn_lower_1:
            for name2 in full_names_2:
                if name == name2.lower().strip():
                    new.append(name2)
    
    # new df
    # drop_cols =['Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21', 'Unnamed: 22',
               # 'Title', 'Training Year', 'Training Site',
               # 'Notes', 'TEPI Opt-in Form', 'Mentor']
    new_df = pd.DataFrame().reindex_like(df2).dropna()
    for name in new:
        results = df2.loc[df2['Full Name'] == name]
        new_df = pd.concat([new_df, results])      

    return new_df


# In[ ]:


#Check application status

def check_app_status(df):
    df = pd.read_csv(df)
    
    first_names = []
    for name in list(df['First Name']):
        first_names.append(str(name).strip().capitalize())
     
    last_names = []
    for name in list(df['Last Name']):
        last_names.append(str(name).strip().capitalize())
        
    full_names = []
    for idx in range(len(last_names)):
        full_names.append(first_names[idx] + " " + last_names[idx])
        
    df['Faculty Name'] = full_names
    
    df['Application Status'] = pd.Series(dtype='str')
    
    # check status
    trained_list = check_status(list(df['Faculty Name']))
    for index, row in df.iterrows():
        if row['Faculty Name'] in trained_list:
            row['Application Status'] = 'Trained'
    return df


# In[ ]:


#Merging sheets

def merge_sheets(df1, df2):
    # read csv
    df1 = pd.read_csv(df1)
    df2 = pd.read_csv(df2)
    
    # edit faculty names 1
    edit_names_1 = []
    og_name_1 = []
    for name in list(df1['Faculty Name']):
        og_name_1.append(str(name).strip())
        edit_names_1.append(str(name).strip().lower())
        
    # edit faculty names 2
    edit_names_2 = []
    og_name_2 = []
    for name in list(df2['Faculty Name']):
        og_name_2.append(str(name).strip())
        edit_names_2.append(str(name).strip().lower())
    
    # track duplicates
    duplicates = []
    for idx in range(len(edit_names_1)):
        if edit_names_1[idx] in edit_names_2:
            duplicates.append(og_name_1[idx])

    
    # drop duplicate rows from df1
    for name in duplicates:
        mask = df1['Faculty Name'] == name
        df1 = df1[~mask]
        
    
    # concat
    merged_df = pd.concat([df1, df2])
    merged_df['Application Status'] = pd.Series(dtype='str')
    
    # check status
    trained_list = check_status(list(merged_df['Faculty Name']))
    for index, row in merged_df.iterrows():
        if row['Faculty Name'] in trained_list:
            row['Application Status'] = 'Trained'
      
    return merged_df


# In[ ]:


#check if trained

def check_trained_status(faculty_list):
    tepi_df = pd.read_csv('tepi_list.csv')
    tepi_list = list(tepi_df['FullName'])
    
    trained_list = []
    for name in faculty_list:
        if name in tepi_list:
            trained_list.append(name)
    
    
    return trained_list


# In[ ]:


#add address

def add_address(df):
    tepi_df = pd.read_csv('TEPI_people.csv')
    name_list = list(tepi_df['FullName'])
    tepi_df = tepi_df.set_index('FullName')
    he_df = pd.read_csv(df)
    for index, row in he_df.iterrows():
        name = row['Faculty Name']
        if name in name_list:
            he_df.loc[index, 'Institution'] = tepi_df.loc[name, 'InstitutionName']
            he_df.loc[index, 'State'] = tepi_df.loc[name, 'AddressState']
            he_df.loc[index, 'City'] = tepi_df.loc[name, 'AddressCity']
    he_df = he_df.dropna(subset=['Institution'])
    return he_df


# In[ ]:


#Move address from people to institution

def insert_address(inst, people):
    inst = list(pd.read_csv(inst)['InstitutionName'])
    people = pd.read_csv(people)
    
    address_df = pd.DataFrame()
    address_df['Institution'] = inst
    track = []
    for index, row in people.iterrows():
        institution = row['InstitutionName']
        if institution not in track:
            track.append(institution)
            inst_idx = inst.index(institution)
            address_df.loc[inst_idx, 'City'] = people.loc[index, 'AddressCity']
            address_df.loc[inst_idx, 'State'] = people.loc[index, 'AddressState']
            address_df.loc[inst_idx, 'Country'] = people.loc[index, 'AddressCountry']
    
    return address_df


# In[ ]:


#insert street address

def insert_street(inst, people):
    inst = pd.read_csv(inst)
    people = pd.read_csv(people)
    inst_name = list(inst['InstitutionName'])
    
    
    
    for name in inst_name:
        inst_idx = inst_name.index(name)
        for index, row in people.iterrows():  
            if row['InstitutionName'] == name:
                if row['AddressStreet'] != None:
                    people.loc[index, 'Inputted Address'] = people.loc[index, 'AddressStreet']
                    people.loc[index, 'AddressStreet'] = inst.loc[inst_idx, 'Street']
                
    return people


# In[ ]:


import pandas as pd
def add_netid(tepi, netid):
    tepi = pd.read_csv(tepi)
    netid = pd.read_csv(netid)
    
    netid_dict = {}
    for index, row in netid.iterrows():
        netid_dict[row['Members']] = row['netid']
    
    #format names
    edit_names = []
    og_name = []
    for name in list(tepi['FullName']):
        og_name.append(str(name).strip())
        edit_names.append(str(name).strip().upper())
    tepi['FullName'] = edit_names
      
    for index, row in tepi.iterrows():  
        name = row['FullName']
        if row['FullName'] in netid_dict.keys() and row['NetID'] == None:
            tepi.loc[index, 'NetID'] = netid_dict[name]
    return tepi
            


# In[ ]:


# find empty netid

def extract_nan(tepi, netid):
    tepi = pd.read_csv(tepi, usecols=['FullName', 'NetID'])
    netid = pd.read_csv(netid)
    
    netid_dict = {}
    for index, row in netid.iterrows():
        netid_dict[row['Members']] = row['netid']
    
    #format names
    edit_names = []
    og_name = []
    for name in list(tepi['FullName']):
        og_name.append(str(name).strip())
        edit_names.append(str(name).strip().upper())
    tepi['FullName'] = edit_names
    
    fill_df = tepi.fillna(0)
    
    name_list = []
    for index, row in fill_df.iterrows():  
        if row['NetID'] == 0:
            name_list.append(row['FullName'])
        
    new_dict = {}
    for name in name_list:
        if name in netid_dict.keys():
            new_dict[name] = netid_dict[name]

    return new_dict


# In[1]:


# check if TEPI is subscribed to mailchimp

def mailchimp_sub(people, sub, unsub):
    people = pd.read_csv(people, usecols=['FullName', 'Mailchimp'])
    sub = pd.read_csv(sub, usecols=['First Name', 'Last Name'])
    unsub = pd.read_csv(unsub, usecols=['First Name', 'Last Name'])
    
    sub_list = []
    for index, row in sub.iterrows():
        fn_string = str(row['First Name']) + " " + str(row['Last Name'])
        sub_list.append(fn_string)

    unsub_list = []
    for index, row in unsub.iterrows():
        fn_string = str(row['First Name']) + " " + str(row['Last Name'])
        unsub_list.append(fn_string)
        
    for index, row in people.iterrows():  
        if row['FullName'] in sub_list:
            people.loc[index, 'Mailchimp'] = True
        elif row['FullName'] in unsub_list:
            people.loc[index, 'Mailchimp'] = False
            
    return people


# For Laura's high enrollment request

# In[ ]:


#find high enrollment institutions

import re
def find_high_enrollment(df):
    df = pd.read_csv(df)
    imp_dict = {}
    imp_list = list(df['Implementation – What format (Intro for Majors, Intro for Non-majors, Upper division Majors, Independent Research, other)? Course Subject? What year students? Projected size of class?'])
    name_list = list(df['Faculty Name'])
    for idx in range(len(name_list)):
        imp_dict[name_list[idx]] = imp_list[idx]
        
    candidates = []
    for tepi in imp_dict:
        curr_str = str(imp_dict[tepi])
        num = re.search(r'\D[5-9][0-9]', curr_str)
        if 'Intro' in curr_str or 'intro' in curr_str:
            if num:
                candidates.append(tepi)

    new_df = pd.DataFrame()
    names = []
    info = []
    for index, row in df.iterrows():
        if row['Faculty Name'] in candidates:
            names.append(row['Faculty Name'])
            info.append(row['Implementation – What format (Intro for Majors, Intro for Non-majors, Upper division Majors, Independent Research, other)? Course Subject? What year students? Projected size of class?'])
            
    new_df['Faculty Name'] = names
    new_df['Info'] = info
    
    return new_df


# Comparing DB and mainlist data (task from Trang)

# In[ ]:


#check which institutions were pulled from the mainlist

def main_institutions(inst_df):
    df = list(pd.read_csv(inst_df)['name'])
    mainlist = list(pd.read_csv('mainlist_inst.csv')['Name'])
    
    add = []
    for name in mainlist:
        if name not in df:
            add.append(name)
            
    string = ' - MAINLIST'
    new_add = [x + string for x in add]
        
    df.extend(new_add)
    df = sorted(list(set(df)))
    new_df = pd.DataFrame()
    new_df['Name'] = df
    
    return new_df


# In[ ]:


#cross validating database

def cross_val_db(db_df, db_csv):
    df = list(pd.read_csv(db_df)['Name'])
    name_list1 = []
    for name in df:
        name_list1.append(name.strip())
    
    
    orig = list(pd.read_csv(db_csv)['name'])
    name_list2 = []
    for name in orig:
        name_list2.append(name.strip())
        
        
    orig_list = []
    for name in name_list2:
        if name not in name_list1:
            orig_list.append(name)
    return orig_list


# In[ ]:


def rename_institution(cleaned, main):
    cleaned = list(pd.read_csv(cleaned)['Name'])
    main = list(pd.read_csv(main)['InstitutionName'])
    
    extra = []
    for name in cleaned:
        if name not in main:
            extra.append(name)
    new = pd.DataFrame() 
    new['Name'] = extra
    return new


# In[ ]:


# move addresses from mainlist to DB list

def insert_address_db(db, main):
    db = list(pd.read_csv(db)['Institution Name'])
    main = pd.read_csv(main)
    
    address_df = pd.DataFrame()
    address_df['Institution'] = db
    track = []
    for index, row in main.iterrows():
        institution = row['InstitutionName']
        if institution not in track:
            track.append(institution)
            if institution in db:
                inst_idx = db.index(institution)
                address_df.loc[inst_idx, 'City'] = main.loc[index, 'City']
                address_df.loc[inst_idx, 'State'] = main.loc[index, 'State']
                address_df.loc[inst_idx, 'Country'] = main.loc[index, 'Country']

    return address_df

