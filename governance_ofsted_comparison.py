from pandas import read_excel, ExcelWriter
from edubase import academies

colors = {
    '4 Serious Weaknesses': '#376092',
    '3 Requires Improvement': '#95B3D7',
    '2 Good': '#B9CDE5',
    '1 Outstanding': '#DCE6F2',
    }

output_dir = 'output'

ofsted_original = read_excel(
    'https://assets.publishing.service.gov.uk/government/uploads/system/\
uploads/attachment_data/file/1059521/\
Management_information_-_state-funded_schools_-_as_at_28_Feb_2022.xlsx',
    sheet_name='Most recent inspections',
    skiprows=3,
    index_col='URN',
    parse_dates=[
        'Inspection end date',
        'Previous inspection end date',
        ],
    )
ofsted = ofsted_original[
    [
        'Ofsted phase',
        'URN at time of latest full inspection',
        'URN at time of previous full inspection',
        'Overall effectiveness',
        'Previous full inspection overall effectiveness',
        'School type at time of latest full inspection',
        'School type at time of previous full inspection',
        'Inspection end date',
        'Previous inspection end date',
        ]
    ].dropna().copy()

academies_cut = academies[[
    'URN', 
    'Group UID', 
    'Group Type',
    'Date Joined Group', 
    'Date Left Group',
    'Group Closed Date',
    ]].dropna(subset=['URN']).copy()
ofsted = ofsted.merge(
    academies_cut, 
    how='left', 
    left_on='URN at time of previous full inspection', 
    right_on='URN'
    )
ofsted_dupes = ofsted.loc[
    ofsted['URN at time of previous full inspection'].duplicated(keep=False)
    ]
ofsted_dupes_to_remove = ofsted_dupes.loc[
        (ofsted_dupes['Previous inspection end date'] <
            ofsted_dupes['Date Joined Group']) |
        (ofsted_dupes['Previous inspection end date'] >
            ofsted_dupes['Date Left Group'])
        ].index.tolist() 
ofsted.drop(
    index=ofsted.loc[
        ofsted.index.isin(ofsted_dupes_to_remove)
        ].index, 
    inplace=True
    )
ofsted_dupes = ofsted.loc[
    ofsted['URN at time of previous full inspection'].duplicated(keep=False)
    ]
ofsted_dupes_to_remove = list(set(
    ofsted_dupes.loc[
        ofsted_dupes['Group UID'].duplicated(keep='last')
        ].index.tolist() 
    ))
ofsted.drop(
    index=ofsted.loc[
        ofsted.index.isin(ofsted_dupes_to_remove)
        ].index, 
    inplace=True
    )
ofsted.drop_duplicates(
    subset=['URN at time of previous full inspection'], 
    keep='last', 
    inplace=True
    )
ofsted.rename(columns={
    'Group UID': 'Previous Group UID', 
    'Group Type': 'Previous Group Type',
    },
    inplace=True
    )
ofsted.drop(columns=[
    'Date Joined Group', 
    'Date Left Group',
    'Group Closed Date',
    'URN',
    ],
    inplace=True
    )

ofsted = ofsted.merge(
    academies_cut, 
    how='left', 
    left_on='URN at time of latest full inspection', 
    right_on='URN'
    )
ofsted_dupes = ofsted.loc[
    ofsted['URN at time of latest full inspection'].duplicated(keep=False)
    ]
ofsted_dupes_to_remove = ofsted_dupes.loc[
        (ofsted_dupes['Inspection end date'] <
            ofsted_dupes['Date Joined Group']) |
        (ofsted_dupes['Inspection end date'] >
            ofsted_dupes['Date Left Group'])
        ].index.tolist() 
ofsted.drop(
    index=ofsted.loc[
        ofsted.index.isin(ofsted_dupes_to_remove)
        ].index, 
    inplace=True
    )
ofsted_dupes = ofsted.loc[
    ofsted['URN at time of latest full inspection'].duplicated(keep=False)
    ]
ofsted_dupes_to_remove = list(set(
    ofsted_dupes.loc[
        ofsted_dupes['Group UID'].duplicated(keep='last')
        ].index.tolist() 
    ))
