import requests
import re
import csv
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
import math
import sys


# Command line arg required
# 1 = scrape yesterday's bookings
# 2 = scrape day before yesterday's bookings
# 3 = scrape bookings 3 days ago
# 30 = max time in past Cobb lets you scrape
try:
    days_back = int(sys.argv[1])
except IndexError:
    print('Please enter a valid command (1, 2, ..., 30)')
    sys.exit()
if days_back not in range(1,31):
    print('Please enter a valid command (1, 2, ..., 30)')
    sys.exit()

the_cols=['timestamp','url','inmate_id','inmate_firstname','inmate_lastname','inmate_middlename','inmate_sex','inmate_race','inmate_age','inmate_dob','inmate_address','booking_timestamp','processing_numbers','agency','facility','charges','severity','court_dates','days_jailed','bond_amount','current_status','release_timestamp','other','notes']
########### Fix processing numbers and bond amount
'http://inmate-search.cobbsheriff.org/inmate/enter_name.shtm'
stamp=str(datetime.now()).split(" ")

d = str(datetime.today() - timedelta(days=days_back)).split(" ")[0]
d_end = str(datetime.today() - timedelta(days=days_back-1)).split(" ")[0]
full_time=stamp[1]
stamp=stamp[0]
full_time=full_time.split(".")[0]
full_time=full_time.replace(":","-")
row_set={'county_name':'cobb','timestamp':' ','url':' ','inmate_id':' ','inmate_firstname':' ','inmate_lastname':' ','inmate_middlename':' ','inmate_sex':' ','inmate_race':' ','inmate_age':' ','inmate_dob':' '
         ,'inmate_address':' ','booking_timestamp':' ','release_timestamp':' ','processing_numbers':' ','agency':' ','facility':' ','charges':' ','severity':' ','bond_amount':' ','current_status':' ','court_dates':' ','days_jailed':' ','other':' ','notes':' '}
race_hash={'b':'black','w':'white','h':'hispanic','a':'asian','m':'middle-eastern','n':'native-american','p':'pacific-islander'}
print('import complete')
none_http_links=[]
inmates=[]
arts=[]
df_charge={'charges':'Inmate Name','severity':'Inmate Name'}
df_key={'timestamp':'n/a','url':'n/a','inmate_id':'SOID','inmate_firstname':'Inmate Name','inmate_lastname':'Inmate Name','inmate_middlename':'Inmate Name','inmate_sex':'R/S','inmate_race':'R/S','inmate_age':'DOB','inmate_dob':'DOB',
'inmate_address':['Address','City','State','Zip'],'booking_timestamp':'Started','release_timestamp':'Released','processing_numbers':'n/a','agency':'n/a','facility':'Location','charges':'Code Section','severity':'Type','bond_amount':'n/a','current_status':'n/a','court_dates':'n/a','days_jailed':'Days in Custody','other':'n/a','notes':'n/a'}
inmate_url={}
inmate_time={}
charges_row={'county_name':'cobb','timestamp':'n/a','url':'n/a','inmate_id':'n/a','booking_timestamp':'n/a','release_timestamp':'n/a','processing_numbers':'n/a','agency':'n/a','facility':'n/a','charges':'n/a','severity':'n/a','bond_amount':'n/a','current_status':'n/a','court_dates':'n/a','days_jailed':'n/a','other':'n/a','notes':'n/a'}
inmate_row={'county_name':'cobb','timestamp':'n/a','url':'n/a','inmate_id':'n/a','inmate_firstname':'n/a','inmate_lastname':'n/a','inmate_middlename':'n/a','inmate_sex':'n/a','inmate_race':'n/a','inmate_age':'n/a','inmate_dob':'n/a','inmate_address':'n/a'}
charges_pd=pd.DataFrame('N/A',index=[],columns=charges_row.keys())
inmate_pd=pd.DataFrame('N/A',index=[],columns=inmate_row.keys())
date={'start_month':d.split("-")[1],'start_day':d.split("-")[2],'start_year':d.split("-")[0],'end_month':d_end.split("-")[1],'end_day':d_end.split("-")[2],'end_year':d_end.split("-")[0]}
'http://inmate-search.cobbsheriff.org/JMS_Admit_Review.asp?BD=9%2F27%2F2017&CCLASS=&ED=9%2F28%2F2017&SK='
url_site='http://inmate-search.cobbsheriff.org/JMS_Admit_Review.asp?BD='+date['start_month']+'%2F'+date['start_day']+'%2F'+date['start_year']+'&CCLASS=&ED='+date['end_month']+'%2F'+date['end_day']+'%2F'+date['end_year']+'&SK='
inmate_dets='http://inmate-search.cobbsheriff.org/'
r = requests.get(url_site)
dfs=pd.read_html(url_site)
print('start')
soup = bs(r.content,"lxml")
inmates_info={}
#### fix for dif webs
for i,table in enumerate(soup.findChildren("table")):
    if i==0:
        continue
    for row in table.findChildren('tr'):
        for j,col in enumerate(row.findChildren('td')):
            if col['class'][0]=='tblheading':
                continue
            if col['class'][0]=='INmateRow' and j==1:
                more_info=col.find_all('a')[0]['href'].split('"')[1]
                im_id=col.find_all('a')[0]['href'].split('"')[3]
                ims=pd.read_html(inmate_dets+more_info)
                del ims[0]
                inmate_url[im_id]=inmate_dets+more_info
                inmate_time[im_id]=str(datetime.now())
                inmates_info[im_id]=ims



