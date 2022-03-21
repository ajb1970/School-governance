import pandas as pd
import numpy as np
import datetime
import os
from time import time
from OSGridConverter import OSGridReference
from re import sub
#from edubase import *
from requests import get
from urllib.request import urlopen
#from neubase import *

colors = [
    '#0070C0', '#FF0000', '#00B050', '#FFFF00', '#990099', '#9966FF',
    '#006666', '#99FF99', '#FF9900', '#FFCC66', '#333399', '#66CCFF',
    '#000000',
    '#44D7A8', '#45A27D', '#4F86F7', '#6F2DA8', '#738276', '#A6E7FF',
    '#B2F302', '#BD8260', '#C95A49', '#CEC8EF', '#DA2647', '#DA614E',
    '#DB91EF', '#FC5A8D', '#FF5050', '#FF878D', '#FF8866', '#FFCFF1',
    '#FFD0B9', '#FFD12A', '#FFD3F8','#FFE4CD', '#FFFF31', '#9B7653',

    '#C46210', '#2E5894', '#9C2542', '#BF4F51', '#A57164', '#58427C',
    '#4A646C', '#85754E', '#319177', '#0A7E8C', '#9C7C38', '#8D4E85',
    '#8FD400', '#D98695', '#757575', '#0081AB', '#FE4C40', '#FFB97B',
    '#FBE870', '#AFE313', '#5FA777', '#00CCCC', '#02A4D3', '#A9B2C3',
    '#766EC8', '#803790', '#EBB0D7', '#FBAED2', '#FF91A4', '#DEA681',
    '#837050', '#8B8680',

    '#CC3336', '#FF9980', '#FBE7B2', '#FAFA37', '#9DE093', '#00CC99',
    '#2D383A', '#2887C8', '#8D90A1', '#6B3FA0', '#732E6C', '#A50B5E',
    '#FDD7E4', '#E97451', '#FFCBA4', '#C9C0BB',

    '#FD0E35', '#B33B24', '#E77200', '#FFEB00', '#C5E17A', '#33CC99',
    '#8FD8D8', '#4997D0', '#4570E6', '#3F26BF', '#D6AEDD', '#BB3385',
    '#FFA6C9', '#CA3435', '#664228', '#D9D6CF',

    '#C32148', '#FE6F5E', '#ECB176', '#F1E788', '#BEE64B', '#93DFB8',
    '#008080', '#47ABCC', '#C3CDE6', '#6456B7', '#733380', '#C8509B',
    '#FFB7D5', '#A55353', '#D27D46', '#E6BC5C',
    ]


na_clean=['-','*','..','.','SUPP','NA','NP','NE','NaN','DNS', ':']

# ONS + OBR Nov 2017
inflation_obr = {
  2009:0.882387192118227,
  2010:0.898524630541872,
  2011:0.911002709359606,
  2012:0.930131527093596,
  2013:0.945471921182266,
  2014:0.959359113300493,
  2015:0.965935467980296,
  2016:0.985221674876847,
  2017:1,
  2018:1.014,
  2019:1.027182
  }

inflation_obr_oct2018 = {
  2013 : 0.923578616548053,
2014 : 0.935445853884057,
2015 : 0.94292300155942,
2016 : 0.963822823819117,
2017 : 0.98212296658626,
2018 : 1,
2019 : 1.01789380136683 }



inflation_obr_2018 = {
2009 : 0.863823131351172,
2010 : 0.87960626334115,
2011 : 0.892273625934073,
2012 : 0.910811100005109,
2013 : 0.926367221794604,
2014 : 0.939796120203845,
2015 : 0.94613379049744,
2016 : 0.967029366267645,
2017 : 0.985053344831151,
2018 : 1,
2019 : 1.01570384822796,
2020 : 1.03257277691375,
2021 : 1.05051775941513,
2022 : 1.06983222466903,
2023 : 1.0885086076891637,
2024 : 1.1075110299467328,
2025 : 1.1268451832067985,
2026 : 1.1465168585972774,
2027 : 1.1665319483435483,
2028 : 1.1868964475333414,
2029 : 1.2076164559124372 }

# ONS GDP + NAO
inflation_nao = {
2009:0.883467430811778,
2010:0.899624625058668,
2011:0.912117979827459,
2012:0.931270215500039,
2013:0.946629389651948,
2014:0.96053358279014,
2015:0.967117988394584,
2016:1,
2017:1.0183752417795,
2018:1.03384912959381,
2019:1.05125725338491
}

