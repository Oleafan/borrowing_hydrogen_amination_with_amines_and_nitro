""" Functions for data plotting"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as pltt
from matplotlib import cm
from matplotlib import rc
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as mcolors
import numpy as np
import warnings
warnings.simplefilter('ignore')

#for export of consolidaed data to docx 
from docx import Document
from docx.shared import Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_UNDERLINE
from docx.enum.text import WD_COLOR_INDEX
from docx.enum.section import WD_ORIENT

import json
from rdkit import Chem
from rdkit.Chem import Draw
from tqdm import tqdm


#colormap based on YlGnBu:
colors = [
    (1, 1, 1),           # white
    (0.96862745, 0.98823529, 0.74117647),  
    (0.78039216, 0.91372549, 0.70588235),
    (0.49803922, 0.80392157, 0.73333333),
    (0.25490196, 0.71372549, 0.76862745),
    (0.11372549, 0.56862745, 0.75294118),
    (0.13333333, 0.36862745, 0.65882353),
    (0.14509804, 0.20392157, 0.58039216),  
]

# Создаем цветовую карту
cmap_custom = LinearSegmentedColormap.from_list('custom_YlGnBu', colors, N=256)

def to_chem (s):
    #Returns Latex formatted data to adequately displa chemical formulas like K2CO3
    s_t="$\ "
    check=0
    for i in s:
        try:
            a=int(i)
            a="_{"+str(i)+"}"
            s_t=s_t+a
            check=check+1
        except ValueError:
            a=i
            if i == ' ':
                a='\:'
            s_t=s_t+a
            continue
    s_t=s_t+"$ "
    return s_t

def prepare_crtab(data, cr_tab1, cr_tab2, sort_vertical = True, sort_horizontal = True, filter_val = 0):
    data_crtab=pd.crosstab(data[cr_tab1],data[cr_tab2]) 
    
    if sort_vertical:
        data_crtab['max']=data_crtab[data_crtab.columns].sum(axis=1)
        data_crtab.sort_values(by='max', ascending = False, inplace=True)
        data_crtab=data_crtab[data_crtab['max']>filter_val]
        data_crtab.drop('max', axis=1,inplace=True)
    if sort_horizontal:
        data_crtab = data_crtab.T
        data_crtab['max']=data_crtab[data_crtab.columns].sum(axis=1)
        data_crtab.sort_values(by='max', ascending = False, inplace=True)
        data_crtab=data_crtab[data_crtab['max']>filter_val]
        data_crtab.drop('max', axis=1,inplace=True)      
        data_crtab = data_crtab.T
    return data_crtab


def d3_diagram (data, cr_tab1, cr_tab2, title, 
                sort_vertical = True, 
                c_mp = 'Number of hits', 
                normalize = False, 
                tochem_x=True, 
                tochem_y=True, 
                
                figsize=(15,5), 
                filter_val=0,
                rotation_x_ticks='vertical', 
                title_font=25,
                xlabel_font = 20,
                x_ticks = None , 
                y_ticks = None,
                man_x_label=False,
                x_label='', 
                sort_horizontal = False,
                rename_x_ticks_dict = None
               ):
    """This function get a dataframe (data), which was filtered to display only desired data.It makes a crosstab using a  
    cr_tab1, cr_tab2 as names for the columns. cr_tab1 becomes y, cr_tab2 -  х. Then it plots a 2d histogram """
    data_crtab=prepare_crtab(data, cr_tab1, cr_tab2, sort_vertical = sort_vertical, sort_horizontal = sort_horizontal, filter_val = filter_val)
    
    if normalize:
        data_crtab=round((data_crtab.T/data_crtab.T.max()).T,2)
        c_mp=c_mp+', fraction'
        title=title+ ', normalized'
    
    y_ticks_l = data_crtab.index.values
    if y_ticks:
        y_ticks_l = y_ticks
    if tochem_y:
        y_ticks_l=[ to_chem(i) for i in y_ticks_l ]
    x_ticks_l=data_crtab.columns.values

    if x_ticks:
        x_ticks_l = x_ticks

    if rename_x_ticks_dict:
        x_ticks_l = [rename_x_ticks_dict[x] for x in x_ticks_l]
    if tochem_x:
        x_ticks_l=[ to_chem(i) for i in x_ticks_l]
    
    xlabel=cr_tab2
    if man_x_label:
        xlabel=x_label
 
    fig = plt.figure(figsize=figsize)
    
    ax=sns.heatmap(data_crtab.values, xticklabels=x_ticks_l, yticklabels=y_ticks_l,
              cbar_kws={'label': c_mp}, cmap=cmap_custom, annot =True, fmt="d")
    
    ax.set_xlabel(xlabel, fontsize = xlabel_font)
    ax.set_title(title, fontsize = title_font)
    plt.xticks(fontsize=13, rotation=rotation_x_ticks)
    plt.yticks(fontsize=13, rotation = 0)

def plot_diff_graph(
    data, 
    crtab_1, 
    crtab_2,
    filter_val = 0,
    figsize = (17, 8),
    xlabel = None,
    title = None,
    rename_x_ticks_dict = None,
    debug = False,
    sort_vertical = True, 
    sort_horizontal = True
                   ):

    data_crtab_full = prepare_crtab(data, crtab_1, crtab_2, filter_val = filter_val, sort_vertical =sort_vertical ,  sort_horizontal = sort_horizontal )
    data_crtab_diff = prepare_crtab(data[data['year'] >= 2022], crtab_1, crtab_2, filter_val = filter_val )
    
    data_crtab_diff_1 = pd.DataFrame(columns = data_crtab_full.columns, index = data_crtab_full.index)
    for col in data_crtab_diff_1.columns:
        if col in data_crtab_diff.columns:
            data_crtab_diff_1[col] = data_crtab_diff[col]
    
    y_ticks_l = data_crtab_full.index.values
    y_ticks_l=[ to_chem(i) for i in y_ticks_l ]
    x_ticks_l=data_crtab_full.columns.values
    if debug:
        return data_crtab_full, data_crtab_diff, data_crtab_diff_1

    data_crtab_diff_1.fillna(0, inplace = True)
    plt.figure(figsize=figsize)
    plt.subplot(2, 1, 1)
    ax =sns.heatmap(data_crtab_full.apply(pd.to_numeric, errors='coerce').values, xticklabels=[], yticklabels=y_ticks_l,
              cbar_kws={'label': 'number of hits'}, cmap=cmap_custom , annot =True, fmt=".0f")
    
    ax.set_title(title, fontsize = 15)
    ax.set_ylabel('Whole data', fontsize = 13)
    plt.yticks(fontsize=13, rotation=0)

    if rename_x_ticks_dict:
        x_ticks_l = [rename_x_ticks_dict[x] for x in x_ticks_l]
    
    plt.subplot(2, 1, 2)
    ax =sns.heatmap(data_crtab_diff_1.fillna(0).apply(pd.to_numeric, errors='coerce').values, xticklabels=x_ticks_l, yticklabels=y_ticks_l,
              cbar_kws={'label': 'number of hits'}, cmap=cmap_custom , annot =True, fmt=".0f")
    
    ax.set_xlabel(xlabel, fontsize = 13)
    # ax.set_title('Data on catalytic activity since 2022', fontsize = 15)
    ax.set_ylabel('Data since 2022', fontsize = 13)
    plt.xticks(fontsize=13, rotation=45)
    plt.yticks(fontsize=13, rotation=0)
    plt.tight_layout()


def get_parameter_pie_df(df, parameter, limit_items = 5):
    item_freqs = pd.DataFrame(df[parameter].value_counts())
    first_item = item_freqs.index.to_list()[0]
    border_item = item_freqs[:limit_items].index.to_list()[-1]
    last_item = item_freqs.index.to_list()[-1]
    others=(item_freqs['count'].loc[border_item:last_item]).sum()   
    pie_df=pd.DataFrame(item_freqs['count'].loc[first_item:border_item])
    items=list(pie_df.index)
    items.append('other')
    pie_df = pd.concat([pie_df, pd.DataFrame({'count': {parameter: others}})])
    pie_df.index = items 
    return pie_df, item_freqs.index.to_list()[limit_items:] #return dataframe adopted for base pie and list of items included to others 
    
def compare_pie(
    df, 
    parameter, 
    titles, #list of lenghth 2
    limit_items = 5, 
    font_size_labels = 9,
    fontsize_title = 12
):
    plt.figure(figsize=(10,5))
    values = np.linspace(0.2, 1, limit_items+1)
    colors = cm.rainbow(values)
    
    df1, other = get_parameter_pie_df(df[df['metal'].isna()], parameter, limit_items)
    ax = plt.subplot(1, 2, 1) 
    ax.pie(df1['count'], labels=df1.index, autopct='%1.1f%%', textprops={'fontsize': font_size_labels}, colors=colors)
    ax.axis('equal')
    ax.set_title(titles[0], fontsize = fontsize_title);    
    # plt.suptitle(', '.join(other_bases), y=0.02)

    df1, other = get_parameter_pie_df(df[~df['metal'].isna()], parameter, limit_items)
    ax = plt.subplot(1, 2, 2) 
    ax.pie(df1['count'], labels=df1.index, autopct='%1.1f%%', textprops={'fontsize': font_size_labels}, colors=colors)
    ax.axis('equal')
    ax.set_title(titles[1], fontsize = fontsize_title);    
    # plt.suptitle(', '.join(other_bases), y=0.02)    

def get_cat_leaders(df):
    metals = list(set(df['metal'].to_list()))
    metals = [x for x in metals if (x != '0' and x == x)]
    metal_leaders = []
    for metal in metals:
        metal_df = df[df['metal'] == metal]
        metal_df.dropna(subset = 'TON', inplace = True)
        metal_df = metal_df[metal_df['TON']<100000000000]

        record = {'metal': metal}
        record['num_papers'] =  len(set(metal_df['doi'].to_list()))
        # max ton maximal TON among all (TONmax(1)/T,°C/base/catalyst typea/atmosphere)
        best = metal_df.sort_values(by = 'TON', ascending = False).to_dict('records')
        if len(best):
            best = best[0]
            if 'year' not in best:
                best['year'] = 'unknown'
            ton = best['TON']
            if ton==ton:
                res = round(best['TON'])
            else:
                res = 'no data on TON'
            record['max_ton'] = f'({res}/{best['temp']}°C/{best['base']}/{best['catalyst']}/{best['atm_type']}/{best['doi']}/{best['year']})'
        else:
            record['max_ton'] = 'no data'
        # maximal TON among the processes with preparative yields (TONmax(2)/T,°C/base/catalyst typea/atmosphere)
        best = metal_df[metal_df['yield']>65].sort_values(by = 'TON', ascending = False).to_dict('records')
        if len(best):
            best = best[0]
            if 'year' not in best:
                best['year'] = 'unknown'
            ton = best['TON']
            if ton==ton:
                res = round(best['TON'])
            else:
                res = 'no data on TON'
            record['max_ton_prep'] = f'({res}/{best['temp']}°C/{best['base']}/{best['catalyst']}/{best['atm_type']}/{best['doi']}/{best['year']})'
        else:
            record['max_ton_prep'] = 'no data'
        #the lowest temperature in the presence of base (TON/Tmin(1),°C/base/catalyst typea/atmosphere)
        best = metal_df[metal_df['yield']>65].sort_values(by = 'temp').to_dict('records')
        if len(best):
            best = best[0]
            if 'year' not in best:
                best['year'] = 'unknown'
            ton = best['TON']
            if ton==ton:
                res = round(best['TON'])
            else:
                res = 'no data on TON'
            record['min_temp'] = f'({res}/{best['temp']}°C/{best['base']}/{best['catalyst']}/{best['atm_type']}/{best['doi']}/{best['year']})'
        else:
            record['min_temp'] = 'no data'
        #the highest TON in the absence of base (TONmax(3)/T,°C/base/catalyst typea/atmosphere)
        best = metal_df[metal_df['base']=='no base'].sort_values(by = 'TON', ascending = False).to_dict('records')
        if len(best):
            best = best[0]  
            if 'year' not in best:
                best['year'] = 'unknown'
            ton = best['TON']
            if ton==ton:
                res = round(best['TON'])
            else:
                res = 'no data on TON'
            record['max_ton_no_base'] = f'({res}/{best['temp']}°C/{best['base']}/{best['catalyst']}/{best['atm_type']}/{best['doi']}/{best['year']})'
        else:
            record['max_ton_no_base'] = 'no data'
            
        #The lowest temperature in the absence of base (TON/Tmin(2),°C/base/catalyst typea/atmosphere)
        best = metal_df.loc[metal_df['base']=='no base'].loc[metal_df['yield']>65].sort_values(by = 'temp').to_dict('records')
        if len(best):
            best = best[0]
            if 'year' not in best:
                best['year'] = 'unknown'
            ton = best['TON']
            if ton==ton:
                res = round(best['TON'])
            else:
                res = 'no data on TON'
            record['min_temp_no_base'] = f'({res}/{best['temp']}°C/{best['base']}/{best['catalyst']}/{best['atm_type']}/{best['doi']}/{best['year']})'
        else:
            record['min_temp_no_base'] = 'no data'
        bases = metal_df[metal_df['yield']>65]['base'].value_counts().index.to_list()
        if len(bases) > 1:
            record['most_popular_working_bases']= bases[0:3]
        else:
            record['most_popular_working_bases']= bases
        metal_leaders.append(record)
    metal_leaders = sorted(metal_leaders, key = lambda x: x['num_papers'], reverse = True)
    metal_leaders = [x for x in metal_leaders if x['num_papers'] > 0]
    return metal_leaders

def create_document(data, title):
    document = Document()
            
    sections = document.sections
    for section in sections:
        section.orientation = WD_ORIENT.LANDSCAPE
    
    p = document.add_paragraph() 
    run = p.add_run(title)
    run.font.size = Pt(14)
    paragraph_format = p.paragraph_format
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = document.add_paragraph('Data stracture in all cells: (TONmax/T,°C/base/catalyst/atmosphere/doi/year/comment)') 
    
    col_names = ['Metal', 'Number of papers', 
                'Maximal TON among all ', 
                 'Maximal TON among the processes with preparative yields >65%',
                    'The lowest temperature among all with preparative yields >65%',
                 'The highest TON in the absence of base',
                 'The lowest temperature in the absence of base with preparative yields >65%', 
                'most popular working bases']
    table = document.add_table(rows= len(data) +1 , cols=len(col_names))
    row = table.rows[0]
    for idx, col_name in enumerate(col_names):
        
        for p in row.cells[idx].iter_inner_content():
            break
        run = p.add_run(col_name)
        run.bold = True
        
    for row_idx, item in enumerate(data):
        row = table.rows[row_idx+1] #так как нулевой ряд - заголовок
        row.cells[0].text = item['metal']
        row.cells[1].text = str(item['num_papers'])
        row.cells[2].text = str(item['max_ton'])
        row.cells[3].text = str(item['max_ton_prep'])
        row.cells[4].text = str(item['min_temp'])
        row.cells[5].text = str(item['max_ton_no_base'])
        row.cells[6].text = str(item['min_temp_no_base'])
        row.cells[7].text = str(item['most_popular_working_bases'])
        
    return document


solvent_diel_const = """PhMe	2.4
dioxane	2.3
p-xylene	2.3
THF	7.5
diglyme	7.3
H2O	78.2
mesitylene	2.4
MeCN	36.0
trifluoroethanol	26.7
DMF	37.1
hexane	1.9
o-xylene	2.6
DMSO	46.7
DCM	9.0
octane	2.0
tAmOH	15.8
PhCF3	9.1
DME	7.2
anisole	4.5
DCE	10.7
CyH	2.0
benzene	2.4
PhCl	5.7
EtOH	24.5
m-xylene	2.4
xylene	2.4
MeOH	33.6
DMA	38.3
EtOAc	6.0
dichlorobenzene	10.4
PhF	5.6
NMP	32.2
iPrOH	18.2
tBuOH	9.3
heptane	1.4
Et2O	4.4
CHCl3	4.9
pyridine	13.2
ethylene diamine	16.0
Et3N	2.5
cymene	2.3
PhtBu	6.4
PhNO2	36.1
morpholine	7.7
nBuOH	17.8
ethylene glycol	37
AcOH	6.2
MeOtBu	4.5
propylene carbonate	62.9
MeNO2	36.2
BuOAc	5.0
HFIP	16.7
AmOH	15.8"""
solvent_diel_const = {x.split('\t')[0]:float(x.split('\t')[1]) for x in solvent_diel_const.split('\n')}