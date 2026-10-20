# Functions for analyzing weighted survey data
# By Ken Burchfiel
# Released under the MIT license

import pandas as pd
import svy
import numpy as np
import polars as pl
import warnings
from polars_readstat import scan_readstat, ScanReadstat

def import_stata_data(file_path, cols_to_convert_to_strings = []):
    '''This function uses the polars_readstat library to import
    stata data via Polars. It also allows selected columns to be
    converted to strings, thus making those columns' meanings
    clearer.
    
    This code is based in part on the polars_readstat documuentation
    at: https://pypi.org/project/polars-readstat/'''
    
    # Reading in our Stata file's schema (which will make it easier to 
    # replace codes for variables with their corresponding names):
    
    dfp_schema = ScanReadstat(file_path)
    dfp_metadata = dfp_schema.metadata
    
    # Importing the dataset:
    # Note: This line could be updated later on to allow
    # only specific columns to be imported.
    dfp = scan_readstat(file_path).collect()
    print("The DataFrame is", len(dfp), "rows long.")
    
    # Converting specified columns to strings:
    
    for col in cols_to_convert_to_strings:
    
        # Retrieving the occupations that correspond to each occupation
        # code:
        col_label_dict = [v for v in dfp_metadata['variables'] 
        if v['name'] == col][0]['value_labels']
        # occ2010_label_dict
        
        # Renaming this column, then creating a copy that shows strings
        # in place of codes:
        
        dfp = dfp.rename({col:col+'_code'}).with_columns(
        (pl.col(col+'_code').cast(
        pl.String).replace(col_label_dict)).alias(col))
    
    return dfp

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
    

    # return df_estimates
    
    # Specifying lengths for upper and lower error bars: (This will make it
    # easier to add confidence intervals to charts.)
    df_estimates = df_estimates.with_columns(
    (pl.col('uci') - pl.col('est')).alias("error_upper"),
    (pl.col('est') - pl.col('lci')).alias("error_lower"))
    # Based on: https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.with_columns.html
    # Creating percentage versions of certain columns for easier readability:
    if analysis_type == 'prop':
        for c in ['est', 'se', 'lci', 'uci', 'error_upper', 'error_lower']:
            df_estimates = df_estimates.with_columns(
                (pl.col(c) * 100).alias(c+'_as_pct'))



    # Determining the number of unweighted respondents with a 
    # valid y value who are present within a given proportion
    # category:
    # Note the use of filter_records() to trim out 
    # results that won't be present within our analysis. ('where' should
    # be used to filter records within actual svy analyses rather
    # than 'filter_records', as it's important for all records to be
    # passed to the analysis function so that accurate confidence intervals
    # can be created.{
    # NOTE: I added the (analysis_type == 'prop') condition because
    # svy was updated in October 2027 to provide 'n' values 
    # automatically, thus making these calculations unnecessary
    # for most analysis types. However, these n values show the 
    # number of respondents for all proportion values rather than 
    # the number that match a certain value. The following code
    # will determine the number of respondents on which each
    # proportion estimate is based, which may prove helpful
    # in some cases.
    
    if analysis_type == 'prop':

        # Specifying parameters for the response-counts pivot table:
        # The default values here will be ideal when the analysis
        # type is 'total'.
        group_cols = [pl.col(by_entry) for by_entry in by] + [pl.col(y)]
            

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
        group_cols).len(name="prop_val_n")
        

        if y in df_unweighted_counts.columns:
            df_unweighted_counts = df_unweighted_counts.cast({y:pl.String}) 

        # Merging our estimate and count tables together:
        df_estimates = df_estimates.join(
        df_unweighted_counts, on = group_cols, how = 'left')
        
        # If a given response (within a proportion analysis) had 0 entries,
        # it will probably have a missing Response_Count entry--which the
        # following code will replace with a 0.
    
        df_estimates = df_estimates.with_columns(
        pl.col('prop_val_n').fill_null(0))
    
    # Adding suffixes: (We won't want to add these to our 'by' values
    # since that could interfere with any subsequent merge operations.)
    if col_suffix != '':
        col_renaming_dict = {c:c+col_suffix if c not in by else c 
        for c in df_estimates.columns}
        
        df_estimates = df_estimates.rename(
        col_renaming_dict)

    if return_as_pandas == True:
        return df_estimates.to_pandas()
    else:
        return df_estimates


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

