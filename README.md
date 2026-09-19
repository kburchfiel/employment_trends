## Employment Trends Dashboard [Work in progress]

By Ken Burchfiel

Released under the MIT License

*Note: I did not use generative-AI tools within this project.*

* This repository contains the **Employment Trends Dashboard** (available at http://kburchfiel.github.io/employment_trends/occ_dashboard.html), which shows estimated United States employment totals, by a user-selected interval (year, half-year, quarter, or month) for hundreds of occupations. It's also possible to view employment totals by age range for larger occupations and to display 95% confidence intervals (though I may need to tweak my method for generating these intervals; see to-do list for more details).

<p style=color:red><b>Due to low sample sizes for many occupations, the results in this dashboard should be interpreted with caution.</b></style>

To create this dashboard dashboard, I first imported IPUMS CPS data (see below) into Python; created pivot tables that store monthly employment totals (either by age range or by all ages together); and then exported these tables to JavaScript files that get read by the dashboard's main HTML file.

### Data source

The data within this dashboard was sourced from https://cps.ipums.org/ . Its citation is as follows:

Sarah Flood, Miriam King, Renae Rodgers, Steven Ruggles, J. Robert Warren, Daniel Backman,  Etienne Breton, Grace Cooper, Julia A. Rivera Drew, Stephanie Richards, David Van Riper, and Kari C.W. Williams. IPUMS CPS: Version 13.0 [dataset]. Minneapolis, MN: IPUMS, 2025. https://doi.org/10.18128/D030.V13.0

This IPUMS data is itself a derivative of Current Population Survey data. To learn more about this survey, visit https://www.census.gov/programs-surveys/cps.html .

### To-Dos

* Within your Python file, create a linear regression that determines which year/month pairs had statistically-significant differences in employment relative to the latest data (i.e. August 2026). Share updates on Reddit as needed. (And consult responses to https://forum.ipums.org/t/what-would-be-the-best-way-to-determine-whether-an-increase-in-total-employment-for-a-given-occupation-is-statistically-significant/7188 for guidance on what regression, test, etc. to use.)

* Add a search box to your occupation dropdown list to make it easier to find certain occupations--or point individuals to the JavaScript file that contains these options. (See https://stackoverflow.com/questions/14148538/multiple-selections-with-datalist for reference.)

* Double-check your methods for calculating confidence intervals by replying within [this thread](https://forum.ipums.org/t/calculating-standard-errors-using-cps-basic-monthly-microdata/6408/6). 

* Consider adding unemployment data into your dashboard as well--as long as the files aren't too large. This will involve (1) adding the data to your existing CSV file (probably via a horizontal merge), and (2) adding a metric-selection option.

* Figure out how to add thousands separators to confidence-interval data within tooltips.