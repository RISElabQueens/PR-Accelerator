# PR-Accelerator

PR-Accelerator is a set of tools that reports analytics and information regarding pull requests (PRs) and points out the delays in first response. This tool was presented in our paper titled [Understanding the Time to First Response In GitHub Pull Requests](https://arxiv.org/abs/2304.08426) published at the [MSR 2023](https://conf.researchr.org/home/msr-2023) conference.

# Tools:

- PR data extractor: It extracts all information about a repository and saves them in three different csv files (pr_comment_enddate.csv, pr_review_enddate.csv and pr_summary_enddate.csv)
- PR first response summary: It reports the analytics about first resposne of a pull request and saves it in a separate csv file (pr_summary.csv)

# Update

- May, 2023: Introduced first two tools (PR data extractor & PR first response summary report) of PR-Accelerator.

# Features

For each pull requests, PR initial interaction analytics tool reports the following information:

- html_url: The URL of the pull request.
- author: The author of the pull request.
- status: The status of the pull request.
- time_to_close/merge[hour] : The time to close/merge the pull request in hours.
- title: The title of the pull request
- created_at: Pull request creation date
- published_at: Pull request publish date
- merged_at: Pull request merge date
- closed_at: Pull request closed date
- approved_by: The person who approved the pull request
- comment_by: Bots/persons who commented on the pull request
- review_by: The reviewer who reviewed the pull request
- requested_reviewers: The requested reviewer information of pull request
- time_to_first_response[hour]: The time to receive the first response in hours
- time_to_second_response[hour]: The time to receive the second response in hours
- first_response_period: First response in time wise categorization form.
- after_first_response_period: Time after the first response in time wise categorization form.
- bot_first: True if the bot is the first responder of the pull request.

# Usage

1. To run _PR-Accelerator_ you need to provide a _GitHub personal access token_ (API key). You can follow the instructions [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) to obtain such a token.



2. Run the following command to clone the repository:

```
git clone https://github.com/RISElabQueens/PR-Accelerator.git
```

3. Install the python packages listed in the requirements.txt:

```
pip install -r requirements.txt
```

4. To get pull request data run the following command

```
python3 pr_getdata.py end_date num_days owner repo github_token
```

> **Example**: python3 pr_getdata.py 2023-04-30 7 huggingface transformers xxxxx
**Explanation:** This would fetch pull request data from the "transformers" repository owned by "huggingface" for pull requests created in the last 7 days and including 2023-04-30 using github_token xxxx.

Note: The above command will generate three csv files (pr_comment_enddate.csv, pr_review_enddate.csv and pr_summary_enddate.csv). You need to provide the path of these csv files in pr_initial_interaction_analytics.py file.

5. To get the initial analytics of a PR run the following command:

```
python3 pr_initial_interaction_analytics.py -output "pr_initial_analytics.csv"
```

## Citation

If you use this tool in your research, please cite our paper:

```
@inproceedings{PR-Accelerator,
   title={Understanding the Time to First Response In GitHub Pull Requests},
   author={Kazi Amit Hasan , Marcos Macedo, Yuan Tian, Bram Adams, Steven Ding},
   booktitle={Proceedings of the MSR 2023 conference},
   year={2023}
}
```