inflation_neu = {
2015 : .888577760246363,
2016 : .918948054306782,
2017 : .933828560795753,
2018 : .955546163653202,
2019 : 1.00,
2020 : 1.04077754368703,
2021 : 1.06948325806582,
2022 : 1.09904475955655,
2023 : 1.11681631476147,
2024 : 1.1345878699664,
}



inflation = inflation_neu

def now():
    return str(datetime.datetime.now())[:-7].replace('-','').replace(' ','_').replace(':','')

def load_pickle( dataframe ):
    return pd.read_pickle( f'pickles/{dataframe}.pickle' )

def load_pickles():
    data = {}
    files = os.listdir('pickles')
    pickles = []
    for f in files:
        if f[-7:] =='.pickle':
            pickles.append( f[:-7] )
    for df in pickles:
        data[ df ] = pd.read_pickle( 'pickles/'+df+'.pickle')
    return data

def save_pickle( dataframe, name, folder = "" ):
    if not( os.path.exists('pickles/' +folder) ):
        os.mkdir( 'pickles/' + folder )
        folder += "/"
    dataframe.to_pickle( 'pickles/' + folder + name + '.pickle' )

def save_pickles( dataframe_dict, folder = "" ):
    if folder != "":
        if not( os.path.exists(folder) ):
            os.mkdir( 'pickles/' + folder )
            folder += "/"
    for df in list(dataframe_dict.keys()):
        dataframe_dict[ df ].to_pickle( 'pickles/' + folder + df + '.pickle' )

def list_pickles():
    pin = os.walk('pickles')
    pout = []
    for folder in pin:
        f = folder[0][8:]
        if len(f)>0:
            f += '/'
        for p in folder[2]:
            pout.append(f+p[:-7])
    return pout


def import_spreadsheet( file_details ):
    """
    Reads a spreadhseet from a CSV, XLS or XLSX file.
    Input:
    file_details: Dictionary with read
    Returns: Dataframe
    """
    if file_details['file'][-4:].lower() == '.csv':
        return import_csv( file_details )
    else:
        return import_excel( file_details )


def import_excel( file_details ):
    print( file_details['file'] )
    xls = file_details.copy()
    file = xls['file']
    del xls['file']
    xls['na_values']=na_clean
    dtypes = xls['dtype']
    del xls['dtype']
    if 'agg' in xls.keys():
        del xls['agg']
    index_col = xls['names'][xls['index_col']]
    del xls['index_col']
    df = pd.read_excel( file, **xls )
    for key in xls.keys():
        if key not in xls.keys():
            del xls[ key ]
    keys_to_remove = []
    for key in dtypes.keys():
        if key not in df.columns:
            keys_to_remove.append( key )
    for key in keys_to_remove:
        del dtypes[ key ]
    df = df.astype( dtypes, errors='ignore')
    df.set_index( index_col, inplace=True )
    return df


def import_csv( file_details ):
    csv = file_details.copy()
    file = csv['file']
    del csv['file']
    csv['na_values'] = na_clean
    csv['dayfirst']=True
    csv['thousands']=','
    if 'agg' in csv.keys():
        del csv['agg']
    return pd.read_csv( file, **csv )



def urn_update_ballot(data, urn_index=False, urn_name='urn', unique_index_output=False, newest_urn=None):
    urns = load_pickle('urn_links_ballot')
    urns = urns.loc[ urns['NEW_URN'] > urns.index]
    if not newest_urn is None:
        urns = urns.loc[ urns['NEW_URN'] <= newest_urn ]
