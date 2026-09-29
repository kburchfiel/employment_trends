# Functions for analyzing weighted survey data
# By Ken Burchfiel
# Released under the MIT license

import pandas as pd
import svy
import numpy as np
import polars as pl

def perform_svy_analysis(sample, y, analysis_type, by = [], where = None, 
    col_suffix = '', return_as_pandas = False):
    '''This function can perform various types of svy analyses. It also
    calculates unweighted response counts, which can be helpful to keep
    track of when performing survey analyses.

    analysis_type: The type of svy analysis to run. The function currently
    supports 'prop' and 'total' analyses.
    
    Note: when analysis_type is set to 'total', you should probably
    pass an unweighted count column (i.e. one that has a value of 1
    for each respondent) as the y value. Meanwhile, when using 'prop'
    as the analysis type, 

    For definitions of y, by, and where, consult the svy documentation
    for parameter estimation 
    at https://svylab.com/docs/svy/tutorials/estimation.html .

    Examples of what these arguments might look like:

    y: 'Count' (with values of 1 for every row) for a 'total' analysis 
    type; a DV field like 'employment_status' for a 'prop' analysis type.
    (The weighted proportion of your sample within each DV value,
    e.g., 'employed', 'unemployed', etc., will then get calculated.)

    by: ['year_and_half', 'occ2010', 'age_range']. (The same values
    should work well for both total-and prop-type analyses.)
    
    where: [svy.col("occ2010") != "niu", svy.col(
"employed") == 1, svy.col('occ2010').isin(large_occupations)]. (Again,
the same values will work well for both total- and prop-type analyses.)

    col_suffix: A suffix that will be added to the end of all output
    columns not in by. (This will make it easier to differentiate
    between analyses for various y values.)

    return_as_pandas: set to True to return the output as a Pandas
    DataFrame; set to False to keep it as a Polars DataFrame.

    '''
    
    # Determining which svy analysis to perform:
    if analysis_type == 'total':
        survey_method = sample.estimation.total
    elif analysis_type == 'prop':
        survey_method = sample.estimation.prop
    else:
        print("perform_svy_analyses doesn't support this analysis type yet.")

    # Performing the requested svy analysis:
    df_estimates = survey_method(
    y = y, by = by, where = where).to_polars()
    df_estimates

    # Setting the y field in the results table to a string will prevent
    # an error from getting raised during a subsequent merge operation.

    if y in df_estimates.columns: # This value won't actually be present
        # within our field names when totals are being analyzed.
        df_estimates = df_estimates.cast({y:pl.String}) # See
        # https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.cast.html
    

    # Specifying lengths for upper and lower error bars: (This will make it
    # easier to add confidence intervals to charts.)
    df_estimates = df_estimates.with_columns(
    (pl.col('uci') - pl.col('est')).alias("error_upper"),
    (pl.col('est') - pl.col('lci')).alias("error_lower"))
    # Based on: https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.with_columns.html
    # Creating percentage versions of certain columns for easier readability:
    for c in ['est', 'se', 'lci', 'uci', 'error_upper', 'error_lower']:
        df_estimates = df_estimates.with_columns((pl.col(c) * 100).alias(c+'_as_pct'))
    
    # Determining the number of unweighted respondent counts with a 
    # valid y value:
    # Note the use of filter_records() to trim out 
    # results that won't be present within our analysis. ('where' should
    # be used to filter records within actual svy analyses rather
    # than 'filter_records', as it's important for all records to be
    # passed to the analysis function so that accurate confidence intervals
    # can be created.
    # NOTE: I added the (analysis_type == 'prop') condition because,
    # in that case, we'll still want to run a pivot-table
    # call even if 'by' is an empty list so that respondent counts for 
    # each distinct dependent-variable value can get calculated. (In this
    # case, [y] will be pivot_table()'s index field. 
    # However, I haven't yet tested out this change--
    # so do make sure that it works!
    
    if (by != []) | (analysis_type == 'prop'):

        # Specifying parameters for the response-counts pivot table:
        # The default values here will be ideal when the analysis
        # type is 'total'.
        group_cols = [pl.col(by_entry) for by_entry in by]

        if analysis_type == 'prop':
            group_cols += [pl.col(y)]
            

        # print("group_cols:", group_cols)
        # filter_records will get called to exclude values from
        # the pivot table that were also excluded from our svy analyses
        # via our analysis function's 'where' argument. We wouldn't 
        # have wanted to use filter_records for that function because
        # it's important to pass all entries, including non-valid ones,
        # to it in order to calculate accurate confidence intervals.
        # (We're not calculating confidence intervals for respondent
        # counts, though, so we don't need to worry about that issue
        # here.)

        # Note: For the following code, you don't need to select a specific 
        # column, like 'Count', on which to base your counts; instead, you 
        # can simply use 'len' to figure out how many rows are present in 
        # each grouping. (See
        # https://docs.pola.rs/api/python/stable/reference/dataframe/\
        # api/polars.dataframe.group_by.GroupBy.len.html)
        
        
        df_unweighted_counts = sample.wrangling.filter_records(
        where).data.group_by(
        group_cols).len(name="Response_Count")
        

        if y in df_unweighted_counts.columns:
            df_unweighted_counts = df_unweighted_counts.cast({y:pl.String}) 

        # Merging our estimate and count tables together:
        df_estimates_and_counts = df_estimates.join(
        df_unweighted_counts, on = group_cols, how = 'left')
        df_estimates_and_counts

    else: # Since there's nothing to pivot the DataFrame by, 
        # we should simply count the number of DV entries
        # within the filtered sample.

        df_estimates_and_counts = df_estimates_and_counts.with_cols(
        sample.wrangling.filter_records(
        where).data[y].len()).alias("Response_Count")

    # If a given response (within a proportion analysis) had 0 entries,
    # it will probably have a missing Response_Count entry--which the
    # following code will replace with a 0.

    df_estimates_and_counts = df_estimates_and_counts.with_columns(
    pl.col('Response_Count').fill_null(0))
    
    # Adding suffixes: (We won't want to add these to our 'by' values
    # since that could interfere with any subsequent merge operations.)
    if col_suffix != '':
        col_renaming_dict = {c:c+col_suffix if c not in by else c 
        for c in df_estimates_and_counts.columns}
        
        df_estimates_and_counts = df_estimates_and_counts.rename(
        columns = col_renaming_dict)

    if return_as_pandas == True:
        return df_estimates_and_counts.to_pandas()
    else:
        return df_estimates_and_counts

