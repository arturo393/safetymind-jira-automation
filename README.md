# Jira Automation Project

This project automates the creation of reports from Jira data.

## Features
- Connects to Jira API to fetch issues from Projects, Boards, or Epics.
- Generates reports in various formats (PDF, Excel, Console).
- Scheduled execution.

## Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd jira-automation
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    - Copy `.env.example` to `.env`.
    - Fill in your Jira URL, Email, and API Token.

## Usage

```bash
python src/main.py
```
