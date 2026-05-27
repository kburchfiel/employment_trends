## Employment Trends Dashboard

By Ken Burchfiel

Released under the MIT License

The simple dashboard created by this code (available at http://kburchfiel.github.io/employment_trends/occ_dashboard.html) shows estimated United States employment totals, by year and month, for hundreds of occupations. <span style=color:red><b>Due to low sample sizes for many occupations, these results should be interpreted with caution.<b></style>

To create this dashboard, I first imported IPUMS CPS data (see below) into Python; created a pivot table that shows employment counts by year and month; and saved the table as a .txt file. I then copied and pasted this table into the code for my HTML page (occ_dashboard.html).

When a user selects an occupation of interest, Danfo.js code within the HTML file filters the underlying dataset to show only rows for that occupation. Next, Plotly.js code is called to create a line chart that shows trends for this occupation.


### Data source

The data within this dashboard was sourced from https://cps.ipums.org/ . Its citation is as follows:

Sarah Flood, Miriam King, Renae Rodgers, Steven Ruggles, J. Robert Warren, Daniel Backman,  Etienne Breton, Grace Cooper, Julia A. Rivera Drew, Stephanie Richards, David Van Riper, and Kari C.W. Williams. IPUMS CPS: Version 13.0 [dataset]. Minneapolis, MN: IPUMS, 2025. https://doi.org/10.18128/D030.V13.0

This IPUMS data is itself a derivative of Current Population Survey data. To learn more about this survey, visit https://www.census.gov/programs-surveys/cps.html .