def create_svy_reg(
    sample, y, x_list, regression_type = 'logistic', where = [],
    max_sig_p_value = 0.05):
    '''This function calls svy's glm.fit() method to create a regression
    analysis, then adds some additional fields to the results.
    Note: Currently, the function only supports logistic regressions;
    I may update it in the future to also accommodate linear regressions.
    
    sig_p_value_threshold: The highest p-value to consider statistically
    significant.)
    '''

    if regression_type == 'logistic':
        family = 'binomial'
        link = 'logit'

    else:
        raise ValueError("Currently, the function only supports \
logistic regressions, though it shouldn't take too long to update it \
to accommodate other regression types.")

    logistic_reg_model = sample.glm.fit(y = y, x = x_list, 
    family = family, link = link, where = where)
    df_reg_results = logistic_reg_model.to_polars().to_pandas()

    if regression_type == 'logistic':
        for c in ['estimate', 'conf_low', 'conf_high']:
            df_reg_results[
            c+'_odds_ratio'] = np.exp(df_reg_results[c])
    
    df_reg_results['Significant'] = np.where(
    df_reg_results['p_value'] <= max_sig_p_value, 'Y', '')

    # Moving certain fields of interest to the left of the DataFrame:
    # (The insert operation will end up inserting the last fields
    # within the list to the left of the first fields, so to
    # counter this behavior, I'm using [::-1] to reverse the list
    # before passing it to the insert() method call.
    for c in ['term', 'estimate', 'p_value', 'Significant'][::-1]:
        df_reg_results.insert(
        0, c, df_reg_results.pop(c))
    
    return df_reg_results

def survey_pivot(df, weight_col, analysis_method, by_list = [], 
    dv = '', col_suffix = '', ones_col = ''):
    '''This function uses the pivot_table() function within Pandas to
    generate weighted survey estimates (but not confidence intervals or 
    regression stats.

    NOTE: This function could be overhauled to use Polars in place of
    Pandas, which may speed up its execution significantly for particularly
    large datasets.
    
    analysis_method: Can be 'Total' (for generating weighted sums)
    or 'Proportion' (for generating weighted proportions). Other
    methods may be added in the future.

    by_list: A list of variables that will be passed to the index argument
    of the pivot-table function. (For proportions, the dv argument 
    will also be added to this list. Note that this list can be empty
    for proportions, in which case the function will calculate the 
    proportion of respondents in each DV value.)

    dv: The dependent variable to use for proportions. This variable
    won't have any effect when analysis_method is set to Total, as 
    in that case, the function will simply find the total weight_col sum
    for each group of by_list values.    

    col_suffix: A suffix that will be added to the end of all output
    columns not in by. (This will make it easier to differentiate
    between analyses for various types and DV values.)

    ones_col: A column containing a value of 1 for each row. This column
    will be used to generate unweighted response sums.
    
    '''
     
    if analysis_method == 'Total':
        index = by_list

    elif analysis_method == 'Proportion':
        index = by_list + [dv]
    else:
        raise ValueError("That analysis method hasn't yet \
been implemented within this function.") 

        
    df_pivot = pd.pivot_table(df, index=index, 
    values = [weight_col, ones_col], 
    aggfunc = 'sum').reset_index()
    
    df_pivot.rename(columns = {ones_col:'Response_Count',
    weight_col:'Total'}, inplace = True)
    
    if analysis_method == 'Proportion':
        if by_list == []: # We don't have any grouping variables in this 
            # case to pass to groupby, so we'll 
            df_pivot['Proportion'] = (
            df_pivot['Total'] / df_pivot['Total'].sum())
        else:
            df_pivot['Proportion'] = (
            df_pivot['Total'] / df_pivot.groupby(by_list)[
            'Total'].transform('sum'))

    if col_suffix != '':
            col_renaming_dict = {c:c+col_suffix if c not in by_list else c 
            for c in df_pivot.columns}
            df_pivot.rename(columns = col_renaming_dict, inplace = True)

    return df_pivot