#    data[ urn_name ] =data[ urn_name ].apply(pd.to_numeric, errors='coerce')
    if unique_index_output:
        edubase = load_pickle('edubase')
        edu = edubase[['EstablishmentStatus (name)']].rename(columns={'EstablishmentStatus (name)':'urn_update_open_close'})
        data = data.merge( edu, how='left', left_index=True, right_index=True )
        data.sort_values(['urn_update_open_close',urn_name], inplace=True)
        data_len = len(data)
        data.drop_duplicates( subset = urn_name, inplace=True, keep='last' )
        print('Duplicates dropped from data: {0}'.format(data_len-len(data)))
        data.drop( columns = ['urn_update_open_close'], inplace=True )
        if urn_index:
            data_urns = data.index.tolist()
        else:
            data_urns = data[ urn_name ].dropna( urn_name ).tolist()
        urns_len = len(urns)
        urns = urns.loc[ ~( (urns.index.isin( data_urns )) & ( urns.NEW_URN.isin( data_urns ))) ]
        print('Split ends dropped from URN links: {0}'.format(urns_len-len(urns)))
    if urn_index:
        data_urns = pd.DataFrame( { 'latest_urn': data.index }, index = data.index )
    else:
        data_urns = data.copy()
        data_urns = data_urns.dropna(subset=[ urn_name ])
        data_urns = data_urns[[ urn_name ]]
        data_urns = data_urns.apply(pd.to_numeric)
        data_urns = data_urns.drop_duplicates(keep='first')
        data_urns = data_urns[ (data_urns[ urn_name ] > 99999) & (data_urns[ urn_name ] < 500000 ) ]
        data_urns['latest_urn'] = data_urns[ urn_name ]
        data_urns.set_index( urn_name, inplace=True )
    matches=1
    while matches>0:
        data_urns = data_urns.merge( urns, how='left', left_on='latest_urn', right_index=True )
        matches = data_urns['NEW_URN'].count()
        print('matches: {0}'.format( matches ) )
        data_urns.loc[ data_urns['NEW_URN'].notnull(), 'latest_urn' ] = data_urns['NEW_URN']
        data_urns.drop(columns=['NEW_URN'],inplace=True)
    if urn_index:
        data = data.merge( data_urns, how='left', left_index=True , right_index=True )
        data['old_urn'] = data.index
    else:
        data = data.merge( data_urns, how='left', left_on = urn_name, right_index=True )
        data.rename( columns = { urn_name: 'old_urn' }, inplace=True)
        data.rename( columns = { 'latest_urn':urn_name }, inplace=True)
    if unique_index_output:
        data = data.merge( edu, how='left', left_on=urn_name, right_index=True )
        data.sort_index(inplace=True)
        data.sort_values(['urn_update_open_close'], inplace=True)
        data_len = len(data)
        data.drop_duplicates( subset = urn_name, inplace=True, keep='last' )
        print('Duplicates dropped from updated data: {0}'.format(data_len-len(data)))
        data.drop(columns=['urn_update_open_close'], inplace=True)
    return  data


def find_latlon( df, easting_col_name = None, northing_col_name = None ):
    cols = df.columns.tolist()
    if easting_col_name is None:
        if 'easting' in cols:
            easting_col_name = 'easting'
        elif 'Easting' in cols:
            easting_col_name = 'Easting'
        elif 'bng_e' in cols:
            easting_col_name = 'bng_e'
        else:
            print('No easting column')
            return
    if northing_col_name is None:
        if 'northing' in cols:
            northing_col_name = 'northing'
        elif 'Northing' in cols:
            northing_col_name = 'Northing'
        elif 'bng_n' in cols:
            easting_col_name = 'bng_n'
        else:
            print('No northing column')
            return
    df_coords=pd.DataFrame(df.loc[(df[ easting_col_name ].notnull() & df[ easting_col_name ].notnull())])
    df_no_coords = pd.DataFrame(df.loc[(df[ easting_col_name ].isnull() | df[ easting_col_name ].isnull())])
    easting = df_coords[ easting_col_name ].tolist()
    northing = df_coords[ northing_col_name ].tolist()
    latitude = []
    longitude = []
    for i in range(len(easting)):
        lat_lon = OSGridReference( easting[i], northing[i]).toLatLong()
        latitude.append(lat_lon.latitude)
        longitude.append(lat_lon.longitude)
    df_coords['latitude'] = pd.Series( latitude, index=df_coords.index )
    df_coords['longitude'] = pd.Series( longitude, index=df_coords.index )
    df = pd.concat([df_coords,df_no_coords],sort=True)
    return df


def to_alphanumeric( text ):
#  return sub('/^[a-z\d\-_\s]+$/i',' ',text).strip()
    return sub(' +', ' ', sub(r'[^a-zA-Z0-9 ]',r'', text)).strip()

def to_alphanumeric_plus_punctuation( text ):
    return sub(
        r'[^A-Za-z0-9 !"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]+', '', text
        ).strip()


def email_clean( text ):
    return sub(r'[^a-zA-Z0-9_.@+-]',r'',text).strip()

def field_count( df, field ):
    return df.groupby( field )[ field ].agg('count')


