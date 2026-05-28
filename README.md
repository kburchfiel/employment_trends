## Employment Trends Dashboards

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