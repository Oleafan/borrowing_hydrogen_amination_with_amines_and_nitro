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
                tochem=True, 
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
    
    if tochem:
        y_ticks_l=[ to_chem(i) for i in y_ticks_l ]
    
    x_ticks_l=data_crtab.columns.values

    if x_ticks:
        x_ticks_l = x_ticks

    if rename_x_ticks_dict:
        x_ticks_l = [rename_x_ticks_dict[x] for x in x_ticks_l]
    if tochem:
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
    plt.yticks(fontsize=13)

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
    plt.yticks(fontsize=13)

    if rename_x_ticks_dict:
        x_ticks_l = [rename_x_ticks_dict[x] for x in x_ticks_l]
    
    plt.subplot(2, 1, 2)
    ax =sns.heatmap(data_crtab_diff_1.fillna(0).apply(pd.to_numeric, errors='coerce').values, xticklabels=x_ticks_l, yticklabels=y_ticks_l,
              cbar_kws={'label': 'number of hits'}, cmap=cmap_custom , annot =True, fmt=".0f")
    
    ax.set_xlabel(xlabel, fontsize = 13)
    # ax.set_title('Data on catalytic activity since 2022', fontsize = 15)
    ax.set_ylabel('Data since 2022', fontsize = 13)
    plt.xticks(fontsize=13, rotation=45)
    plt.yticks(fontsize=13)
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