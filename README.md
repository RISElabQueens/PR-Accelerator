# PR-Accelerator


PR-Accelerator is a set of tools that reports analytics and information regarding pull requests (PRs) and points out the delays in first response. This tool was presented in our paper titled Understanding the Time to First Response In GitHub Pull Requests published at the MSR 2023 conference.

# Update
- May, 2023: Introduced first two tools (PR data extractor & PR initial interaction analytics report) of PR-Accelerator.

# Features

For each pull requests, the tool reports the following information:

- html_url: The URL of the pull request.
- author: The author of the pull request.
- status: The status of the pull request.
- time_to_close/merge[hour]	: The time to close/merge the pull request in hours.
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

1. To run *PR-Accelerator* you need to provide a *GitHub personal access token* (API key). You can follow the instructions [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) to obtain such a token.

2. Install the python packages listed in the requirements.txt:
```
pip install -r requirements.txt
```
3. Run the following command
```
git clone https://github.com/RISElabQueens/PR-Accelerator.git
```
4. To get pull request data run the following command
```
python3 pr_getdata.py enddate owner repo github_token 
```
> Example: python3 pr_getdata.py 2023-04-30 huggingface transformers xxxxx

5. Run the following command:
```
python3 pr_initial_interaction_analytics.py -output "pr_summary.csv"
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
