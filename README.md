## Employment Trends Dashboard [Work in progress]

By Ken Burchfiel

Released under the MIT License

*Note: I did not use generative-AI tools within this project.*

* This repository contains the **Employment Trends Dashboard** (available at http://kburchfiel.github.io/employment_trends/occ_dashboard.html), which shows estimated United States employment totals, by a user-selected interval (year, half-year, quarter, or month) for hundreds of occupations. It's also possible to view employment totals by age range.

<p style=color:red><b>Due to low sample sizes for many occupations, the results in this dashboard should be interpreted with caution.</b></style>

To create this dashboard dashboard, I first imported IPUMS CPS data (see below) into Python; created pivot tables that store monthly employment totals (either by age range or by all ages together); and saved these tables into the same .csv file. I then copied and pasted this CSV data into a standalone JavaScript file (csv_data.js) which then gets imported by my dashboard's main HTML file.

### Data source

The data within this dashboard was sourced from https://cps.ipums.org/ . Its citation is as follows:

Sarah Flood, Miriam King, Renae Rodgers, Steven Ruggles, J. Robert Warren, Daniel Backman,  Etienne Breton, Grace Cooper, Julia A. Rivera Drew, Stephanie Richards, David Van Riper, and Kari C.W. Williams. IPUMS CPS: Version 13.0 [dataset]. Minneapolis, MN: IPUMS, 2025. https://doi.org/10.18128/D030.V13.0

This IPUMS data is itself a derivative of Current Population Survey data. To learn more about this survey, visit https://www.census.gov/programs-surveys/cps.html .

### To-Dos

* Round values within exported unemployment CSV files to two decimal digits. This should reduce your file sizes by a decent amount.

* Add a search box to your occupation dropdown list to make it easier to find certain occupations. (See https://stackoverflow.com/questions/14148538/multiple-selections-with-datalist for reference.)

* Find a way to hide occupations that don't meet the 'large occupation' threshold when age range is selected, thus preventing users from choosing options for which we don't have any data.

* See if there's a way to show age ranges as colors and occupations as different line formats (or vice versa).

* Update your sample-generation code to incorporate PSUs and strata, thus allowing for more accurate confidence intervals. See [this thread](https://forum.ipums.org/t/calculating-standard-errors-using-cps-basic-monthly-microdata/6408/6) for reference.

* Consider adding unemployment data into your dashboard as well--as long as the files aren't too large. This will involve (1) adding the data to your existing CSV file (probably via a horizontal merge), and (2) adding a metric-selection option.