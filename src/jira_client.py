from jira import JIRA

class JiraClient:
    def __init__(self, server, email, token):
        self.server = server
        self.email = email
        self.token = token
        self.jira = None

    def connect(self):
        try:
            self.jira = JIRA(server=self.server, basic_auth=(self.email, self.token))
            # Test connection by getting current user
            user = self.jira.myself()
            print(f"Connected as: {user['displayName']}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
