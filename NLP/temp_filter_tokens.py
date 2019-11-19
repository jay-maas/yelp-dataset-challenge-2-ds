"""
Temporary Tokenization Fixer for Reference.

Goal:  Scan tokens in the token column of a dataframe
        Create a subset df with review_id and tokens.
        Save data to S3.
        Generate POST jobs for saved data
"""

import logging
import os

from jobs import get_jobs, pop_current_job, read_job,\
     download_data, delete_local_file, delete_s3_file, load_data

###Logging###
log_path = os.path.join(os.getcwd(), 'debug.log')
logging.basicConfig(filename=log_path, level=logging.INFO)


###INSERT CLEANING/PROCESSING FUNCTION HERE###


if __name__ == "__main__":
    main_logger = logging.getLogger(__name__+" Token Fixer")

    num_jobs = len(get_jobs('retoken')) # No module creates retoken jobs.  Manually create these.

    for i in range(num_jobs):
        # Get a job and read out the datapath
        current_job = pop_current_job()
        asset = read_job(current_job)['Key']

        main_logger.info('Running job {}.  Read file {}'.format(current_job, asset))

        # Load the data
        datapath = download_data(asset)
        data = load_data(datapath)


        ###INSERT TOKEN CLEANING FUNCTION HERE###


        # Cleanup
        delete_local_file(datapath)
        delete_s3_file(current_job)
        main_logger.info("Deleted Job: {}".format(current_job))