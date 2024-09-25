# this function is defined in the utilities of the primitive generator, please make sure
# to remove that one. 
from .common_libs import *

layer_colors = {2: '#b0dcff', 7: '#5c5429', 
        14: 'green', 15: '#322f99', 
        17: 'red', 35: 'red',
        132: '#b0f5d7', 999: '#0077be'}


def show_cells(cells, fig_size=(6.4, 4.8), show_layout = True):
    '''
    # input : layout cells, fig_size = (width, height) and show_layout boolean: true by default
    # output: plot function 
    # Visualize the layout using matplotlib
    '''
    # check if the cells input is a list
    if not isinstance(cells, list):
        cells = [cells]    # Convert non-list input into a list

    fig, ax = plt.subplots(figsize=fig_size, dpi=300)
    for cell in cells:
        for polygon in cell.polygons:
            points = polygon.points
            layer = polygon.layer
            color = layer_colors.get(layer, 'gray')  # Default color is black if layer not specified
            ax.fill(*zip(*points), color=color, alpha=0.3)
        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
        
        if show_layout:
            plt.show()

    return ax

