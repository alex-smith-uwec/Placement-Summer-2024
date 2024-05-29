
##this file has functions to take Reviewer with SEN and MGPA entered by humans and processing MATHH results
import pandas as pd
import numpy as np
## gpa is overall gradepoint average (capped at 4)
## mgpa is math gpa calculated during transcript review
## mact is math ACT
## mpt is math placement level as determined by mfund, aalg, tag
## sen is assessment of senior year math achievement. Ranges from 0 to 10. Determined during transcript review. SEE RUBRIC!!

def H_none(gpa, mgpa, sen):
    """
    Determines MATHH with no ACT, no MPT. Uses mgpa and sen from transcript review.
    
    Parameters:
    gpa (float): Overall gradepoint average (capped at 4).
    mgpa (float): Math GPA calculated during transcript review.
    sen (int): Assessment of senior year math achievement (0-10).
    
    Returns:
    int: MATHH level.
    """
    cap_gpa=min(gpa,4)
    # agpa = (cap_gpa + mgpa) / 2
    #geometric mean
    agpa = (cap_gpa*mgpa)**0.5

    if sen >= 8:
        if agpa >= 3.5:
            return 7
        elif agpa >= 3.25:
            return 6
        elif agpa >= 3:
            return 5
        elif agpa >= 2.5:
            return 4
        else:
            return 3
    elif sen >= 5 and sen < 8:
        if agpa >= 3.5:
            return 6
        elif agpa >= 3.25:
            return 5
        elif agpa >= 2.5:
            return 4
        else:
            return 3
    elif sen >= 3 and sen < 5:
        if agpa > 3.5:
            return 5
        elif agpa >= 3:
            return 4
        elif agpa >= 2.5:
            return 3
        else:
            return 2
    else:  # sen < 3
        if agpa > 3.5:
            return 4
        elif agpa >= 3:
            return 3
        elif agpa >= 2.5:
            return 2
        else:
            return 1

def H_mpt(gpa, mgpa, mpt, sen):
    """
    Determines MATHH with additional info of MPT only.
    
    Parameters:
    gpa (float): Overall gradepoint average (capped at 4).
    mgpa (float): Math GPA calculated during transcript review.
    mpt (int): Math placement level.
    sen (int): Assessment of senior year math achievement (0-10).
    
    Returns:
    int: MATHH level.
    """
    h0 = H_none(gpa, mgpa, sen)##updated May 29, 2024 with input from Abra

    if mpt <= h0 - 2:
        return h0-1 
    elif mpt <= h0:
        return h0
    elif mpt >= h0 + 4:
        return h0
    else:
        return min(h0 + 1, 7)

def H_mact(gpa, mgpa, mact, sen):
    """
    Determines MATHH with additional info of MACT only.
    
    Parameters:
    gpa (float): Overall gradepoint average (capped at 4).
    mgpa (float): Math GPA calculated during transcript review.
    mact (int): Math ACT score.
    sen (int): Assessment of senior year math achievement (0-10).
    
    Returns:
    int: MATHH level.
    """
    h0 = H_none(gpa, mgpa, sen)

    if h0 >= 4:  
        return h0
    else:
        if mact >= 23:
            return 5 
        elif mact == 22:
            return 4
        elif mact == 21:
            return 3
        elif mact > 16:
            return 2
        else:
            return 1

def H_both(gpa, mgpa, mact, mpt, sen): ##updated May 29, 2024 with input from Abra
    """
    Determines MATHH with additional info of both MACT and unproctored MPT.
    
    Parameters:
    gpa (float): Overall gradepoint average (capped at 4).
    mgpa (float): Math GPA calculated during transcript review.
    mact (int): Math ACT score.
    mpt (int): Math placement level.
    sen (int): Assessment of senior year math achievement (0-10).
    
    Returns:
    int: MATHH level.
    """
    value2 = H_none(gpa, mgpa, sen)
    value3 = H_mpt(gpa, mgpa, mpt, sen)
    value6 = H_mact(gpa, mgpa, mact, sen)
    
    if mpt >= value2 + 3 and value6 <= value2:
        return value2
    
    if mpt >= value2 + 2 and value6 < value2:
        return value2
    
    return max(value2, value3, value6)





def type(review):
    conditions = [
        review['proc_MPT'].notna(),
        review['Expedited'].notna(),
        review['MACT'].isna() & review['unproc_MPT'].isna(),
        review['MACT'].isna() & review['unproc_MPT'].notna(),
        review['MACT'].notna() & review['unproc_MPT'].isna(),
        review['MACT'].notna() & review['unproc_MPT'].notna()
    ]
    choices = [
        'h_proctored',
        'h_expedited',
        'h_none',
        'h_mpt',
        'h_act',
        'h_both'
    ]
    review['Review Type'] = np.select(
        conditions,
        choices,
        default=None
    )
    return review





def mathh(df):
    def apply_logic(row):
        if row['Review Type'] == 'h_proctored':
            return row['proc_MPT']
        elif row['Review Type'] == 'h_expedited':
            return row['Expedited']
        elif row['Review Type'] == 'h_none':
            return H_none(row['GPA'], row['MGPA'], row['SEN'])
        elif row['Review Type'] == 'h_mpt':
            return H_mpt(row['GPA'], row['MGPA'], row['unproc_MPT'], row['SEN'])
        elif row['Review Type'] == 'h_act':
            return H_mact(row['GPA'], row['MGPA'], row['MACT'], row['SEN'])
        elif row['Review Type'] == 'h_both':
            return H_both(row['GPA'], row['MGPA'], row['MACT'], row['unproc_MPT'], row['SEN'])
        else:
            return None

    # Ensure MATHH_date is in datetime format
    df['MATHH_date'] = pd.to_datetime(df['MATHH_date'], errors='coerce')
    
    # Create a copy of the original MATHH column to compare old and new values
    original_mathh = df['MATHH'].copy()

    # Apply logic to update MATHH column
    df['MATHH'] = df.apply(apply_logic, axis=1)
    
    # Get the current date
    current_date = pd.Timestamp.today().normalize()

    # Update MATHH_date based on changes in MATHH values
    for i in df.index:
        if df.at[i, 'MATHH'] != original_mathh.at[i]:
            # If MATHH has changed, update to today's date
            df.at[i, 'MATHH_date'] = current_date

    return df