def pivot_neubase_table( df, new_index, pivot_field):
#  print(df.columns.tolist())
#  df_cut=pd.DataFrame(df[ [new_index, 'Year', pivot_field] ])
    df_cut=df[ [new_index, 'Year', pivot_field] ]
#  df_cut.dropna(subset=[pivot_field],inplace=True)
#  print(df_cut.columns.tolist())
    df_pivot=pd.pivot_table(df_cut,[pivot_field],[new_index],['Year'])
    df_pivot.columns = [' '.join(col).strip() for col in df_pivot.columns.values]
    return df_pivot


def pivot_neubase_table2( df, new_index):
    if not type( new_index ) is list:
        new_index = [ new_index ]
    pivot_fields=[ field for field in df.columns if field not in new_index + ['Year'] ]
    pf = []
    for field in pivot_fields:
        try:
            df[field] = df[field].apply(float)
            pf.append(field)
        except:
            print('Skipped: '+field)
    df_pivot=pd.pivot_table(df,pf,new_index,['Year'])
    df_pivot.columns = [' '.join(col).strip() for col in df_pivot.columns.values]
    return df_pivot


def format_worksheet(workbook, worksheet, header, index, dec_list=[], gbp_list=[], int_list=[], percent_list=[], dec_percent_list=[], str_list=[], footer_row = None, footer = [], col_width = 20):
    '''
    index: list of the width of index columns
    dec_list: list of column indices, applies to gbp_list etc.
    '''
    dec_list         = [ i + len(index) for i in dec_list ]
    gbp_list         = [ i + len(index) for i in gbp_list ]
    int_list         = [ i + len(index) for i in int_list ]
    percent_list     = [ i + len(index) for i in percent_list ]
    str_list         = [ i + len(index) for i in str_list ]
    dec_percent_list = [ i + len(index) for i in dec_percent_list ]
    header_format = workbook.add_format()
    header_format.set_text_wrap()
    header_format.set_align('top')
    header_format.set_bold()
    header_format.set_bg_color('#96d3ff')
    header_format.set_align('center')
    header_format.set_border()
    index_format = workbook.add_format()
    index_format.set_align('top')
    index_format.set_align('left')
    index_format.set_bold()
#  index_format.set_align('center')
    index_format.set_border()
    percent_format = workbook.add_format()
    percent_format.set_num_format('0"%"')
    dec_percent_format = workbook.add_format()
    dec_percent_format.set_num_format('0.0"%"')
    gbp_format = workbook.add_format()
    gbp_format.set_num_format('"£"#,##0')
    int_format = workbook.add_format()
    int_format.set_num_format('#,##0')
    dec_format = workbook.add_format()
    dec_format.set_num_format('0.0')
    str_format = workbook.add_format()
#  worksheet.set_row(0,108,header_format)
    for i, width in enumerate(index):
        worksheet.set_column(i,i,width,index_format)
    for i in gbp_list:
        worksheet.set_column(i,i,col_width,gbp_format)
    for i in percent_list:
        worksheet.set_column(i,i,col_width,percent_format)
    for i in dec_percent_list:
        worksheet.set_column(i,i,col_width,dec_percent_format)
    for i in int_list:
        worksheet.set_column(i,i,col_width,int_format)
    for i in dec_list:
        worksheet.set_column(i,i,col_width,dec_format)
    for i in str_list:
        worksheet.set_column(i,i,col_width,str_format)
    for col_num, value in enumerate( header ):
        worksheet.write(0, col_num, value, header_format)
    worksheet.freeze_panes(1, len(index))
    if not(footer_row is None):
        for i,f in enumerate(footer):
            worksheet.write(footer_row+i,0,f)


