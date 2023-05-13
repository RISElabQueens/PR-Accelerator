import pandas as pd
import numpy as np
import argparse


def pr_first_response_summary():
    pr_comments = pd.read_csv("")  # put the path of pr_comments data here
    pr_reviews = pd.read_csv("")  # put the path of pr_reviews data here
    pr_summary = pd.read_csv("")  # put the path of pr_summary data here

    # First, ensure 'created_at' is a datetime object for correct sorting
    pr_comments['created_at'] = pd.to_datetime(pr_comments['created_at'])

    # Make sure 'pull_request_url' is the index in pr_summary for the upcoming merge operation
    pr_summary.set_index('html_url', inplace=True)

    # Join pr_comment with pr_summary on 'pull_request_url' to get 'author' in pr_comment
    pr_comment = pr_comments.merge(
        pr_summary[['author']], how='left', left_on='pull_request_url', right_index=True)

    # Filter out rows where 'author' is same as 'comment_by'
    pr_comment = pr_comment[pr_comment['author'] != pr_comment['comment_by']]

    # Now, sort the dataframe based on 'created_at' and then group by 'pull_request_url'
    grouped = pr_comment.sort_values('created_at').groupby('pull_request_url')

    # Get the first and second 'time_from_open[hour]' for each group
    time_to_first_comment = grouped['time_from_open[hour]'].nth(
        0)  # first non-author comment
    time_to_second_comment = grouped['time_from_open[hour]'].nth(1)

    # Now join these series to the pr_summary dataframe
    pr_summary['time_to_first_response[hour]'] = time_to_first_comment
    pr_summary['time_to_second_response[hour]'] = time_to_second_comment

    # If you want to reset the index back to a range index
    pr_summary.reset_index(inplace=True)
    oneday = 24
    oneweek = 7 * oneday
    onemonth = 30 * oneday

    # right : (bool, default True )  Indicates whether bins includes the rightmost edge or not. If right == True (the default), then the bins [1, 2, 3, 4] indicate (1,2], (2,3], (3,4].
    pr_summary['first_response_period'] = pd.cut(pr_summary['time_to_first_response[hour]'], [0, oneday, oneweek, onemonth, np.inf],
                                                 labels=[
                                                     'within 1 day', '1 day to 1 week', '1 week to 1 month', 'more than 1 month'],
                                                 include_lowest=True)
    pr_summary['after_first_response_period'] = pd.cut(pr_summary['time_to_close/merge[hour]'], [0, oneday, oneweek, onemonth, np.inf],
                                                       labels=[
                                                           'within 1 day', '1 day to 1 week', '1 week to 1 month', 'more than 1 month'],
                                                       include_lowest=True)

    # bot list
    bot_list = ['akka-ci', 'lightbend-cla-validator', 'typesafehub-validator', 'ansibot', 'dependabot', 'ansible-zuul,' 'azure-pipelines',
                'github-actions', 'dependabot', 'asfbot', 'travis-ci',
                'CLAassistant', 'discoursebot', 'dependabot-preview',
                'dependabot',  'discourse-translator-bot', 'lgtm-com'
                'discoursedangerbot', 'github-pages',
                'dependabot',  'jira', 'pr-milestone-check', 'dependabot-preview',
                'npm-cli-bot', 'npm-robot', 'nodejs-github-bot',
                'codetriage-readme-bot', 'C3POdoo', 'fw-bot', 'robodoo', 'rails-bot', 'travisbot',
                'welcome', 'saltstack-bot', 'stale',
                'codecov', 'wip', 'k8s-github-robot', 'k8s-ci-robot', 'fejta-bot',
                'k8s-reviewable', 'k8s-cherrypick-bots', 'googlebot', 'k8s-triage-robot',
                'linux-foundation-easycla',
                'k8s-bot', 'HuggingFaceDocBuilderDev', 'HuggingFaceDocBuilderDev'
                ]
    # Sort the dataframe based on 'created_at' and then group by 'pull_request_url'
    grouped = pr_comment.sort_values('created_at').groupby('pull_request_url')
    first_comment_by = grouped['comment_by'].first()
    
    # Identify whether the first comment for each pull request is made by a bot
    bot_first = first_comment_by.isin(bot_list)
    pr_summary.set_index('html_url', inplace=True)
    pr_summary['bot_first'] = bot_first
    pr_summary.reset_index(inplace=True)
    return pr_summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-output', type=str, help='Output file name')
    args = parser.parse_args()

    pr_summary = pr_first_response_summary()

    # Save the pr_summary dataframe to the specified output file
    pr_summary.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
