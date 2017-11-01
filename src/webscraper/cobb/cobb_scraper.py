import requests
import re
import sys
import csv
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
import pickle
from datetime import datetime, timedelta
import math

the_cols=['timestamp','url','inmate_id','inmate_firstname','inmate_lastname','inmate_middlename','inmate_sex','inmate_race','inmate_age','inmate_dob','inmate_address','booking_timestamp','processing_numbers','agency','facility','charges','severity','court_dates','days_jailed','bond_amount','current_status','release_timestamp','other','notes']
########### Fix processing numbers and bond amount
'http://inmate-search.cobbsheriff.org/inmate/enter_name.shtm'
stamp=str(datetime.now()).split(" ")
d = str(datetime.today() - timedelta(days=3)).split(" ")[0]
full_time=stamp[1]
stamp=stamp[0]
full_time=full_time.split(".")[0]
full_time=full_time.replace(":","-")
row_set={'county_name':'cobb','timestamp':' ','url':' ','inmate_id':' ','inmate_firstname':' ','inmate_lastname':' ','inmate_middlename':' ','inmate_sex':' ','inmate_race':' ','inmate_age':' ','inmate_dob':' '
         ,'inmate_address':' ','booking_timestamp':' ','release_timestamp':' ','processing_numbers':' ','agency':' ','facility':' ','charges':' ','severity':' ','bond_amount':' ','current_status':' ','court_dates':' ','days_jailed':' ','other':' ','notes':' '}
