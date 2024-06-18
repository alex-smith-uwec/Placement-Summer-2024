import pandas as pd
import numpy as np

def reviewer(dash):
    # Drop specified columns
    dash = dash.drop(columns=['Primary Name', 'Birthdate', 'Academic Plan 1 (Long Descr)'])
    
    # Rename specified columns
    dash = dash.rename(columns={
        'Admit Plan': 'Plan',
        'Meeting Dt': 'Appt',
        'HS GPA': 'GPA',
        'ACT Reported MATH': 'Official_MACT',
        'Self Reported ACT MATH': 'Self_MACT',
        'Unproctored MFND': 'MFUND',
        'Unproctored AALG': 'AALG',
        'Unproctored TAG': 'TAG',
        'Unproctored Test Dt': 'Unproc_date'
    })
    
    # Add specified columns with default None values
    dash['Expedited'] = None
    dash['SEN'] = None
    dash['MGPA'] = None
    dash['MACT']=None
    dash['unproc_MPT'] = None
    dash['proc_MPT']=None
    dash['MATHH'] = None
    dash['MATHH_date'] = None
    dash['Reviewer Comment'] = None

    
    # Reorder columns
    columns_order = [
        'Emplid', 'Preferred Name', 'Plan', 'Appt', 'Expedited', 'SEN', 'MGPA', 'Reviewer Comment', 'GPA',
        'MACT','Official_MACT', 'Self_MACT', 'SAT Reported MATH', 'Self Reported SAT MATH', 
        'MFUND', 'AALG', 'TAG', 'unproc_MPT', 'Unproc_date', 'WPT MFND', 'WPT AALG', 
        'WPT TAG', 'proc_MPT', 'Holistic Level', 'MATHH', 'MATHH_date','Email','Email Other'
    ]
    
    dash = dash[columns_order]
    
    return dash





def math_act(row):
    """
    Get Math ACT score from available sources: official, self-reported, or converted from Math SAT.

    This function retrieves the Math ACT score from a given row of data. The score is extracted based on the following priority:
    1. Official Math ACT score
    2. Self-reported Math ACT score
    3. Converted Math SAT score (reported)
    4. Converted Math SAT score (self-reported)

    Args:
        row (pd.Series): A row of data containing the following fields:
            - 'Official_MACT': Official Math ACT score
            - 'Self_MACT': Self-reported Math ACT score
            - 'SAT Reported MATH': Reported Math SAT score
            - 'Self Reported SAT MATH': Self-reported Math SAT score

    Returns:
        float: The Math ACT score, either directly from ACT or converted from SAT. Returns np.nan if no score is available.
    """
    # SAT to ACT conversion dictionary
    sat_to_act = {
        800: 36, 790: 35, 780: 35, 770: 35, 760: 34, 750: 33, 740: 33, 730: 32, 720: 32, 
        710: 31, 700: 30, 690: 30, 680: 29, 670: 28, 660: 28, 650: 27, 640: 27, 630: 27, 
        620: 26, 610: 26, 600: 25, 590: 25, 580: 24, 570: 24, 560: 23, 550: 23, 540: 22, 
        530: 21, 520: 20, 510: 19, 500: 18, 490: 18, 480: 17, 470: 17, 460: 17, 450: 16, 
        440: 16, 430: 16, 420: 16, 410: 15, 400: 15, 390: 15, 380: 15, 370: 14, 360: 14, 
        350: 14, 340: 13, 330: 13, 320: 13, 310: 12, 300: 12, 290: 11, 280: 11, 270: 10, 
        260: 10
    }

    if not pd.isna(row['Official_MACT']):
        return row['Official_MACT']
    elif not pd.isna(row['Self_MACT']):
        return row['Self_MACT']
    elif not pd.isna(row['SAT Reported MATH']):
        sat_math = row['SAT Reported MATH']
        return sat_to_act.get(sat_math, np.nan)
    else:
        sat_math = row['Self Reported SAT MATH']
        return sat_to_act.get(sat_math, np.nan)

def act(df):
    """
    Fill in the 'MACT' column using the math_act function.

    Args:
        df (pd.DataFrame): A dataframe containing the columns 
            'Official_MACT', 'Self_MACT', 'SAT Reported MATH', 'Self Reported SAT MATH'.

    Returns:
        pd.DataFrame: The dataframe with the 'MACT' column filled.
    """
    df['MACT'] = df.apply(math_act, axis=1)
    df = df.drop(columns=['Official_MACT', 'Self_MACT', 'SAT Reported MATH', 'Self Reported SAT MATH'])
    return df

##Define a function F_mpt to return math placement level between 1 and 7
def unproc_mpt(mfund, aalg, tag):
    """
    Determines the unproctored math placement level based on math fundamentals score (mfund),
    advanced algebra score (aalg), and tag score (tag). Returns a placement level from 1 to 7.
    
    Parameters:
    mfund (float): Math Fundamentals score (unproctored)
    aalg (float): Advanced Algebra score (unproctored)
    tag (float): Trig score. (unproctored)

    Returns:
    float: The unproctored math placement level, or NaN if mfund is not a number.
    """
    if np.isnan(mfund):
        return np.nan
    if mfund < 355:
        return 1
    elif mfund < 465 and aalg < 455:
        return 2
    elif mfund < 465:
        return 3
    elif aalg < 400:
        return 4
    elif aalg < 555:
        return 5
    elif aalg < 575:
        return 6
    elif aalg>575 and tag<555:
       return 6
    else:
        return 7