def pl_survey_pivot(dfp, weight_col, analysis_method,
                    by_list = [], dv = '', col_suffix = '',
                    add_suffix_to_dv = False,
                    convert_output_to_pandas = False):
    
    '''
    This function uses group_by(), agg() and other Polars functions to
    generate weighted survey estimates (but not confidence intervals or 
    regression stats.
    
    dfp: The Polars DataFrame containing the data to be analyzed.
    
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
    between analyses for various types and DV values.) The function
    won't attempt to add a suffix if this value is an empty string.
    
    convert_output_to_pandas: If True, the function will return a Pandas
    DataFrame; if False, it will return a Polars DataFrame.
    '''
    
    if analysis_method == 'Total':
        index = by_list
        if dv != '':
            # It's possible that, in this case, the results will be 
            # misinterpreted to show the totals for each DV value, which 
            # is not the case. Therefore, I added in the following warning.
            warnings.warn("WARNING: You've requested to calculate totals, but \
    your dv argument is not an empty string. The function will calculate \
    totals for each by-list combination only regardless of dv values. To \
    incorporate your dv into your totals, add it to by_list instead.")
    
        
    elif analysis_method == 'Proportion':
        index = by_list + [dv]
    else:
        raise ValueError("That analysis method hasn't yet \
    been implemented within this function.") 
    
    
    dfp_grouped = dfp.group_by(
    index).agg(
    pl.col(weight_col).sum().name.suffix('_sum'), 
    pl.col(weight_col).count().name.suffix('_count'))

    if analysis_method == 'Proportion':
        # In this case, proportions for each by_list combination will be 
        # calculated by dividing the weighted sum for each row by 
        # the weighted sum for *all* rows that have the same
        # by_list combination. 
        # This response is based on
        # https://stackoverflow.com/a/74513100/13097194 , which also
        # references https://docs.pola.rs/user-guide/migration/pandas/#pandas-transform .
        
        dfp_grouped = dfp_grouped.with_columns(
        ((pl.col(weight_col+'_sum') / pl.col(
        weight_col+'_sum').sum()).over(by_list)).alias('Proportion'))
        dfp_grouped
    
        # It can be useful to express this proportion as a percentage
        # as well.
    
        dfp_grouped = dfp_grouped.with_columns(
        (pl.col('Proportion')*100).alias('Percentage'))

    if col_suffix != '':
        if add_suffix_to_dv == False:
            suffix_free_cols = by_list + [dv]
        else:
            suffix_free_cols = by_list   
        
        # In some cases, it might be ideal to rename the dv as well
        col_renaming_dict = {c:c+col_suffix if c not in suffix_free_cols else c 
                for c in dfp_grouped.columns}
        
        dfp_grouped = dfp_grouped.rename(col_renaming_dict)
        
    dfp_grouped = dfp_grouped.sort(index)

    # Renaming output fields:
    # (This code works well for Total and Proportion
    # analyses, but may need to be modified or skipped for
    # other analysis types, such as mean/median calculations.)
    dfp_grouped = dfp_grouped.rename(
    {weight_col+'_sum':'Total', weight_col+'_count':'Count'})
    
    if convert_output_to_pandas == True:
        return dfp_grouped.to_pandas()
    else:
        return dfp_grouped



def survey_pivot(df, weight_col, analysis_method, by_list = [], 
    dv = '', col_suffix = '', ones_col = ''):
    '''Note: pl_survey_pivot, which is Polars-based, is a newer version
    of this Pandas-based function. I recommend using the former (which
    still allows you to export results to Pandas if desired) instead
    of the latter. 
    
    This function uses the pivot_table() function within Pandas to
    generate weighted survey estimates (but not confidence intervals or 
    regression stats.
    
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
        if dv!= '':
            warnings.warn("WARNING: You've requested to calculate totals, but \
your dv argument is not an empty string. The function will calculate \
totals for each by-list combination only regardless of dv values. To \
incorporate your dv into your totals, add it to by_list instead.")

    elif analysis_method == 'Proportion':
        index = by_list + [dv]
    else:
        raise ValueError("That analysis method hasn't yet \
been implemented within this function.") 

        
    df_pivot = pd.pivot_table(df, index=index, 
    values = [weight_col, ones_col], 
    aggfunc = 'sum').reset_index()
    
    df_pivot.rename(columns = {ones_col:'n',
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
