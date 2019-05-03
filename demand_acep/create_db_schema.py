""" This file contains functions that create the schema in the database """

from sqlalchemy import *
import pandas as pd
import os

def read_source_files(channel_metadata_file, years_file):
    """ 
    This function reads the source file and extracts the table names and
    corresponding column names.
    
    Parameters
    ----------
    channel_metadata_file : string
        `channel_metadata_file` represents the absolute path of the channel 
        metadata file **including** the filename.
    years_file : string
        `years_file` represents the absolute path of the file containing the 
        years for which the tables should be created for. This file should be a 
        text file with one year per row and the column header "years". 

    Returns
    -------
    list
        A list of containing a dict and a list containing years. The dict 
        has meter names a keys and list of corresponding channels as values.
    """

    # Read in files containing data type
    meter_details = pd.read_excel(channel_metadata_file)
    # Extract channel names
    
    ###########################################################################
    # TODO: Create a metadata file with channel names for every meter 
    # ----------------------------------------------------------------
    # this is hardcoded to read upto line 48, 
    # as the file contains other lines at the end. This should be changed to a 
    # file containing channels per meter, as different meters can have different
    # channels and that file should be a source of truth across applications, 
    # the new database schema is created when this file changes
    ############################################################################
    
    # Additional column name time is added to store the timestamp of measurement
    channel_names = ['time'] + list(meter_details['Channels'][:48])
    # Extract name of meters 
    # TODO: Change this part to remmove the hardcoding
    #  when the metadata files are sorted
    # ---------------------------------------------------------
    meter_names = list(meter_details.columns.values)[-4:]
    
    # Create a dictionary to store the channels per meter. So keys are the meter 
    # names and the values are a list of channel per meter
    meter_channel_dict = {}
    # Loop across the meter_names list to add channels for each meter
    for meter_name in meter_names: 
        meter_channel_dict[meter_name] = channel_names 
        
    # Get years from the years file
    years_df = pd.read_csv(years_file)
    
    data_years = years_df['years'].values.tolist()
    
    return meter_channel_dict, data_years
    
    
def create_schema_from_source_files(sql_engine, channel_metadata_file, years_file):
    """ 
    This function reads the source file and extracts the table names and
    corresponding column names.
    
    Parameters
    ----------
    sql_engine : SQLAlchemy engine
        'sql_engine` should support database operation.
    channel_metadata_file : string
        `channel_metadata_file` represents the absolute path of the channel 
        metadata file **including** the filename.
    years_file : string
        `years_file` represents the absolute path of the file containing the 
        years for which the tables should be created for. This file should be a 
        text file with one year per row and the column header "years". 

    Returns
    -------
    Nothing (can change in future)
    """
    
    meter_channel_dict, data_years = read_source_files(channel_metadata_file, years_file)
    
    # Metadata for the SQLAlchemy tables database - will add tables eventually 
    # This should be connected to the correct database. 
    metadata = MetaData(sql_engine)
    
    for meter in meter_channel_dict:
        # Get the channels for this meter
        meter_channels = meter_channel_dict[meter]
        # Create the following lists for the database insertion 
        # Types of columns - defaulting to float, except for time
        columns_types = [TIMESTAMP] + [Float] * (len(meter_channels) - 1)
        # Primary key flags - defaulting to false, except for time
        primary_key_flags = [True] + [False] * (len(meter_channels) - 1)
        # Nullable flags - defaulting to false, except for time
        nullable_flags = [True] + [False] * (len(meter_channels) - 1)
        # Iterate over the years list 
        for year in data_years: 
            # Create table name from meter name and year 
            table_name = meter + "_" + str(year)
            
            # Dynamically create table names and corresponding column names
            table_name = Table(table_name, metadata,
             *(Column(column_name, column_type,
                      primary_key=primary_key_flag,
                      nullable=nullable_flag)
               for column_name,
                   column_type,
                   primary_key_flag,
                   nullable_flag in zip(meter_channels,
                                        columns_types,
                                        primary_key_flags,
                                        nullable_flags)))
    
    # Create the tables in the metadata - this defaults to checking that 
    # the table names first, so will only create tables if they do not exist
    # making this function idempotent
    metadata.create_all()
    
    return 
