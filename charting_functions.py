# Functions to assist with creating HTML and PNG-based copies of 
# Plotly charts
# By Ken Burchfiel
# Released under the MIT License

import pandas as pd
import plotly.express as px
from IPython.display import Image, display
import plotly.graph_objects as go

def save_and_display_image(fig, file_path, chart_height, chart_width, 
chart_scale, display_width = 720, save_html_copy = False):
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
                                title_div = 'h3', hide_modebar = False,
                                save_chart = True,
                                hover_data = [],
                                custom_data = [],
                                hover_template = ""):
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

    title_div: The div that you'd like to use for the title. Can be
    h3, h2, p, etc.

    title: The chart's title. If you need to add a subtitle, you can
    do so by placing "<br><sub>your_subtitle_text</sub>" after the 
    main title.

    save_chart: Set to True to save the final HTML-based chart
    to the file specified at file_path.

    file_path: The path (either absolute or relative) where the file
    should be saved. Don't include the 'HTML' at the end, as this will
    get added in automatically.       
    '''
    
    fig_for_HTML = go.Figure(fig) # Allows us to make a copy of the figure
    # that will be better suited for HTML display
    
    # Updating this figure for HTML rendering:
    # Since the title and annotation will be stored as separate HTML
    # elements, we should set margin_t and margin_b to 0 in order to
    # eliminate unnecessary space between the chart itself and these items.
    
    fig_for_HTML.update_layout(
    height = chart_height,
    margin_t = 0, margin_b = 0)


    if hide_modebar == True:
        config = {'displayModeBar': False, 'responsive':True} 
        # I find that the modebar sometimes gets in the way when
        # viewing charts on mobile devices. (The code for hiding the
        # modebar comes from
        # https://plotly.com/python/configuration-options/#hiding-the-plotly-logo-on-the-modebar .)

    else:
        config = {'responsive':True}
    
    
    # Creating an HTML copy of this file:
    fig_as_html = fig_for_HTML.to_html(config=config, 
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

    if save_chart == True:
        with open(file_path+'.html', 'w') as file:
            file.write(title_fig_and_annotation)

def render_static_and_interactive_charts(
    df, title, file_path,
    x, y,
    html_chart_height = 500, png_chart_height = 0,
    chart_width = 600,
      chart_scale = 4, color = None, markers = True,
    html_margin_t = 0, html_margin_b = 0, html_margin_r = 25,
    png_margin_t = 100, png_margin_b = 80,
    subtitle = '',
    category_orders = {}, color_discrete_sequence = None,
    hover_data = None, xaxis_title = None, yaxis_title = None,
    annotation_text = '', annotation_x = -0.16, annotation_y = -0.42,
    annotation_align = 'left', showarrow = False,
    annotation_xref = 'paper', annotation_yref = 'paper',
    title_y = None, legend_title = None, reorder_xaxis = False,
    categoryarray = [], title_div = 'h3', error_y = None, 
    error_y_minus = None, error_x = None, error_x_minus = None,
    hide_modebar = False,
    html_legend_orientation = 'h', html_legend_yanchor = 'bottom', 
    html_legend_y = 1.02, 
    html_legend_xanchor = 'center', html_legend_x = 0.5, 
    html_legend_maxheight = None, custom_data = [],
    hovertemplate = ""):

    '''This function creates both static (PNG-based) and interactive
    (HTML-based) figures. The interactive figures are created via
    create_responsive_html_chart(), which allows titles and 
    annotations to get text wrapped (by making them separate HTML
    elements). Meanwhile, the title, subtitle, and annotation are added
    directly to the PNG-based chart. As a result, certain modifications
    to the PNG-based chart, such as a height increase, will need to be 
    made in order to accommodate these additional elements.

    The HTML version of the chart will have separate <div> elements for its
    title/subtitle and annotation. Therefore, by default, html_margin_t 
    and html_margin_b (the margin_t and margin_b values,
    respectively, for the HTML-based chart) are set to 0 in order to 
    eliminate unnecessary space between the chart and these separate 
    <div> elements. However, if the chart has a legend above or below
    it, these two values may need to be tweaked accordingly. Meanwhile,
    the default setting for html_margin_r 
    (which doesn't yet have a PNG-based equivalent) allows the chart
    to take up more horizontal space, thus making it more readable on
    narrower screens.
    

    png_margin_t and png_margin_b refer to the margin_t and margin_b
    settings, respectively, to use within the PNG-based chart. Their 
    default values equal Plotly's default values (as specified in
    https://plotly.com/python/reference/layout/) as of 2026-10-03.

    category_orders is a dictionary that you can use to manually reorder
    field values. For more on this parameter, see
    https://plotly.com/python/legend/#legend-order .
    
    html_chart_height refers to the desired height of the HTML-based chart.

    png_chart_height specifies the desired height of the PNG chart. If 
    kept at its default value (0), this height will automatically be
    calculated using the following forumla:
    png_chart_height = html_chart_height + (png_margin_t - html_margin_t)
    + (png_margin_b + html_margin_b). (Basically, we're increasing 
    the height by the difference between our PNG and HTML margin settings
    so that the PNG margins won't eat into the space for the graph itself.

    reorder_xaxis: Set to True to manually update the order in which
    x-axis values appear. This can be helpful from time to time to
    ensure that items are in the right chronological order (particularly
    when not all years have data available for all values passed to 
    the color argument).

    categoryarray: The array to use to reorder the x axis.
    
    error_y, error_y_minus, error_x, and error_y_minus specify which
    error-bar fields, if any, to use within the figure.

    annotation_text will be applied within both the HTML chart and the 
    PNG one; however, all other annotation parameters (i.e. 
    annotation_x, annotation_y, 
    annotation_align, showarrow, annotation_xref, and
    annotation_yref) will get applied to the PNG chart only.

    The default HTML legend options will place the legend at the 
    top center of the chart. This frees up valuable display area for 
    the chart to expend horizontally on mobile devices. (Similar settings
    could also work well for PNG-based charts, though they would probably
    need some tweaking). 
    
    Note that setting legend_yanchor to 'bottom' allows
    the legend to extend up from the legend_y value, rather than down
    from it. This helps prevent legends from overlapping the chart on
    narrow screens, and also eliminates wasted white space between the
    legend and chart on wider screens.    

    One issue with this approach, though, is that the legend can grow
    increasingly tall on narrower screens, thus cutting into space for
    the chart. Therefore, it may be useful to specify a max-height
    setting (i.e. of around 130) in order to ensure that the chart itself
    will remain viewable.

    It also appears that, if any of these legend values is set to None, 
    Plotly will simply maintain its default setting for that variable. Thus, 
    'None' should work well as a default argument for at least some of
    these items.

    
    hover_data: Additional variables to include within the *default* 
    hover template.
    
    custom_data: Additional variables to display within your *custom*
    hover template (defined via the hovertemplate) argument.

    hovertemplate: A custom template that specifies how hover data 
    should be formatted. Example (that incorporates custom_data values):

    custom_data = ['Response_Count_emp_total', 'age_range']
    hovertemplate = "Year: <b>%{x}</b><br>Age range: \
<b>%{customdata[1]}</b><br>Total employment: <b>%{y:,.0f}</b><br>Response \
count: <b>%{customdata[0]:,}</b><extra></extra>"   

    For crucial documentation on hovertemplate, visit
    https://plotly.com/python/hover-text-and-formatting/ . You'll get the 
    hang of them faster than you think (especially if you know some
    rudimentary HTML).
    

    Note: If hover_data isn't empty, but hover_template is not an empty 
    string, the hover_data content won't have any effect. Meanwhile, 
    if custom_data contains values, but hovertemplate is an empty string,
    custom_data values won't get shown.

    (It would also be possible to use the same parameter for both
    custom_data and hover_data values, then determine which of *those*
    parameters it will be applied to based on the status of hovertemplate.)
    '''
    

    # Creating a figure that will be used as the basis for both
    # our HTML and PNG-based charts:
    fig = px.line(df,
    x = x, y = y,
    hover_data = hover_data, markers=markers,
    color = color,
    error_y = error_y, error_y_minus = error_y_minus,
    error_x = error_x, error_x_minus = error_x_minus,
    category_orders = category_orders, custom_data = custom_data,
    color_discrete_sequence = color_discrete_sequence).update_layout(
    xaxis_title = xaxis_title, yaxis_title = yaxis_title,
    legend_title=legend_title)
    if reorder_xaxis == True:
        fig.update_xaxes(categoryorder = 'array',
categoryarray = categoryarray)

    if len(hovertemplate) > 0:

        fig.update_traces(hovertemplate = hovertemplate)
        

    # Creating an HTML-specific copy to which certain HTML-only settings
    # can get applied:
    fig_for_html = go.Figure(fig).update_layout(height = html_chart_height, 
    margin_b = html_margin_b, margin_t = html_margin_t, 
    margin_r = html_margin_r, legend_orientation = html_legend_orientation,
    legend_yanchor = html_legend_yanchor, legend_y = html_legend_y, 
    legend_xanchor = html_legend_xanchor, legend_x = html_legend_x, 
    legend_maxheight = html_legend_maxheight)    

    if len(subtitle) > 0:
        title_and_subtitle = title + '<br><sub>' + subtitle + '</sub>'
    else:
        title_and_subtitle = title

    # Creating and saving an HTML copy of the chart that can get
    # incorporated into an HTML-based blog post:
    create_responsive_html_chart(
        fig = fig_for_html, chart_height = html_chart_height,
        annotation_text = annotation_text, 
        file_path = file_path, title = title_and_subtitle,
        title_div = title_div, hide_modebar = hide_modebar)
    
    # Preparing the figure for PNG export: (This will involve adding
    # in our title, subtitle, and annotation--and also adjusting the 
    # chart's height and margins to make room for this
    # additional content.
    if png_chart_height == 0:
        png_chart_height = html_chart_height + (
        png_margin_t - html_margin_t) + (
        html_margin_t - html_margin_b)
    fig.update_layout(title = title_and_subtitle,
    title_y = title_y, height = png_chart_height, margin_t = png_margin_t,
    margin_b = png_margin_b)
    fig.add_annotation(x = annotation_x, y = annotation_y,
    align = annotation_align,
    text = annotation_text, showarrow = showarrow, 
    xref = annotation_xref, yref = annotation_yref)

    print(file_path)
    
    save_and_display_image(fig, file_path, 
    png_chart_height, chart_width, chart_scale)

    return fig_for_html # Having access to the HTML-based figure can be helpful
    # for further customization and testing.