ofsted.drop(
    index=ofsted.loc[
        ofsted.index.isin(ofsted_dupes_to_remove)
        ].index, 
    inplace=True
    )
ofsted.drop_duplicates(
    subset=['URN at time of latest full inspection'], 
    keep='last', 
    inplace=True
    )
ofsted.rename(columns={
    'Group UID': 'Latest Group UID', 
    'Group Type': 'Latest Group Type',
    },
    inplace=True
    )
ofsted.drop(columns=[
    'Date Joined Group', 
    'Date Left Group',
    'Group Closed Date',
    'URN',
    ],
    inplace=True
    )

ofsted_rating_map = {
    1: '1 Outstanding',
    2: '2 Good',
    3: '3 Requires Improvement',
    4: '4 Serious Weaknesses',
    }
ofsted_previous_rating_map = {
    1: '1 Previously Outstanding',
    2: '2 Previously Good',
    3: '3 Previously Requires Improvement',
    4: '4 Previously Serious Weaknesses',
    }
ofsted['Ofsted rating'] = ofsted['Overall effectiveness'].map(
    ofsted_rating_map
    )
ofsted['Previous Ofsted rating'] = (
    ofsted['Previous full inspection overall effectiveness'].map(
        ofsted_previous_rating_map
        )
    )
ofsted_rating_map = {
    1: 'Good or better',
    2: 'Good or better',
    3: 'Less than good',
    4: 'Less than good',
    }
ofsted['Current Ofsted'] = ofsted['Overall effectiveness'].map(
    ofsted_rating_map
    )
ofsted_previous_rating_map = {
    1: 'Previously good or better',
    2: 'Previously good or better',
    3: 'Previously less than good',
    4: 'Previously less than good',
    }
ofsted['Previous Ofsted'] = (
    ofsted['Previous full inspection overall effectiveness'].map(
        ofsted_previous_rating_map
        )
    )

sponsored_academy_list = [
    'Academy Alternative Provision Sponsor Led',
    'Academy Special Sponsor Led',
    'Academy Sponsor Led',
    ]
converter_academy_list = [
    'Academy Alternative Provision Converter',
    'Academy Converter',
    'Academy Special Converter',
    ]
free_school_list = [
    'Free School',
    'Free School - Alternative Provision',
    'Free School Special',
    ]
maintained_school_list = [
    'Community School',
    'Community Special School',
    'Foundation School',
    'Foundation Special School',
    'LA Nursery School',
    'Pupil Referral Unit',
    'Voluntary Aided School',
    'Voluntary Controlled School'
    ]
maintained_2_sat = ofsted.loc[
    (ofsted['Previous Group Type'].isnull()) &
    (ofsted['Latest Group Type']=='Single-academy trust')
    ]
maintained_2_mat = ofsted.loc[
    (ofsted['Previous Group Type'].isnull()) &
    (ofsted['Latest Group Type']=='Multi-academy trust')
    ]
sat_mat_2_mat = ofsted.loc[
    (
        (ofsted['Previous Group Type']=='Single-academy trust') |
        (ofsted['Previous Group Type']=='Multi-academy trust')
        ) &        
    (ofsted['Latest Group Type']=='Multi-academy trust') &
    (ofsted['Previous Group UID']!=ofsted['Latest Group UID'])
    ]
mat_2_mat = ofsted.loc[
    (ofsted['Previous Group Type']=='Multi-academy trust') &
    (ofsted['Latest Group Type']=='Multi-academy trust') &
    (ofsted['Previous Group UID']!=ofsted['Latest Group UID'])
    ]
maintained = ofsted.loc[
    (ofsted['Previous Group Type'].isnull()) &
    (ofsted['Latest Group Type'].isnull())
    ]
sat_nochange = ofsted.loc[
    (ofsted['Latest Group Type']=='Single-academy trust') &
    (ofsted['Previous Group UID']==ofsted['Latest Group UID'])
    ]
mat_nochange = ofsted.loc[
    (ofsted['Latest Group Type']=='Multi-academy trust') &
    (ofsted['Previous Group UID']==ofsted['Latest Group UID'])
    ]
