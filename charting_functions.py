# Functions to assist with creating HTML and PNG-based copies of 
# Plotly charts
# By Ken Burchfiel
# Released under the MIT License

import pandas as pd
import plotly.express as px
from IPython.display import Image, display
import plotly.graph_objects as go

def save_and_display_image(fig, file_path, chart_height, chart_width, chart_scale, display_width = 720, save_html_copy = False):
    '''This function saves the Plotly chart passed to 'fig' as both a PNG
    and (if save_html_copy is set to True) HTML file, then displays the 
    PNG file within a Jupyter notebook.
    Don't add 'png' to the file path, as this will get added in automatically.
    '''

    # Saving a PNG image:
    fig.write_image(file_path + '.png', 
    height = chart_height, width = chart_width, scale = chart_scale)

    # Saving an interactive HTML copy:
    # Note: Setting 'full_html' to False will make it easier to incorporate
    # these HTML files into another HTML file (i.e. via a Jinja2 template).
    # Setting include_plotlyjs to 'cdn' can greatly reduce the file's
    # size.
    # See
    # https://plotly.com/python/interactive-html-export/#inserting-plotly-output-into-html-using-a-jinja2-template
    # for more details.
    if save_html_copy == True:
        fig.write_html(file_path + '.html', 
        include_plotlyjs = 'cdn', full_html = False,
        config={'responsive':True})
    display(Image(file_path + '.png', width = display_width))
    # Based on https://stackoverflow.com/a/35061341/13097194

def create_responsive_html_chart(fig, chart_height,
                                annotation_text, file_path, 
                                title = '',
                                margin_t = 100, margin_b = 80,
                                title_div = 'h3'):
    '''This function creates an interactive chart in which titles and 
    annotations can be wrapped as needed.
    
    Plotly, to the best of my knowledge, doesn't allow titles and
    annotations within figures to be wrapped. In addition, it can be hard 
    to ensure correct placement of annotations for responsive 
    (i.e. non-static) charts.
    Therefore, a workaround I learned online was to separate the chart 
    title and subtitle into separate HTML elements. This both allows for 
    text wrapping and simplifies the process of correctly positioning 
    annotations.

    NOTE: This function doesn't update the elements' style; instead,
    you should update them within the HTML file in wish you want to place
    these charts. (The classes assigned to each element should help with
    this.)

    margin_t and margin_b should equal the margins that exist within
    the chart at the time you call this function. (The default settings
    equal Plotly's own defaults; see 
    the margin_t and margin_b entries within
    https://plotly.com/python/reference/layout/ . Similarly, chart_height
    should equal the height of the chart passed to the fig parameter.
    (See code and comments for an explanation of why this is helpful.)

    title_div: The div that you'd like to use for the title. Can be
    h3, h2, p, etc.

    title: The chart's title. If you need to add a subtitle, you can
    do so by placing "<br><sub>your_subtitle_text</sub>" after the 
    main title.

    file_path: The path (either absolute or relative) where the file
    should be saved. Don't include the 'HTML' at the end, as this will
    get added in automatically.   
    
    '''
    
    fig_for_HTML = go.Figure(fig) # Allows us to make a copy of the figure
    # that will be better suited for HTML display
    
    # Updating this figure for HTML rendering:
    # Since the title and annotation will be stored as separate HTML
    # elements, we can (and should) set margin_t and margin_b to 0
    # so that they'll be closer to the figure. We should also subtract
    # our original margin_t and margin_b values from the chart's height
    # in order to account for these removed items. (Otherwise, the chart
    # will be taller than necessary.)
    
    fig_for_HTML.update_layout(
    height = chart_height - margin_t - margin_b,
    margin_t = 0, margin_b = 0) # Setting the top and bottom margins
    # to 0 will allow our separate title and annotation elements to move
    # closer to the actual chart

    # Creating an HTML copy of this file:
    fig_as_html = fig_for_HTML.to_html(config={'responsive':True}, 
    full_html = False, include_plotlyjs='cdn')

    # Creating a string that combines the title, figure, and annotation
    # together, thus allowing them to be saved as a single HTML file:
    # (Alternatively, I could have added standalone divs for these elements 
    # to a Jinja2 template. That approach would make it easier to 
    # customize the styling of my title and annotation elements, but would 
    # also be more complex.)
    # Adding class names to each element will make them
    # easier to style within our final HTML file.
    
    title_fig_and_annotation = f"<{title_div} class = 'chart_title'>\
{title}</{title_div}><div class = 'chart_contents'>{fig_as_html}\
</div><p class = 'chart_annotation'>{annotation_text}</p>"

    with open(file_path+'.html', 'w') as file:
        file.write(title_fig_and_annotation)    