def excel_out(
        df,
        name,
        dir_name,
        index=False,
        col_format=[],
        col_width=[],
        col_color=None,
        header=None,
        footer=None,
        fit_to_columns=False,
        notes=None,
        wrap_cols=[],
        freeze_cols=None):
    if col_format==[]:
        if index:
            col_format = [ str(df.index.get_level_values(i).dtype) for i in range(len(df.index.names)) ]
        col_format.extend( [ str(d) for d in df.dtypes.tolist() ] )
    if col_width==[]:
        col_width = 20
    if not type( col_width ) is list:
        col_width = [col_width]*len(col_format)
    if len(col_width) < len(col_format):
        col_width.extend([20]*(len(col_format)-len(col_width)))
    if not os.path.exists( dir_name ):
        os.mkdir( dir_name )
    titles = []
    if index:
        titles = list(df.index.names)
        if titles == [None]:
            titles = ['']
    titles.extend(df.columns.tolist())
    if len(titles) < len(col_format):
        titles.extend(['']*(len(col_format)-len(titles)))

    filename = f'{dir_name}/{name}.xlsx'
    filename_writable = False
    loop_count = 0
    while not filename_writable and loop_count < 20:
        try:
            writer = pd.ExcelWriter( filename, engine='xlsxwriter')
            filename_writable = True
        except:
            print( f'{filename} not accessible' )
            filename = f'{filename[:-5]}(1).xlsx'
        loop_count += 1

    df.to_excel(writer, 'Sheet1', index=index, startrow=1, header=False, merge_cells=False )
    workbook = writer.book
    worksheet = writer.sheets[ 'Sheet1' ]
    if not header is None:
        worksheet.set_header( header )
    if not footer is None:
        worksheet.set_footer( footer )
    if fit_to_columns:
        worksheet.fit_to_pages(1, 0)
    if col_color is None:
        col_color = random_color()
    header_format = workbook.add_format()
    header_format.set_text_wrap()
    header_format.set_align('top')
    header_format.set_bold()
    header_format.set_bg_color( col_color )
    header_format.set_align('center')
    header_format.set_border()
    index_format = workbook.add_format()
    index_format.set_align('top')
    index_format.set_align('left')
    index_format.set_bold()
    index_format.set_border()
    index_num_format = workbook.add_format()
    index_num_format.set_bold()
    index_num_format.set_border()
    percent_format = workbook.add_format()
    percent_format.set_num_format('0"%"')
    dec_percent_format = workbook.add_format()
    dec_percent_format.set_num_format('0.0"%"')
    real_percent_format= workbook.add_format()
    real_percent_format.set_num_format('0%')
    real_dec_percent_format = workbook.add_format()
    real_dec_percent_format.set_num_format('0.0%')
    gbp_format = workbook.add_format()
    gbp_format.set_num_format('"£"#,##0')
    gbp_m_format = workbook.add_format()
    gbp_m_format.set_num_format('"£"0.0,,"m";-"£"0.0,,"m"')
    int_format = workbook.add_format()
    int_format.set_num_format('#,##0')
    dec_format = workbook.add_format()
    dec_format.set_num_format('0.0')
    millions_format = workbook.add_format()
    millions_format.set_num_format('0.0,,;-0.0,,')
    str_format = workbook.add_format()
    num_format = str_format
    wrap_format = workbook.add_format()
    wrap_format.set_text_wrap()
    for i, cf in enumerate(col_format):
        if cf[:3].lower() == 'int' or cf == 'int'[:len(cf)]:
            num_format = int_format
        if cf[:5].lower() == 'float':
            num_format = dec_format
        if cf.lower() == 'percent':
            num_format = percent_format
        if cf.lower() == 'dec_percent':
            num_format = dec_percent_format
        if cf.lower() == 'millions':
            num_format = millions_format
        if cf.lower() == 'r_percent':
            num_format = real_percent_format
        if cf.lower() == 'r_dec_percent':
            num_format = real_dec_percent_format
        if cf.lower() == 'gbp':
            num_format = gbp_format
        if cf.lower() == 'millions_gbp':
            num_format = gbp_m_format
        if cf.lower() == 'wrap':
            num_format = wrap_format
        if index and i < len(df.index.names):
            worksheet.set_column(i,i,col_width[i],index_num_format)
        else:
            worksheet.set_column(i,i,col_width[i],num_format)
        worksheet.write(0, i, titles[i], header_format)
    if freeze_cols is None:
        if not index:
            worksheet.freeze_panes(1, 1)
        else:
            worksheet.freeze_panes(1, len(df.index.names))
    else:
        worksheet.freeze_panes(1, freeze_cols )
    if not(notes is None):
        if type(notes) is str:
            worksheet.write( df.shape[0] + 3, 0, notes )
        if type(notes) is list:
            for i, note in enumerate(notes):
                worksheet.write( df.shape[0] + 3 + i, 0, note)
    if wrap_cols != []:
        for col in wrap_cols:
            row_no = 1
            for row in df.iterrows():
                if not pd.isnull( row[1][col] ):
                    worksheet.write(row_no, col, row[1][col], wrap_format)
                row_no += 1
    writer.save()