main_df=dfs[1]
main_df.columns=list(dfs[1].loc[0].values)
main_df=main_df.drop(0,axis=0)
main_df['Charge']=1
for i in list(main_df.index):
    test=main_df.loc[i]['SOID']
    if math.isnan(float(test)):
        main_df.at[i,'SOID']=soid
    else:
        soid=test
        main_df.at[i,'Charge']=0
for num,i in enumerate(inmates_info.keys()):
    subset_main_df=main_df[main_df['SOID']==i]
    inmate_row_i=dict(row_set)
    print(num)
    for k in the_cols:
        if k=='county_name':
            continue
        if k=='timestamp':
            try:
                inmate_row_i[k]=inmate_time[i].split(".")[0]+' EST'
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='url':
            try:
                inmate_row_i[k]=inmate_url[i]
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='current_status':
            try:
                if type(inmates_info[i][-1].iloc[1][2])==type(inmates_info[i][-1].iloc[1][2]):
                    inmate_row_i[k]=' '
                else:
                    inmate_row_i[k]=inmates_info[i][-1].iloc[1][2]
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='inmate_id':
            try:
                inmate_row_i[k]=str(i)
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='inmate_lastname':
            try:
                inmate_row_i[k] = subset_main_df.iloc[0]['Inmate Name'].split(' ')[0]
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='inmate_firstname':
            try:
                inmate_row_i[k] = subset_main_df.iloc[0]['Inmate Name'].split(' ')[1]
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='inmate_middlename':
            try:
                split_name = subset_main_df.iloc[0]['Inmate Name'].split(' ')
                if len(split_name)>2:
                    inmate_row_i[k] = ' '.join(split_name[2:])
                else:
                    inmate_row_i[k] = ''
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='inmate_sex':
            try:
                inmate_row_i[k]=subset_main_df.iloc[0]['R/S'].split("/")[1].lower()
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='inmate_race':
            try:
                inmate_row_i[k]=race_hash[subset_main_df.iloc[0]['R/S'].split("/")[0].replace(" ","").lower()]
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='inmate_age':
            try:
                inmate_row_i[k]=datetime.today().year-int(subset_main_df.iloc[0]['DOB'])
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='inmate_dob':
            try:
                inmate_row_i[k]=subset_main_df.iloc[0]['DOB']
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='inmate_address':
            try:
                str_l=list(inmates_info[i][0].loc[11])
                inmate_row_i[k]=str(str_l[0])+" "+str(str_l[1])+","+str(str_l[2])+" "+str(str_l[3])
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='booking_timestamp':
            try:
                date_book=str(re.sub(u'\xa0',' ',inmates_info[i][0].loc[3][2]))
                inmate_row_i[k] = str(datetime.strptime(date_book, '%m/%d/%Y %H:%M')) + ' EST'
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='processing_numbers':
            try:
                charg='Case #'
                for p in range(len(inmates_info[i])):
                    if inmates_info[i][p].loc[0][0]=='Charges':
                        x=p+1
                case_num = inmates_info[i][x].loc[1][1]
                if not isinstance(case_num, str):
                    case_num = ''
                charg+=case_num
                inmate_row_i[k]=charg
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='agency':
            try:
                inmate_row_i[k]=inmates_info[i][0].loc[3][0]
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='facility':
            try:
                fac=inmates_info[i][0].loc[7][3]
                if fac!='Released':
                    inmate_row_i[k]=fac
                else:
                    inmate_row_i[k]=' '
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='charges':
            try:
                charge_names = [v for v in list(subset_main_df.iloc[1:]['Inmate Name'])] # all charges from main page
                inmate_row_i[k] = " | ".join(charge_names)
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='severity':
            try:
                inmate_row_i[k] = ''
                first_severity = True
                charge_names = [v for v in list(subset_main_df.iloc[1:]['Inmate Name'])]  # all charges from main page for current inmate
                
                # Look for strings in subpage tables matching the charge strings we got from the main page for the current inmate
                # The subpage charge string is split into 2 cells, code section & description.
                # Crucially, whether it's a felony or misdemeanor is always in the cell to the right of the charge.
                # It's OK if there's more than one of the same charge since it will still be in same category (misdemeanor/felony)
                for charge in charge_names:
                    table_found = False
                    for table in inmates_info[i]:
                       row, col = np.where(table.applymap(lambda cell: charge.startswith(str(cell)))) # location in table containing start of charge
                       if len(row)==0: # charge not found in table
                           continue
                       else:
                           for r, c in zip(row, col): # in case same start of charge happens 2x in same table
                               if not charge.endswith(str(table.iloc[r,c+1])): # 2nd part of charge must match too
                                   continue # next row in this table that has the correct start of charge
                               else: # we have a matching charge
                                   break
                           if not charge.endswith(str(table.iloc[r,c+1])):
                               continue # next table
                           severity = str(table.iloc[r,c+2]).lower()\
                               .replace(' unindicted','')\
                               .replace(' indicted','')\
                               .replace('civil','')\
                               .replace('high & aggravated ','')\
                               .replace('no classification','')\
                               .replace('ordinance','')\
                               .replace('pardons & parole','')\
                               .replace('nan','')
                           if severity != 'misdemeanor' and severity != 'felony' and severity !='':
                               inmate_row_i[k] = ''
                               raise ValueError('Unexpected format of severity "' + severity + '", originating from website severity "' + table.iloc[row,col+2] + '"')
                           table_found = True
                           break
                    if not table_found:
                        inmate_row_i[k] = ''
                        raise ValueError('Main site charge "' + charge + '" not found in subpage. Not storing severity for any charges.')
                    if first_severity:
                        inmate_row_i[k] = severity
                        first_severity = False
                    else:
                        inmate_row_i[k] = inmate_row_i[k] + ' | ' + severity

            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='court_dates':
            try:
                inmate_row_i[k]=' '
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='days_jailed':
            try:
                inmate_row_i[k]=inmates_info[i][0].loc[7][5]
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='bond_amount':
            bond_start=0
            try:
                charg_bond=[]
                charg_num=len(subset_main_df)-1
                remain=0
                for p in range(len(inmates_info[i])):
                    if inmates_info[i][p].loc[0][0]=='Charges':
                        x=p+1
                for p in range(charg_num):
                    try:
                        for s in range(len(inmates_info[i][x+p])):
                            if inmates_info[i][x+p].loc[s][0]=='Bond Amount':
                                if bond_start!=0:
                                    charg_bond.append(' | '+inmates_info[i][x+p].loc[s][1]+' - Bond')
                                else:
                                    charg_bond.append(inmates_info[i][x+p].loc[s][1]+' - Bond')
                                bond_start=1
                                for j in range(len(inmates_info[i][x+p])-s):
                                    if type(inmates_info[i][x+p].loc[s+j+1][1])==type(1.01):
                                        break
                                    elif inmates_info[i][x+p].loc[s+j+1][1]=='Bond Status':
                                        break
                                    else:
                                        charg_bond.append(inmates_info[i][x+p].loc[s+j+1][2]+' - '+inmates_info[i][x+p].loc[s+j+1][1])
                    except IndexError:
                        pass
                sts=', '.join(charg_bond)
                inmate_row_i[k]=sts.replace(', |',' |')
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='release_timestamp':
            try:
                if type(subset_main_df.iloc[0]['Released'])==type(float(5)):
                    inmate_row_i[k]=''
                else:
                    date_release=str(re.sub(u'\xa0',' ',subset_main_df.iloc[0]['Released']))
                    inmate_row_i[k]=str(datetime.strptime(date_release, '%m/%d/%Y %H:%M')) + ' EST'
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='other':
            try:
                inmate_row_i[k]=inmate_row_i[k][0:-2]+', Address where arrested: '+inmates_info[i][x-2].loc[1][2]
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='notes':
            inmate_row_i[k]+=""
    inmates.append(inmate_row_i)

cor_col=['county_name', 'timestamp', 'url', 'inmate_id', 'inmate_lastname', 'inmate_firstname', 'inmate_middlename', 'inmate_sex', 'inmate_race', 'inmate_age', 'inmate_dob', 'inmate_address', 'booking_timestamp', 'release_timestamp', 'processing_numbers', 'agency', 'facility', 'charges', 'severity', 'bond_amount', 'current_status', 'court_dates', 'days_jailed', 'other', 'notes']
with open(r'../../../data/cobb_bookings-from-' + d + '_' + stamp + '_' + full_time + '.csv', 'w') as csvfile:
    spamwriter = csv.writer(csvfile, lineterminator='\n')
    spamwriter.writerow(cor_col)
    for i in inmates:
        spamwriter.writerow([i[j] for j in cor_col])