maintained_2_sponsored = ofsted.loc[
    (
        ofsted['School type at time of previous full inspection'].isin(
            maintained_school_list
            )
        ) &
    (   
        ofsted['School type at time of latest full inspection'].isin(
            sponsored_academy_list
            )
        )
    ]
sponsored_both = ofsted.loc[
    (   
        ofsted['School type at time of previous full inspection'].isin(
            sponsored_academy_list
            )
        ) &
    (   
        ofsted['School type at time of latest full inspection'].isin(
            sponsored_academy_list
            )
        )
    ]
maintained_2_converter = ofsted.loc[
    (
        ofsted['School type at time of previous full inspection'].isin(
            maintained_school_list
            )
        ) &
    (   
        ofsted['School type at time of latest full inspection'].isin(
            converter_academy_list
            )
        )
    ]
converter_both = ofsted.loc[
    (   
        ofsted['School type at time of previous full inspection'].isin(
            converter_academy_list 
            )
        ) &
    (   
        ofsted['School type at time of latest full inspection'].isin(
            converter_academy_list 
            )
        )
    ]
free_school_both = ofsted.loc[
    (   
        ofsted['School type at time of latest full inspection'].isin(
            free_school_list
            )
        ) &
    (   
        ofsted['School type at time of previous full inspection'].isin(
            free_school_list
            )
        )    
    ]

ofsted_groups = [
    {
        'filename': 'maintained to sat',
        'data': maintained_2_sat,
        'title': 'that converted to single-academy trusts',
        },
    {
        'filename': 'maintained to mat',
        'data': maintained_2_mat,
        'title': 'that converted to multi-academy trusts',
        },
    {
        'filename': 'sat&mat to new mat',
        'data': sat_mat_2_mat,
        'title': 'in SATs and MATs that moved to a new MAT',
        },
    {
        'filename': 'maintained',
        'data': maintained,
        'title': '',
        },
    {
        'filename': 'single-academy trusts',
        'data': sat_nochange,
        'title': 'with two judgements as single-academy trusts',
        },
    {
        'filename': 'multi-academy trusts',
        'data': mat_nochange,
        'title': 'with two judgements as multi-academy trusts',
        },
    {
        'filename': 'converter academies',
        'data': converter_both,
        'title': 'with two judgements as a converter academy',
        },
    {
        'filename': 'maintained to converter',
        'data': maintained_2_converter,
        'title': 'that became a converter academy',
        },
    {
        'filename': 'sponsor led academies',
        'data': sponsored_both,
        'title': 'with two judgements as a sponsor led academy',
        },
    {
        'filename': 'maintained to sponsor led',
        'data': maintained_2_sponsored,
        'title': 'that were converted to a sponsor led academy',
        },
    {
        'filename': 'free schools',
        'data': free_school_both,
        'title': 'with two judgements as a free school',
        },
    ]