race_hash={'b':'black','w':'white','h':'hispanic','a':'asian','m':'middle-eastern','n':'native-american','p':'pacific-islander'}
print('import complete')
#col_names={'other':,'days_jailed':,'court_dates':,'current_status':,'bond_amount':,'severity':,'charges':,'facility':,'agency':,'processing_numbers':,'release_timestamp':,'booking_timestamp':,'inmate_address':,'inmate_dob':,'inmate_age':,'inmate_race':,'inmate_sex':,'inmate_middlename':,'inmate_firstname':,'inmate_lastname':,'inmate_id':,'url':,'timestamp':,'county_name':}
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
date={'start_month':d.split("-")[1],'start_day':d.split("-")[2],'start_year':d.split("-")[0],'end_month':stamp.split("-")[1],'end_day':stamp.split("-")[2],'end_year':stamp.split("-")[0]}
'http://inmate-search.cobbsheriff.org/JMS_Admit_Review.asp?BD=9%2F27%2F2017&CCLASS=&ED=9%2F28%2F2017&SK='
url_site='http://inmate-search.cobbsheriff.org/JMS_Admit_Review.asp?BD='+date['start_month']+'%2F'+date['start_day']+'%2F'+date['start_year']+'&CCLASS=&ED='+date['end_month']+'%2F'+date['end_day']+'%2F'+date['end_year']+'&SK='
inmate_dets='http://inmate-search.cobbsheriff.org/'
r = requests.get(url_site)
dfs=pd.read_html(url_site)
print('start')
#print(url_site)
soup = bs(r.content,"lxml")
#soup=soup.prettify()
inmates_info={}
#### fix for dif webs
for i,table in enumerate(soup.findChildren("table")):
    if i==0:
        continue
    #print(table)
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
                inmate_time[im_id]=str(datetime.now())#.replace(" ","_")
                inmates_info[im_id]=ims
                #rm=requests.get(inmate_dets+more_info)
                #inmate  = bs(rm.content,"lxml")
                #sys.exit()
            #print(col['class'])


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
    #print(inmates_info[i][7])
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
        if k=='inmate_id':
            try:
                inmate_row_i[k]=i
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='inmate_firstname':
            try:
                inmate_row_i[k]=subset_main_df.iloc[0]['Inmate Name'].split(" ")[0]
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='inmate_lastname':
            try:
                if len(subset_main_df.iloc[0]['Inmate Name'].split(" "))==3:
                    inmate_row_i[k]=subset_main_df.iloc[0]['Inmate Name'].split(" ")[2]
                elif len(subset_main_df.iloc[0]['Inmate Name'].split(" "))==2:
                    inmate_row_i[k]=subset_main_df.iloc[0]['Inmate Name'].split(" ")[1]
                elif len(subset_main_df.iloc[0]['Inmate Name'].split(" "))>3:
                    inmate_row_i[k]=subset_main_df.iloc[0]['Inmate Name'].split(" ")[-1]
                else:
                    raise Exception
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='inmate_middlename':
            try:
                if len(subset_main_df.iloc[0]['Inmate Name'].split(" "))==3:
                    inmate_row_i[k]=subset_main_df.iloc[0]['Inmate Name'].split(" ")[1]
                elif len(subset_main_df.iloc[0]['Inmate Name'].split(" "))==2:
                    inmate_row_i[k]=' '
                elif len(subset_main_df.iloc[0]['Inmate Name'].split(" "))>3:
                    inmate_row_i[k]=' '.join(subset_main_df.iloc[0]['Inmate Name'].split(" ")[1:-1])
                else:
                    raise Exception
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
                inmate_row_i[k]=date_book.split(" ")[0].split("/")[2]+'-'+date_book.split(" ")[0].split("/")[0]+'-'+date_book.split(" ")[0].split("/")[1]+' '+date_book.split(" ")[1]+':00 EST'
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='processing_numbers':
            try:
                charg='Case #'
                for p in range(len(inmates_info[i])):
                    if inmates_info[i][p].loc[0][0]=='Charges':
                        x=p+1
                charg+=inmates_info[i][x].loc[1][1]
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
                inmate_row_i[k]=inmates_info[i][0].loc[7][3]
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='charges':
            try:
                charg=''
                for p in list(subset_main_df.index):
                    if 1==subset_main_df.loc[p]['Charge']:
                        charg+=subset_main_df.loc[p]['Inmate Name']+'| '
                inmate_row_i[k]=charg[0:-2]
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='severity':
            try:
                for p in range(len(inmates_info[i])):
                    if inmates_info[i][p].loc[0][0]=='Charges':
                        x=p+1
                charg=''
                inmates_info[i][x].loc[1][1]
                for z in range(len(inmates_info[i][x])):
                    if inmates_info[i][x].loc[z][2]=='Description':
                        z+=1
                        break                
                charg_num=len(subset_main_df)-1
                if (type(inmates_info[i][x].loc[z+1][2])==type(1.01) and inmates_info[i][x].loc[z+2][0]=='Bond Amount') or inmates_info[i][x].loc[z+1][0]=='Bond Amount':
                    remain=0
                    for p in range(charg_num):
                        if remain>=charg_num:
                            break
                        for z in range(len(inmates_info[i][x+p])):
                            if inmates_info[i][x+p].loc[z][2]=='Description':
                                z+=1
                                break    
                        charg_ind=str(inmates_info[i][x+p].loc[z][3])+'|'
                        charg+=charg_ind.split(" ")[0]+'|'
                        try:
                            inmate_row['other']+=charg_ind.split(" ")[1]+'|'
                        except:
                            pass
                        remain+=1
                        for a in range(len(inmates_info[i][x+p])-z):
                            if type(inmates_info[i][x+p].loc[z+a][3])==type(float(0)) or 'BondingInfo'==inmates_info[i][x+p].loc[z+a][3]:
                                continue
                            elif 'violation' in inmates_info[i][x+p].loc[z+a][3].lower() or 'petty' in inmates_info[i][x+p].loc[z+a][3].lower() or 'misdemeanor' in inmates_info[i][x+p].loc[z+a][3].lower() or 'felony' in inmates_info[i][x+p].loc[z+a][3].lower():
                                charg_ind=str(inmates_info[i][x+p].loc[z+a][3])
                                charg+=charg_ind.split(" ")[0]+'|'
                                try:
                                    inmate_row['other']+=charg_ind.split(" ")[1]+'|'
                                except:
                                    pass
                                remain+=1
                        
                else:
                    for p in range(len(inmates_info[i][x])-z):
                        if type(inmates_info[i][x].loc[z+p][3])==type(float(0)) or 'BondingInfo'==inmates_info[i][x].loc[z+p][3]:
                            continue
                        elif 'violation' in inmates_info[i][x].loc[z+p][3].lower() or 'petty' in inmates_info[i][x].loc[z+p][3].lower() or 'misdemeanor' in inmates_info[i][x].loc[z+p][3].lower() or 'felony' in inmates_info[i][x].loc[z+p][3].lower():
                            charg_ind=str(inmates_info[i][x].loc[z+p][3])
                            charg+=charg_ind.split(" ")[0]+'|'
                            try:
                                inmate_row['other']+=charg_ind.split(" ")[1]+'|'
                            except:
                                pass
                charg=charg[0:-1]
                inmate_row_i[k]=charg
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
                charg_bond=''
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
                                    charg_bond+='| '
                                charg_bond+=inmates_info[i][x+p].loc[s][1]+' -Bond, '
                                bond_start=1
                                for j in range(7):
                                    if type(inmates_info[i][x+p].loc[s+j+1][1])==type(1.01):
                                        break
                                    elif inmates_info[i][x+p].loc[s+j+1][1]=='Bond Status':
                                        break
                                    else:
                                        charg_bond+=inmates_info[i][x+p].loc[s+j+1][2]+' -'+inmates_info[i][x+p].loc[s+j+1][1]+', '
                    except IndexError:
                        pass
                inmate_row_i[k]=charg_bond
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='current_status':
            pass
        if k=='release_timestamp':
            try:
                if type(subset_main_df.iloc[0]['Released'])==type(float(5)):
                    inmate_row_i[k]=' '
                else:
                    date_book=str(re.sub(u'\xa0',' ',subset_main_df.iloc[0]['Released']))
                    inmate_row_i[k]=date_book.split(" ")[0].split("/")[2]+'-'+date_book.split(" ")[0].split("/")[0]+'-'+date_book.split(" ")[0].split("/")[1]+' '+date_book.split(" ")[1]+':00 EST'
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='other':
            try:
                inmate_row_i[k]='Address where arrested: '+inmates_info[i][x-2].loc[1][2]
            except Exception as e:
                inmate_row_i['notes']+=' Error with column '+k+': '+str(e)+' | '
        if k=='notes':
            inmate_row_i[k]+="If the inmate has been released the location will only show 'released', court dates or current status were not given for this county, "
    inmates.append(inmate_row_i)

cor_col=['county_name', 'timestamp', 'url', 'inmate_id', 'inmate_lastname', 'inmate_firstname', 'inmate_middlename', 'inmate_sex', 'inmate_race', 'inmate_age', 'inmate_dob', 'inmate_address', 'booking_timestamp', 'release_timestamp', 'processing_numbers', 'agency', 'facility', 'charges', 'severity', 'bond_amount', 'current_status', 'court_dates', 'days_jailed', 'other', 'notes']
with open(r'../../../data/cobb_'+stamp+'-'+full_time+'.csv', 'w') as csvfile:
    spamwriter = csv.writer(csvfile, lineterminator='\n')
    spamwriter.writerow(cor_col)
    for i in inmates:
        spamwriter.writerow([i[j] for j in cor_col])
