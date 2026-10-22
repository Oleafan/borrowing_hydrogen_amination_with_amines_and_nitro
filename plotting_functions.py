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
import os
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

# borders between heatmap cells (reviewer: cells should be clearly separated, like in a table)
GRID_COLOR = '#7a7a7a'
GRID_LW = 0.6


def _annot_labels(values, fmt='{:.0f}', hide_zeros=True):
    """Text labels for heatmap cells; zero (and NaN) cells get no label if hide_zeros."""
    values = np.asarray(values, dtype=float)
    labels = np.empty(values.shape, dtype=object)
    for idx, v in np.ndenumerate(values):
        labels[idx] = '' if (hide_zeros and (v == 0 or np.isnan(v))) else fmt.format(v)
    return labels


def _frame(ax, color=GRID_COLOR, lw=GRID_LW):
    """Outer frame of a heatmap drawn with the axes spines (seaborn's cell edges
    at the bottom and right borders are clipped by the axes)."""
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(color)
        spine.set_linewidth(lw)
        spine.set_zorder(6)

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
        # data_crtab=data_crtab[data_crtab['max']>filter_val]
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
                rename_x_ticks_dict = None,
                grid_color = GRID_COLOR,
                grid_lw = GRID_LW,
                hide_zeros = True
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
    
    annot_fmt = '{:g}' if normalize else '{:.0f}'
    ax=sns.heatmap(data_crtab.values, xticklabels=x_ticks_l, yticklabels=y_ticks_l,
              cbar_kws={'label': c_mp}, cmap=cmap_custom,
              annot=_annot_labels(data_crtab.values, annot_fmt, hide_zeros), fmt="",
              linewidths=grid_lw, linecolor=grid_color)
    if grid_lw:
        _frame(ax, grid_color, grid_lw)
    
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
    title_font = 15,
    ylabel_font = 13,
    rename_x_ticks_dict = None,
    debug = False,
    sort_vertical = True, 
    sort_horizontal = True,
    grid_color = GRID_COLOR,
    grid_lw = GRID_LW,
    hide_zeros = True
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
    full_values = data_crtab_full.apply(pd.to_numeric, errors='coerce').values
    diff_values = data_crtab_diff_1.fillna(0).apply(pd.to_numeric, errors='coerce').values
    if rename_x_ticks_dict:
        x_ticks_l = [rename_x_ticks_dict[x] for x in x_ticks_l]

    # one common color scale for 'whole data' and 'data since 2022' and one colorbar
    vmax = np.nanmax([np.nanmax(full_values), np.nanmax(diff_values)]) if full_values.size else 1
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 0.015], wspace=0.03)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    cax = fig.add_subplot(gs[:, 1])

    sns.heatmap(full_values, ax=ax1, xticklabels=[], yticklabels=y_ticks_l,
                cmap=cmap_custom, vmin=0, vmax=vmax, cbar=False,
                annot=_annot_labels(full_values, hide_zeros=hide_zeros), fmt="",
                linewidths=grid_lw, linecolor=grid_color)
    if grid_lw:
        _frame(ax1, grid_color, grid_lw)
    ax1.set_title(title, fontsize = title_font)
    ax1.set_ylabel('Whole data', fontsize = ylabel_font)
    ax1.tick_params(axis='y', labelsize=10, rotation=0)

    sns.heatmap(diff_values, ax=ax2, xticklabels=x_ticks_l, yticklabels=y_ticks_l,
                cmap=cmap_custom, vmin=0, vmax=vmax, cbar=True, cbar_ax=cax,
                cbar_kws={'label': 'number of hits'},
                annot=_annot_labels(diff_values, hide_zeros=hide_zeros), fmt="",
                linewidths=grid_lw, linecolor=grid_color)
    if grid_lw:
        _frame(ax2, grid_color, grid_lw)
    ax2.set_xlabel(xlabel, fontsize = ylabel_font)
    ax2.set_ylabel('Data since 2022', fontsize = ylabel_font)
    ax2.tick_params(axis='y', labelsize=10, rotation=0)
    plt.setp(ax2.get_xticklabels(), fontsize=10, rotation=45)
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
    fontsize_title = 12,
    orientation = 'horizontal', 
    startangle=0
):
    if orientation == 'horizontal':
        plt.figure(figsize=(8.5,4.5))
    elif  orientation == 'vertical':
        plt.figure(figsize=(4,7))        
    values = np.linspace(0.2, 1, limit_items+1)
    colors = cm.rainbow(values)
    
    df1, other = get_parameter_pie_df(df[df['metal'].isna()], parameter, limit_items)
    if orientation == 'horizontal':
        ax = plt.subplot(1, 2, 1) 
    elif  orientation == 'vertical':
        ax = plt.subplot(2, 1, 1) 
    ax.pie(df1['count'], labels=[to_chem(x) for x in df1.index], autopct='%1.1f%%', textprops={'fontsize': font_size_labels}, colors=colors, startangle=startangle)
    ax.axis('equal')
    ax.set_title(titles[0], fontsize = fontsize_title);    
    # plt.suptitle(', '.join(other_bases), y=0.02)

    df1, other = get_parameter_pie_df(df[~df['metal'].isna()], parameter, limit_items)
    if orientation == 'horizontal':
        ax = plt.subplot(1, 2, 2) 
    elif  orientation == 'vertical':
        ax = plt.subplot(2, 1, 2) 
    ax.pie(df1['count'], labels=[to_chem(x) for x in df1.index], autopct='%1.1f%%', textprops={'fontsize': font_size_labels}, colors=colors, startangle=startangle)
    ax.axis('equal')
    ax.set_title(titles[1], fontsize = fontsize_title);    
    plt.tight_layout()
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