for ofsted_group in ofsted_groups:
    summary = ofsted_group['data'].groupby(
        [
            'Ofsted phase',
            'Ofsted rating',
            'Previous Ofsted rating'
            ]
        ).agg({'Ofsted rating': 'count'}).unstack().fillna(0)
    summary.columns = [col[1] for col in summary.columns]

    short_summary = ofsted_group['data'].groupby(
        [
            'Ofsted phase',
            'Current Ofsted',
            'Previous Ofsted'
            ]
        ).agg({'Ofsted rating': 'count'}).unstack().fillna(0)
    short_summary.columns = [col[1] for col in short_summary.columns]

    for col in short_summary.columns:
        short_summary[col+ ' %'] = (
            short_summary[col] / (
                short_summary.groupby('Ofsted phase')\
                    ['Previously good or better'].transform('sum') + 
                short_summary.groupby('Ofsted phase')\
                    ['Previously less than good'].transform('sum')
                )
            )
    # short_summary.drop(columns=[
    #     'Previously good or better', 'Previously less than good'
    #     ],
    #     inplace=True
    #     )

    for col in summary.columns:
        summary[col+' count'] = summary[col]
        summary[col] = summary[col]/summary.groupby('Ofsted phase')[col]\
            .transform('sum')
    summary['Total'] = 0
    for col in ['1 Previously Outstanding', '2 Previously Good',
           '3 Previously Requires Improvement', '4 Previously Serious Weaknesses']:
        if col in summary.columns:
            summary['Total'] += summary[col+' count']
    summary['Share'] = summary['Total']/summary.groupby('Ofsted phase')\
        ['Total'].transform('sum')

    writer = ExcelWriter(
        f"{output_dir}/{ofsted_group['filename']}.xlsx",
        engine='xlsxwriter'
        )
    workbook = writer.book
    percent_format = workbook.add_format()
    percent_format.set_num_format('0%')
    percent_format.set_align('center')
    percent_format.set_align('vcenter')
    percent_format.set_border()
    percent_format.set_font_size(11)
    header_format = workbook.add_format()
    header_format.set_font_size(12)
    header_format.set_align('top')
    header_format.set_bold()
    header_format.set_align('center')
    header_format.set_text_wrap()
    header_format.set_border()
    int_format = workbook.add_format()
    int_format.set_num_format('#,##0')
    int_format.set_align('center')
    int_format.set_align('vcenter')
    int_format.set_border()
    int_format.set_font_size(11)

    short_summary.to_excel(
        writer,
        'Short summary',
    )
    worksheet = writer.sheets['Short summary']
    worksheet.set_column(0, 1, 15, header_format)
    worksheet.set_column(2, 3, 15, int_format)
    worksheet.set_column(4, 5, 15, percent_format)

    summary.to_excel(
        writer,
        'Summary',
    )
    worksheet = writer.sheets['Summary']
    worksheet.set_column(0, 1, 15, header_format)
    worksheet.set_column(2, 5, 15, percent_format)
    worksheet.set_column(6, 10, 15, int_format)
    worksheet.set_column(11, 11, 15, percent_format)

    phases = {}
    for row_index, row in enumerate(summary.index):
        if row[0] not in phases.keys():
            phases[row[0]] = {'first_row': row_index}
        if row_index == len(summary.index)-1:
            phases[row[0]]['last_row'] = row_index
        elif summary.index[row_index+1][0] != row[0]:
            phases[row[0]]['last_row'] = row_index
    for phase in phases:
        if phase not in ['Primary', 'Secondary', 'Special']: continue
        chartsheet = workbook.add_chartsheet(f'{phase} chart')
        chart = workbook.add_chart(
            {
                'type': 'column',
                'subtype': 'stacked'
                }
            )
        chartsheet.set_chart(chart)
        for row in range(
                phases[phase]['last_row'],
                phases[phase]['first_row']-1,
                -1
                ):
            if summary.index[row][1] != '4 Serious Weaknesses':
                label_color = 'black'
            else:
                label_color = 'white'
            chart.add_series(
                {
                    'name': summary.index[row][1],
                    'categories': ['Summary', 0, 2, 0, 5],
                    'values': ['Summary', row+1, 2, row+1, 5],
                    'fill':   {'color': colors[summary.index[row][1]]},
                    'gap': 150,
                    'data_labels': {
                        'value': True,
                        'font': {'color': label_color, 'size': 11},
                        },
                    }
                )
            if ofsted_group['title'] == '':
                title = f"""Ofsted judgements of maintained {phase.lower()} \
schools
with two judgements"""
            else:
                title = f"""Ofsted judgements of {phase.lower()} schools
{ofsted_group['title']}"""
            chart.set_title(
                {
                    'name': title,
                    'name_font': {'size': 18},
                }
            )
            chart.set_y_axis(
                {
                    'num_font': {'size': 12},
                    'max' : 1,
                }
            )
            chart.set_x_axis(
                {
                    'num_font': {'size': 12},
                }
            )
            chart.set_legend(
                {
                    'position': 'right',
                    'font': {'size': 12},
                }
            )
    ofsted_original.loc[
        ofsted_original['URN at time of latest full inspection'].isin(
            ofsted_group['data']['URN at time of latest full inspection']
            )
        ].to_excel(
            writer,
            'Data',
            index=False,
            )
    writer.close()