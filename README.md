## Employment Trends Dashboards [Work in progress]

By Ken Burchfiel

Released under the MIT License

*Note: I did not use generative-AI tools within this project.*

This repository contains two interactive dashboards:

* The **Employment Trends Dashboard** (available at http://kburchfiel.github.io/employment_trends/occ_dashboard.html) shows estimated United States employment totals, by a user-selected interval (year, half-year, quarter, or month) for hundreds of occupations. 

* The **Employment Trends by Age Dashboard** (available at http://kburchfiel.github.io/employment_trends/occ_by_age_range_dashboard.html) is similar, except that it shows estimated totals *by age range* for occupations with a recent estimated employment of at least 1 million.

<p style=color:red><b>Due to low sample sizes for many occupations, the results in these dashboards should be interpreted with caution.</b></style>


To create these dashboard, I first imported IPUMS CPS data (see below) into Python; created pivot tables that store monthly employment totals (either by age range or by all ages together); and saved these tables as .txt files. I then copied and pasted these tables into the code for my HTML pages (occ_dashboard.html and occ_by_age_range_dashboard.html).

When a user selects an occupation of interest, Danfo.js code within the HTML file filters the underlying dataset to show only rows for that occupation. Next, Plotly.js code is called to create a line chart that shows trends for this occupation.

### Data source

The data within this dashboard was sourced from https://cps.ipums.org/ . Its citation is as follows:

Sarah Flood, Miriam King, Renae Rodgers, Steven Ruggles, J. Robert Warren, Daniel Backman,  Etienne Breton, Grace Cooper, Julia A. Rivera Drew, Stephanie Richards, David Van Riper, and Kari C.W. Williams. IPUMS CPS: Version 13.0 [dataset]. Minneapolis, MN: IPUMS, 2025. https://doi.org/10.18128/D030.V13.0

This IPUMS data is itself a derivative of Current Population Survey data. To learn more about this survey, visit https://www.census.gov/programs-surveys/cps.html .

### To-Dos

* Replace Danfo.js code with D3-array code. (This will also involve importing your data in CSV format; see Python dataset-generation code within your county growth dashboard project for reference. That project will also be a useful reference for adding D3-array code into your employment-trends dashboards.)

    * Since these CSV files will be pretty large, you may also want to figure out a way to easily import them into JavaScript. One option might be to just paste in the CSV file using starting and ending quotes, as shown here: https://www.freecodecamp.org/news/javascript-multiline-string-how-to-create-multi-line-strings-in-js/ (See the How to Create Multiline Strings with Template Literals in JavaScript section)

* Round values within exported CSV files to integers (for employment totals) and to two decimal digits (for unemployment rates). This should reduce your file sizes by a decent amount.

* Allow multiple occupations to be compared within the same chart by converting your occupation-selection-menu to one that allows multiple items to be selected. (This would be feasible with D3-array/vanilla array code, but probably not within Danfo.js, since the .query() method doesn't have an 'in' or 'isin' option.)

* Update your sample-generation code to incorporate PSUs and strata, thus allowing for more accurate confidence intervals. See [this thread](https://forum.ipums.org/t/calculating-standard-errors-using-cps-basic-monthly-microdata/6408/6) for reference.

* If your CSV files end up being small enough: Consider merging your overall and age-specific employment-totals dashboards into the same dashboard. You could have an age-selector menu with 'All' or 'By age range' options that would let users view employment totals by age brackets or by everyone together. (When 'By age range' is selected, only the first occupation within the dropdown menu would be used.)

* Build out your unemployment-rates dashboard, but keep an eye on confidence intervals also.