def proc_mpt(mfund, aalg, tag):
    """
    Determines the math placement level based on  proctored math fundamentals score (WPT MFND),
    advanced algebra score (WPT AALG), and tag score (WPT TAG). Returns a placement level from 1 to 7.
    
    Parameters:
    WPT MFND (float): Math Fundamentals score (proctored)
    WPT AALG (float): Advanced Algebra score (proctored)
    WPT TAG (float): Trig score (proctored)

    Returns:
    float: The proctored math placement level, or NaN if WPT MFUND is not a number.
    """
    if np.isnan(mfund):
        return np.nan
    if mfund < 355:
        return 1
    elif mfund < 465 and aalg < 455:
        return 2
    elif mfund < 465:
        return 3
    elif aalg < 400:
        return 4
    elif aalg < 555:
        return 5
    elif aalg < 575:
        return 6
    elif aalg>575 and tag<555:
       return 6
    else:
        return 7

def reviewer_with_mpt(df):
    """
    Fill in the 'unproc_MPT' and 'proc_MPT' columns using the unproc_mpt and proc_mpt functions, respectively.

    Args:
        df (pd.DataFrame): A dataframe containing the columns 'MFUND', 'AALG', 'TAG' for unproc_MPT,
                           and 'WPT MFND', 'WPT AALG', 'WPT TAG' for proc_MPT.

    Returns:
        pd.DataFrame: The dataframe with the 'unproc_MPT' and 'proc_MPT' columns filled.
    """
    df['unproc_MPT'] = df.apply(lambda row: unproc_mpt(row['MFUND'], row['AALG'], row['TAG']), axis=1)
    df['proc_MPT'] = df.apply(lambda row: proc_mpt(row['WPT MFND'], row['WPT AALG'], row['WPT TAG']), axis=1)
    return df


def expedite(reviewer, admit_plans):
    # Create a dictionary from the admit_plans dataframe for lookup
    admit_plan_dict = admit_plans.set_index('Admit Plan')['expedite (if conditions met)'].to_dict()
    
    def get_expedited_value(row):
        # First stage of logic
        if pd.notna(row['WPT MFND']):
            return row['proc_MPT']
        elif pd.isna(row['MACT']) and row['MFUND'] <= 355:
            return 1
        elif pd.isna(row['MACT']) and 356 <= row['MFUND'] <= 465 and row['AALG'] < 455 and row['GPA'] < 3:
            return 2
        elif row['MACT'] <= 15:  
            return 1
        elif row['MACT'] <= 19 and row['GPA'] < 3:   
            return 2
        # Second stage of logic
        elif 24 <= row['MACT'] <= 27 and admit_plan_dict.get(row['Plan'], 0) == 1:
            return 5
        elif 28 <= row['MACT'] <= 31 and admit_plan_dict.get(row['Plan'], 0) == 1:
            return 6
        # Third stage of logic
        elif row['MACT'] >= 32 and row['GPA'] >= 3:
            return 7
        else:
            return None
    
    # Apply the logic to each row in the reviewer dataframe
    reviewer['Expedited'] = reviewer.apply(get_expedited_value, axis=1)
    
    return reviewer








def SEN_MGPA(reviewer, transcript_records):
    # Ensure 'Emplid' is of the same type in both dataframes
    reviewer['Emplid'] = reviewer['Emplid'].astype(str)
    transcript_records['Emplid'] = transcript_records['Emplid'].astype(str)

    # Merge the reviewer dataframe with transcript_records on 'Emplid'
    merged_df = reviewer.merge(transcript_records[['Emplid', 'SEN', 'MGPA','MATHH','MATHH_date','Reviewer Comment']], on='Emplid', how='left', suffixes=('', '_transcript'))

    # Ensure that the combined columns are processed correctly by filling NaN values explicitly
    merged_df['SEN'] = merged_df['SEN'].fillna(merged_df['SEN_transcript'])
    merged_df['MGPA'] = merged_df['MGPA'].fillna(merged_df['MGPA_transcript'])
    merged_df['MATHH'] = merged_df['MATHH'].fillna(merged_df['MATHH_transcript'])
    merged_df['MATHH_date'] = merged_df['MATHH_date'].fillna(merged_df['MATHH_date_transcript'])
    merged_df['Reviewer Comment'] = merged_df['Reviewer Comment'].fillna(merged_df['Reviewer Comment_transcript'])
    
    # Drop the temporary '_transcript' columns
    merged_df = merged_df.drop(columns=['SEN_transcript', 'MGPA_transcript','MATHH_transcript','MATHH_date_transcript','Reviewer Comment_transcript'])
    
    return merged_df