def sum_columns( df, sum_col_name , cols):
    df[sum_col_name] = 0.0
    df['isnull']=True
    for col in cols:
        df.loc[df[col].notnull(), 'isnull']=False
        df[sum_col_name] += df[col].apply(float).fillna(0)
    df.loc[df['isnull'], sum_col_name ] = np.nan
    df.drop('isnull',axis=1,inplace=True)


def clean_columns( df ):
    for col in df.columns:
        if df[col].dtype=='float':
            df.loc[~np.isfinite(df[col]), col] = np.nan
    index_cols=[]
    if 'year' in df.index.names:
        index_cols=df.index.names
        df.reset_index(inplace=True)
    if 'Year' in df.columns:
        for year in df['Year'].unique():
            for col in df.columns:
                null_col = True
                for v in df[col].loc[df['Year']==year].values:
                    if v != np.nan and v != np.NaN and v != np.NAN:
                        if v != 0.0:
                            null_col = False
                if null_col:
                    df.loc[df['Year']==year, col] = np.nan
    if index_cols != []:
        df.set_index( index_cols, inplace = True)


def download_edubase():
    files_to_delete = os.listdir('data/edubase/daily_downloads')
    for file in files_to_delete:
        os.remove( 'data/edubase/daily_downloads/'+file )
    today = datetime.date.today().strftime('%Y%m%d')
    yesterday = (datetime.date.today() - datetime.timedelta(1)).strftime('%Y%m%d')
    edubase_url = 'http://ea-edubase-api-prod.azurewebsites.net/edubase/edubasealldata'+today+'.csv'
    edubase_url_yesterday = 'http://ea-edubase-api-prod.azurewebsites.net/edubase/edubasealldata'+yesterday+'.csv'
    edubasestate_url = 'http://ea-edubase-api-prod.azurewebsites.net/edubase/edubaseallstatefunded'+today+'.csv'
    edubasestate_url_yesterday = 'http://ea-edubase-api-prod.azurewebsites.net/edubase/edubaseallstatefunded'+yesterday+'.csv'
    try:
        urlopen(edubase_url)
    except:
        edubase_url = edubase_url_yesterday
    filename = 'data/edubase/daily_downloads/' + edubase_url.split('/')[-1]
    r = get(edubase_url, stream=True)
    with open( filename, 'wb') as f:
        f.write(r.content)
    edubase = pd.read_csv( filename, encoding='latin', index_col=0, low_memory=False)
    save_pickles({'edubase':edubase})
    try:
        urlopen(edubasestate_url)
    except:
        edubasestate_url = edubasestate_url_yesterday
    filename = 'data/edubase/daily_downloads/' + edubasestate_url.split('/')[-1]
    r = get(edubasestate_url, stream=True)
    with open( filename, 'wb') as f:
        f.write(r.content)
    edubasestate = pd.read_csv( filename, encoding='latin', index_col=0, low_memory=False)
    save_pickles({'edubasestate':edubasestate})
    links_url = 'http://ea-edubase-api-prod.azurewebsites.net/edubase/links_edubasealldata'+today+'.csv'
    links_url_yesterday = 'http://ea-edubase-api-prod.azurewebsites.net/edubase/links_edubasealldata'+yesterday+'.csv'
    try:
        urlopen(links_url)
    except:
        links_url = links_url_yesterday
    filename = 'data/edubase/' + links_url.split('/')[-1]
    r = get(links_url)
    with open( filename, 'wb') as f:
        f.write(r.content)
    links = pd.read_csv( filename, encoding='latin', usecols=[0,1,3] )
    links=links.loc[ links.LinkType=='Successor' ]
    links.drop( columns=['LinkType'], inplace=True )
    links.drop_duplicates(subset='LinkURN', inplace=True)
    links.drop_duplicates(subset='URN', inplace=True)
    links.rename( columns={'LinkURN':'NEW_URN'}, inplace=True )
    proposed_to_open = edubase.loc[edubase['EstablishmentStatus (name)']=='Proposed to open'].index.tolist()
    links = links[ ~(links['NEW_URN'].isin( proposed_to_open )) ]
    links.set_index('URN', inplace=True)
    save_pickles({'urn_links':links})
    # ballot URN
    links = pd.read_csv( filename, encoding='latin', usecols=[0,1,3] )
    links=links.loc[ links.LinkType=='Successor' ]
    links.drop( columns=['LinkType'], inplace=True )
    links.drop_duplicates(subset='URN', inplace=True)
    links.rename( columns={'LinkURN':'NEW_URN'}, inplace=True )
    proposed_to_open = edubase.loc[edubase['EstablishmentStatus (name)']=='Proposed to open'].index.tolist()
    links = links[ ~(links['NEW_URN'].isin( proposed_to_open )) ]
    links.set_index('URN', inplace=True)
    save_pickles({'urn_links_ballot':links})





