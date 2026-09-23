## Employment Trends Dashboard [Work in progress]

By Ken Burchfiel

Released under the MIT License

*Note: I did not use generative-AI tools within this project.*

* This repository contains the **Employment Trends Dashboard** (available at http://kburchfiel.github.io/employment_trends/occ_dashboard.html), which shows estimated United States employment totals, by a user-selected interval (year, half-year, quarter, or month) for hundreds of occupations. It's also possible to view employment totals by age range for larger occupations and to display 95% confidence intervals (though I may need to tweak my method for generating these intervals; see to-do list for more details).

<p style=color:red><b>Due to low sample sizes for many occupations, the results in this dashboard should be interpreted with caution.</b></p>

To create this dashboard dashboard, I first imported IPUMS CPS data (see below) into Python; created pivot tables that store monthly employment totals (either by age range or by all ages together); and then exported these tables to JavaScript files that get read by the dashboard's main HTML file.

[Click here](https://kburchfiel3.wordpress.com/2026/09/22/cps-data-indicates-that-us-software-developer-employment-has-increased-since-2022/) to read view a blog post that discusses findings related to software-developer employment.

### Data source

The data within this dashboard was sourced from https://cps.ipums.org/ . Its citation is as follows:

Sarah Flood, Miriam King, Renae Rodgers, Steven Ruggles, J. Robert Warren, Daniel Backman,  Etienne Breton, Grace Cooper, Julia A. Rivera Drew, Stephanie Richards, David Van Riper, and Kari C.W. Williams. IPUMS CPS: Version 13.0 [dataset]. Minneapolis, MN: IPUMS, 2025. https://doi.org/10.18128/D030.V13.0

This IPUMS data is itself a derivative of Current Population Survey data. To learn more about this survey, visit https://www.census.gov/programs-surveys/cps.html .

### To-Dos

* Use R to spot-check findings in order to ensure that your code is working as expected.

* Check changes in proportions within svy-based Python code for statistical significance.

* Use ACS1 data for recent years to:

    1. Estimate and visualize the total number of individuals employed as software developers
    2. Estimate the proportion of individuals (both total and, if sample sizes allow, by age) who are employed as software developers
    3. Use logistic regressions to determine whether these proportions (again, both overall and by age if possible) have changed signifiantly over time
    5. Estimate unemployment rates, both overall and (if you have large-enough samples) by age, for software developers over time
    6. Determine whether *these* changes have been statistically significant.

    Note: As part of these updates, repurpose your existing code for calculating totals and proportions to calculate replicate weights (i.e. by setting the 'method' argument as needed; see https://svylab.com/learn/notes/posts/svy-vs-r-comparison/#replication-based-estimation for guidance on both creating an ACS sample and on passing the correct parameters to your code.

* Review relevant responses to  https://forum.ipums.org/t/calculating-standard-errors-using-cps-basic-monthly-microdata/6408/8 .

* Try to find a way to determine, via a regression analysis, whether differences in totals between two years were statistically significant. Share updates on Reddit as needed. (And consult responses to https://forum.ipums.org/t/what-would-be-the-best-way-to-determine-whether-an-increase-in-total-employment-for-a-given-occupation-is-statistically-significant/7188 for guidance on what regression, test, etc. to use.)

* Add a search box to your occupation dropdown list to make it easier to find certain occupations--or point individuals to the JavaScript file that contains these options. (See https://stackoverflow.com/questions/14148538/multiple-selections-with-datalist for reference.) Consider replacing your existing select-menu code with a JavaScript-based approach that would better facilitate searching.

* Consider adding unemployment data into your dashboard as well--as long as the files aren't too large. This will involve (1) adding the data to your existing CSV file (probably via a horizontal merge), and (2) adding a metric-selection option.

* Figure out how to add thousands separators to confidence-interval data within tooltips.

* Consider creating an HTML-based blog post, perhaps using a Jinja2 setup, that would allow interactive charts to appear alongside your text. (This could be hosted on the GitHub site for your project.)

* Update your WordPress blog post as needed.

* As an experiment, try exporting your Markdown blog post to HTML so that you can see whether it shows up correctly (e.g. with PNG images present) within your GitHub pages site. (Use pandoc for this task so that you can control the widths of images; I think {width:600px} or something similar at the end of the image tag would work, but double-check the documentation.