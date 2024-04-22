class Bug:
    def __init__(
        self, fixing_commit: str, introducing_commits: list[str], scope: list[str]
    ) -> None:
        self.fixing_commit: str = fixing_commit
        self.introducing_commits: list[str] = introducing_commits
        self.scope: list[str] = scope
