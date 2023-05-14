import json
import csv
import time
import sys
from datetime import datetime, timedelta

import requests_cache

csv_headers = ['author', 'html_url', 'status', 'time_to_close/merge[hour]', 'title', 'created_at', 'published_at', 'merged_at',
               'closed_at', 'approved_by', 'comment_by', 'review_by', 'requested_reviewers']

csv_headers_comments = ['html_url', 'content', 'created_at', 'comment_by', 'pull_request_url',
                        'time_from_publish[hour]', 'time_from_open[hour]', 'time_to_close/merge[hour]']

csv_headers_reviews = ['html_url', 'type', 'pull_request_url',
                       'content', 'created_at', 'updated_at', 'review_by']


def get_next_url(response):
    links = response.headers.get('Link', '')
    links_segments = links.split(',')
    next_api_url = None
    for segment in links_segments:
        if 'rel="next"' in segment:
            left_index = segment.find('<')
            right_index = segment.find('>')
            if left_index != -1 and right_index != -1:
                next_api_url = segment[left_index + 1: right_index]
                break
    return next_api_url


def main(end_date_str, num_days, owner, repo, token):
    session = requests_cache.CachedSession('cached_requests',
                                           allowable_methods=['GET', 'POST'],
                                           expire_after=3600 * 48)

    # end_date = datetime.now().strftime("%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    start_date_str = (end_date - timedelta(days=num_days)).strftime("%Y-%m-%d")

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
        "include": "true"
    }
    page_size = 20

    pr_list = []
    comment_list = []
    review_list = []

    # set the user and repository name
    # owner = "huggingface"
    # repo = "transformers"
    # org:{owner}
    # repo:{owner}/{repo}
    api_url = f"https://api.github.com/search/issues?q=type:pr+repo:{owner}/{repo}+created:{start_date_str}..{end_date_str}&per_page={page_size}&page=1"
    while True:
        print(api_url)
        response = session.get(api_url, headers=headers)
        if not response.from_cache:
            time.sleep(10)

        if response.status_code == 200:
            prs = response.json()['items']
            for pr in prs:
                if pr.get('draft') is True:
                    continue

                pr_list.append(pr)
            next_api_url = get_next_url(response)
            if next_api_url is None:
                break
            else:
                api_url = next_api_url
        else:
            print(f"Error: {response.text}")

    for pr in pr_list:
        comment_by = []
        review_by = []
        approved_by = []
        while True:
            pr_url = pr['url'].replace('issue', 'pull')
            print(pr_url)
            response = session.get(pr_url, headers=headers)
            if not response.from_cache:
                time.sleep(10)
            if response.status_code == 200:
                pr_data = response.json()
                pr['merged_at'] = pr_data.get('merged_at')
                pr['author'] = pr_data['user']['login']
                break

        review_url = pr['url'].replace('issue', 'pull') + '/reviews'
        while True:
            print(review_url)
            response = session.get(review_url, headers=headers)
            if not response.from_cache:
                time.sleep(10)

            if response.status_code == 200:
                reviews = response.json()
                for review in reviews:
                    if review['state'] == 'APPROVED':
                        approved_by.append(review['user']['login'])

                    review['review_by'] = review['user']['login']
                    review['content'] = review['body']
                    review['type'] = "ReviewComment"
                    review['created_at'] = review['submitted_at']
                    review['updated_at'] = None
                    review_list.append(review)

                    if review['review_by'] != pr['author']:
                        # only consider non-author
                        review_by.append(review['review_by'])

                next_api_url = get_next_url(response)
                if next_api_url is None:
                    break
                else:
                    review_url = next_api_url

        ready_for_review_time = None
        requested_reviewers = []
        events_url = pr['url'] + '/events'
        while True:
            print(events_url)
            response = session.get(events_url, headers=headers)
            if not response.from_cache:
                time.sleep(10)

            if response.status_code == 200:
                events = response.json()
                for event in events:
                    if event["event"] == "ready_for_review":
                        ready_for_review_time = event['created_at']
                    elif event["event"] == "review_requested":
                        if 'requested_reviewer' in event:
                            reviewer = event['requested_reviewer']['login']
                            if reviewer not in requested_reviewers:
                                requested_reviewers.append(reviewer)
                        elif 'requested_team' in event:
                            reviewer = event['requested_team']['name']
                            if reviewer not in requested_reviewers:
                                requested_reviewers.append(reviewer)
                        else:
                            print(f"requested_reviewer event doesn't have user id")
                next_api_url = get_next_url(response)
                if next_api_url is None:
                    break
                else:
                    events_url = next_api_url
        if ready_for_review_time is None:
            publish_time = pr['created_at']
        else:
            publish_time = ready_for_review_time

        pr['approved_by'] = approved_by
        pr['published_at'] = publish_time
        pr['requested_reviewers'] = requested_reviewers

        publish_time = datetime.strptime(
            pr['published_at'], "%Y-%m-%dT%H:%M:%SZ")

        if pr['merged_at'] is not None:
            pr['status'] = "MERGED"
            merge_time = datetime.strptime(
                pr['merged_at'], "%Y-%m-%dT%H:%M:%SZ")
            pr['time_to_close/merge[hour]'] = round(
                (merge_time - publish_time).total_seconds() / 3600.0, 1)
        elif pr['closed_at'] is not None:
            if pr['state'] == "open":
                # ignore reopen prs
                break
            else:
                pr['status'] = "CLOSED"
            close_time = datetime.strptime(
                pr['closed_at'], "%Y-%m-%dT%H:%M:%SZ")
            pr['time_to_close/merge[hour]'] = round(
                (close_time - publish_time).total_seconds() / 3600.0, 1)
        else:
            pr['status'] = 'OPEN'
            pr['time_to_close/merge[hour]'] = round(
                (datetime.now() - publish_time).total_seconds() / 3600.0, 1)

        review_comment_url = pr['url'].replace('issue', 'pull') + '/comments'
        while True:
            print(review_comment_url)
            response = session.get(review_comment_url, headers=headers)
            if not response.from_cache:
                time.sleep(10)

            if response.status_code == 200:
                reviews = response.json()
                for review in reviews:
                    review['review_by'] = review['user']['login']
                    review['type'] = "Review"
                    review['content'] = review['body']
                    review_list.append(review)
                    if review['review_by'] != pr['author']:
                        # only consider non-author
                        review_by.append(review['review_by'])

                next_api_url = get_next_url(response)
                if next_api_url is None:
                    break
                else:
                    review_comment_url = next_api_url

        pr['review_by'] = review_by
        comments_url = pr['url'] + '/comments'
        while True:
            print(comments_url)
            response = session.get(comments_url, headers=headers)
            if not response.from_cache:
                time.sleep(10)

            if response.status_code == 200:
                comments = response.json()

                for comment in comments:
                    if len(comment['body'].strip()) <= 2:
                        print(f"Skip comment: {comment['body']}")
                        continue

                    comment['content'] = comment['body'].strip()
                    comment['comment_by'] = comment['user']['login']
                    comment_publish_time = datetime.strptime(
                        comment['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                    open_time = datetime.strptime(
                        pr['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                    comment['time_from_publish[hour]'] = round(
                        (comment_publish_time - publish_time).total_seconds() / 3600.0, 1)
                    comment['time_from_open[hour]'] = round(
                        (comment_publish_time - open_time).total_seconds() / 3600.0, 1)
                    if pr['status'] == 'OPEN':
                        comment['time_to_close/merge[hour]'] = round(
                            (datetime.now() - comment_publish_time).total_seconds() / 3600.0, 1)
                    elif pr['status'] == 'MERGED':
                        merge_time = datetime.strptime(
                            pr['merged_at'], "%Y-%m-%dT%H:%M:%SZ")
                        comment['time_to_close/merge[hour]'] = round(
                            (merge_time - comment_publish_time).total_seconds() / 3600.0, 1)
                    else:
                        close_time = datetime.strptime(
                            pr['closed_at'], "%Y-%m-%dT%H:%M:%SZ")
                        comment['time_to_close/merge[hour]'] = round(
                            (close_time - comment_publish_time).total_seconds() / 3600.0, 1)

                    comment_list.append(comment)
                    if comment['comment_by'] != pr['author']:
                        # only consider non-author
                        comment_by.append(comment['comment_by'])

                next_api_url = get_next_url(response)
                if next_api_url is None:
                    break
                else:
                    comments_url = next_api_url
        pr['comment_by'] = comment_by

    with open(f'pr_summary_{end_date_str}.csv', 'w', encoding='utf-8') as fout:
        csv_writer = csv.writer(fout)
        csv_writer.writerow(csv_headers)
        for pr in pr_list:
            row = pr_to_row(pr)
            csv_writer.writerow(row)

    with open(f'pr_comments_{end_date_str}.csv', 'w', encoding='utf-8') as fout:
        csv_writer = csv.writer(fout)
        csv_writer.writerow(csv_headers_comments)
        for comment in comment_list:
            comment['pull_request_url'] = comment['html_url'].split('#')[0]
            row = comment_to_row(comment)
            csv_writer.writerow(row)

    with open(f'pr_reviews_{end_date_str}.csv', 'w', encoding='utf-8') as fout:
        csv_writer = csv.writer(fout)
        csv_writer.writerow(csv_headers_reviews)
        for review in review_list:
            row = review_to_row(review)
            csv_writer.writerow(row)


def review_to_row(review):
    return [
        review['html_url'],
        review['type'],
        review['pull_request_url'],
        review['content'],
        review['created_at'],
        review['updated_at'],
        review['review_by'],
    ]


def comment_to_row(comment):
    return [
        comment['html_url'],
        comment['content'],
        comment['created_at'],
        comment['comment_by'],
        comment['pull_request_url'],
        comment['time_from_publish[hour]'],
        comment['time_from_open[hour]'],
        comment['time_to_close/merge[hour]'],
    ]


def pr_to_row(pr):
    return [
        pr['author'],
        pr['html_url'],
        pr['status'],
        pr['time_to_close/merge[hour]'],
        pr['title'],
        pr['created_at'],
        pr['published_at'],
        pr['merged_at'],
        pr['closed_at'],
        json.dumps(pr['approved_by']),
        json.dumps(pr['comment_by']),
        json.dumps(pr['review_by']),
        json.dumps(pr['requested_reviewers']),
    ]


if __name__ == '__main__':
    arg_end_date_str = sys.argv[1]
    arg_num_days = int(sys.argv[2])
    arg_owner = sys.argv[3]
    arg_repo = sys.argv[4]
    arg_token = sys.argv[5]

    main(arg_end_date_str, arg_num_days, arg_owner, arg_repo, arg_token)