#def urn_merge( left_data, right_data, field ):
#  print()
#  left_cols=left_data.columns.tolist()
#  urns_pos = pd.read_csv('input/urns+ve_150917.csv',index_col=0)
#  urns_neg = pd.read_csv('input/urns-ve_150917.csv',index_col=0)
#  dataout = pd.DataFrame()
#  for urns in [[urns_pos,'NEW_URN'],[urns_neg,'OLD_URN']]:
#    left_right = pd.merge(left_data, right_data, how='left', left_index=True, right_index=True)
#    dataout = pd.concat( [dataout, left_right[ left_right[ field ].notnull() ] ] )
#    print(( dataout.shape))
#    left_data = left_right[ left_right[ field ].isnull() ]
#    left_data = left_data[ left_cols ]
#    left_data = pd.merge(left_data,urns[0],how='left',left_index=True, right_index=True)
#    for cycle_count in range(3):
#      if cycle_count > 0:
#        left_right = pd.merge( left_data, right_data, how='left', left_on=urns[1]+str(cycle_count), right_index=True)
#        dataout = pd.concat( [dataout, left_right[ left_right[ field ].notnull() ] ] )
#        print((dataout.shape))
#        left_data = left_right[ left_right[ field ].isnull() ]
#        left_data = left_data[ left_cols ]
#        left_data = pd.merge( left_data, urns[0], how='left',left_on=urns[1]+str(cycle_count), right_index=True)
#      cycle_count += 1
#      left_data = left_data.rename(columns={urns[1]: urns[1]+str(cycle_count) })
#      left_cols.append( urns[1]+str(cycle_count) )
#  dataout = pd.concat( [dataout, left_data])
#  print((dataout.shape))
#  for col in dataout.columns:
#    if 'NEW_URN' in col or 'OLD_URN' in col:
#      dataout = dataout.drop( col, axis = 1 )
#  return dataout
def random_color():
    rand = lambda: np.random.randint(210, 255)
    return '#%02X%02X%02X' % (rand(), rand(), rand())


def word_wrap( text, line_len=63 ):
    words = text.split(' ')
    text_wrapped = ''
    current_line = ''
    for word in words:
        if len(current_line) + len(word) > line_len - 1:
            text_wrapped += '\n' + current_line
            current_line = ''
        current_line += word + ' '
    if len(text_wrapped) > 0:
        return f'{text_wrapped}\n{current_line}'
    return current_line


def update_mem_nums( df, mem_col = 'Membership Number' ):
    mem_no_conv = load_pickle('mem_no_conv')
    df = df.merge( mem_no_conv, how='left', left_on=mem_col, right_on='old_mem_no')
    df.loc[ df.new_mem_no.isnull(), 'new_mem_no' ] = df[ mem_col ]
    df.drop( columns=[ mem_col, 'old_mem_no'], inplace=True )
    df.rename( columns={'new_mem_no':mem_col}, inplace=True )
    return df


def update_mem_no_in_pickles():
    pickles = list_pickles()
    for p in pickles:
        print( '\n' + p )
        df = load_pickle( p )
        if type( df ) == pd.DataFrame:
            for col in df.columns.tolist():
                if col.lower()[:6] == 'member':
                    print( col )
                if col == 'Membership Number':
                    df = update_mem_nums( df, 'Membership Number' )
                    save_pickle( df, p )
                    print( 'UPDATED' )


def log(text, filename = None):
    now = str(datetime.datetime.now())[:19]
    if filename is None:
        filename = f'log_{ now }'
    if not os.path.exists('log'):
        os.mkdir('log')
    text = f'{ now }, { text }\n'
    print(text[:-1])
    log_file = open( f'log/{ filename }', 'a')
    log_file.write( text )
    log_file.close()


if __name__ == '__main__':
    download_edubase()