def _crosstab_whole_and_new(data, y, x, filter_val, year_split=2022):
    """Crosstab y x x for the whole data and for data since year_split (same rows/columns).
    Rows (y values) appeared not more than filter_val times in the whole data are neglected."""
    full = pd.crosstab(data[y], data[x])
    full = full.loc[full.sum(axis=1).sort_values(ascending=False, kind='stable').index]
    full = full[full.sum(axis=1) > filter_val]
    new_data = data[data['year'] >= year_split]
    new = pd.crosstab(new_data[y], new_data[x])
    new = new.reindex(index=full.index, columns=full.columns, fill_value=0)
    return full, new


def _draw_cell_grid(ax, n_rows, n_cols, color, lw):
    """Borders around every cell, including empty (masked) ones.
    Inner borders are lines; the outer frame is the axes frame (spines), which is never clipped."""
    if n_rows > 1:
        ax.hlines(np.arange(1, n_rows), 0, n_cols, colors=color, linewidth=lw, zorder=5)
    if n_cols > 1:
        ax.vlines(np.arange(1, n_cols), 0, n_rows, colors=color, linewidth=lw, zorder=5)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(color)
        spine.set_linewidth(lw)
        spine.set_zorder(6)


def plot_heatmap_grid(
    panels,
    y='base',
    fig_width=7.0,
    layout='side',
    cell_h=None,
    cbar_label='Number of successful reactions',
    col_titles=('Whole data', 'Data since 2022'),
    year_split=2022,
    temp_step=10,
    annot_fontsize=6.5,
    tick_fontsize=7,
    panel_label_fontsize=9,
    xlabel_fontsize=8,
    grid_color=GRID_COLOR,
    grid_lw=0.5,
    figsize=None,   # ignored: the figure size is calculated from fig_width and cell_h
    panel_w=None,   # ignored (old parameter)
):
    """Several 'whole data / data since 2022' heatmaps combined in one figure.

    The figure is built in its final (print) size: fig_width is the width in inches
    (about 7 in for a full page width, 3.3 in for one column), font sizes are real points.
    Save it with fig.savefig(..., dpi=600, bbox_inches='tight') and insert at 100% width.

    layout = 'side'    - 'whole data' and 'data since 2022' side by side;
             'stacked' - 'data since 2022' below 'whole data', every block uses the full width.
    One common color scale and one colorbar for all heatmaps, empty cells instead of zeros,
    short panel labels (e.g. 'a) Ni'), borders around all cells. All blocks have the same width;
    the cell width is the block width / number of columns, the cell height is fixed (cell_h, inches).

    panels: list of dicts with keys
        'data'       - dataframe with successful reactions only (must contain y, x and 'year'),
        'x'          - column for the x axis, e.g. 'num_temp_range' or 'metal',
        'label'      - short panel label, e.g. 'a) Ni',
        'filter_val' - rows (y values) appeared not more than filter_val times are neglected (default 0),
        'x_label'    - optional x-axis title (default: 'Temperature range, °C' for 'num_temp_range',
                       otherwise the column name capitalized).
    If all panels use the same x column, the same set of columns is used in all panels and
    the x tick labels are shown only under the last block.
    """
    tables = [_crosstab_whole_and_new(p['data'], y, p['x'], p.get('filter_val', 0), year_split)
              for p in panels]
    is_temp = [p['x'] == 'num_temp_range' for p in panels]
    shared_x = len(set(p['x'] for p in panels)) == 1

    def x_values(full_tables, temp):
        cols = set().union(*[set(f.columns) for f in full_tables])
        if temp:
            return list(range(min(cols), max(cols) + 1))
        return sorted(cols, key=lambda m: (m == 'no metal', str(m)))

    if shared_x:
        common = x_values([full for full, _ in tables], is_temp[0])
        columns = [common] * len(panels)
    else:
        columns = [x_values([full], temp) for (full, _), temp in zip(tables, is_temp)]

    def x_tick_labels(cols, temp):
        if temp:
            return [f'[{b*temp_step},{(b+1)*temp_step})' for b in cols]
        return [str(c) for c in cols]

    vmax = max(full.values.max() for full, _ in tables)  # one color scale for everything

    # ---- layout in inches (final print size) ----
    pt = 1 / 72
    if cell_h is None:
        cell_h = annot_fontsize * 1.9 * pt
    max_ylab = max(len(str(b)) for full, _ in tables for b in full.index)
    max_panel_lab = max(len(p['label']) for p in panels)
    left = (max_panel_lab * panel_label_fontsize * 0.62 + max_ylab * tick_fontsize * 0.5 + 10) * pt
    cbar_space = 0.62
    col_gap = 0.10
    title_h = (xlabel_fontsize + 5) * pt
    max_xlab = max(len(l) for cols, temp in zip(columns, is_temp) for l in x_tick_labels(cols, temp))
    xlab_space = (max_xlab * tick_fontsize * 0.55 * 0.72 + xlabel_fontsize + 16) * pt
    gap_small = 0.07

    if layout == 'side':
        block_w = (fig_width - left - col_gap - cbar_space) / 2
    elif layout == 'stacked':
        block_w = fig_width - left - cbar_space
    else:
        raise ValueError("layout must be 'side' or 'stacked'")

    # numbers must fit into the narrowest cells: reduce the font if needed (one font for the whole figure)
    max_digits = max(len(str(int(t.values.max()))) for pair in tables for t in pair if t.size)
    min_cell_w = block_w / max(len(c) for c in columns) / pt          # in points
    annot_fontsize = min(annot_fontsize, (min_cell_w - 1.5) / (max_digits * 0.6))

    # blocks: (panel index, 0 = whole / 1 = since 2022, x0, height, title, show x tick labels, gap below)
    blocks = []
    n = len(panels)
    for r in range(n):
        h = max(len(tables[r][0]), 1) * cell_h
        last = r == n - 1
        show_x = (not shared_x) or last
        gap_after = xlab_space if show_x else gap_small
        if layout == 'side':
            for c in (0, 1):
                blocks.append(dict(r=r, c=c, x0=left + c * (block_w + col_gap), h=h, row=r,
                                   title=col_titles[c] if r == 0 else None, show_x=show_x, gap=gap_after))
        else:
            blocks.append(dict(r=r, c=0, x0=left, h=h, row=2 * r, title=col_titles[0],
                               show_x=False, gap=gap_small))
            blocks.append(dict(r=r, c=1, x0=left, h=h, row=2 * r + 1, title=col_titles[1],
                               show_x=show_x, gap=gap_after))

    # vertical positions (rows of blocks)
    rows = sorted(set(b['row'] for b in blocks))
    row_h = {b['row']: b['h'] for b in blocks}
    row_gap = {b['row']: b['gap'] for b in blocks}
    row_title = {b['row']: any(bb['title'] for bb in blocks if bb['row'] == b['row']) for b in blocks}
    y = 0.05
    row_top = {}
    for rr in rows:
        y += title_h if row_title[rr] else 0
        row_top[rr] = y
        y += row_h[rr] + row_gap[rr]
    fig_h = y
    fig = plt.figure(figsize=(fig_width, fig_h))

    axes = np.empty((n, 2), dtype=object)
    for b in blocks:
        r, c = b['r'], b['c']
        panel, cols, temp = panels[r], columns[r], is_temp[r]
        top = row_top[b['row']]
        ax = fig.add_axes([b['x0'] / fig_width, 1 - (top + b['h']) / fig_h, block_w / fig_width, b['h'] / fig_h])
        axes[r, c] = ax
        table = tables[r][c].reindex(columns=cols, fill_value=0)
        sns.heatmap(table, ax=ax, mask=(table == 0), cmap=cmap_custom, vmin=0, vmax=vmax,
                    annot=True, fmt='d', annot_kws={'fontsize': annot_fontsize}, cbar=False)
        _draw_cell_grid(ax, table.shape[0], table.shape[1], grid_color, grid_lw)
        ax.set_facecolor('white')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.tick_params(length=0, pad=2)
        if b['x0'] == left:   # left column of blocks: base names and panel label
            ax.set_yticks(np.arange(table.shape[0]) + 0.5)
            ax.set_yticklabels([to_chem(v) for v in table.index], rotation=0, fontsize=tick_fontsize)
            if c == 0:
                ax.set_ylabel(panel['label'], rotation=0, ha='right', va='center',
                              fontsize=panel_label_fontsize, fontweight='bold', labelpad=4)
        else:
            ax.set_yticks([])
        if b['title']:
            ax.set_title(b['title'], fontsize=xlabel_fontsize, pad=3,
                         loc='center' if layout == 'side' else 'left')
        if b['show_x']:
            ax.set_xticks(np.arange(len(cols)) + 0.5)
            ax.set_xticklabels(x_tick_labels(cols, temp), rotation=45, ha='right',
                               rotation_mode='anchor', fontsize=tick_fontsize)
            default_label = 'Temperature range, °C' if temp else panel['x'].capitalize()
            ax.set_xlabel(panel.get('x_label', default_label), fontsize=xlabel_fontsize, labelpad=2)
        else:
            ax.set_xticks([])

    # one common colorbar, vertically centered on the heatmaps
    first_top = row_top[rows[0]]
    last_bottom = row_top[rows[-1]] + row_h[rows[-1]]
    cb_h = min(2.2, last_bottom - first_top)
    cb_top = (first_top + last_bottom - cb_h) / 2
    cb_x = left + (2 * block_w + col_gap if layout == 'side' else block_w) + 0.12
    cax = fig.add_axes([cb_x / fig_width, 1 - (cb_top + cb_h) / fig_h, 0.09 / fig_width, cb_h / fig_h])
    sm = plt.cm.ScalarMappable(cmap=cmap_custom, norm=plt.Normalize(vmin=0, vmax=vmax))
    cbar = fig.colorbar(sm, cax=cax)
    cbar.set_label(cbar_label, fontsize=xlabel_fontsize - 0.5)
    cbar.ax.tick_params(labelsize=tick_fontsize - 0.5, length=2)
    cbar.outline.set_linewidth(grid_lw)
    return fig, axes


# ---------------------------------------------------------------------------
# saving figures for the manuscript
FIGURES_DIR = 'figures'


def save_fig(name, fig=None, folder=FIGURES_DIR, dpi=600, fmt='png', axes=None):
    """Save a figure in high resolution to folder/name.fmt (folder is created if needed).

    name  - file name without extension, e.g. 'Figure 12' or 'Figure 21a' (as in the manuscript)
    fig   - figure to save (default: the current figure)
    axes  - optional list of axes: only the area of these axes (with their labels) is saved,
            e.g. one panel of a multi-panel figure
    Call it before plt.show() (after plt.show() the current figure is a new empty one).
    """
    fig = fig if fig is not None else plt.gcf()
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f'{name}.{fmt}')
    if axes is None:
        fig.savefig(path, dpi=dpi, bbox_inches='tight')
    else:
        from matplotlib.transforms import Bbox
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        bbox = Bbox.union([a.get_tightbbox(renderer) for a in axes])
        bbox = bbox.transformed(fig.dpi_scale_trans.inverted()).padded(0.05)
        fig.savefig(path, dpi=dpi, bbox_inches=bbox)
    return path
