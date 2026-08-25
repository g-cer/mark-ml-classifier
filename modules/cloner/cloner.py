"""Clone a list of GitHub repositories from a CSV and persist the outcome of each attempt.

Given an input file, the component performs shallow clones (depth=1) into a target directory,
executes operations concurrently via a thread pool, and records successes in cloned_log.csv
and failures in errors.csv with sanitized messages.

It automatically skips repositories already listed as cloned, ensuring idempotent runs.
Paths (input/output/logs), the maximum number of repositories to process, and the degree of
parallelism are configurable at instantiation.

The goal is to provide a reusable, traceable acquisition step that cleanly separates configuration
from execution and produces reproducible logs debugging."""

import os
from pathlib import Path
import concurrent.futures
from threading import Lock

import git
import pandas as pd
from git import Repo

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class RepoCloner:
    """Handles cloning of GitHub repositories and logs the results or errors."""

    def __init__(self, input_path, output_path, n_repos=5, log_dir=Path("./modules/cloner/log")):
        self.input_path = input_path
        self.output_path = output_path
        self.n_repos = n_repos
        self.writer_lock = Lock()
        # The log directory holds generated CSVs only, so it is not versioned:
        # create it on demand so a freshly cloned repository can run as-is.
        os.makedirs(log_dir, exist_ok=True)
        self.cloned_log_path = os.path.join(log_dir, 'cloned_log.csv')
        self.error_log_path = os.path.join(log_dir, 'errors.csv')

    def _clone_repo(self, row):
        """Clone a single GitHub repository and log results."""
        repo_full_name = row["ProjectName"]
        repo_url = f'https://github.com/{repo_full_name}.git'
        dest_path = os.path.join(self.output_path, repo_full_name)

        try:
            logger.info("Cloning %s", repo_full_name)
            Repo.clone_from(repo_url, str(dest_path), depth=1)
            logger.info("Cloned %s", repo_full_name)
        except git.exc.GitError as e:
            logger.error("Error cloning %s", repo_full_name)
            with self.writer_lock:
                with open(self.error_log_path, 'a', encoding='utf-8') as error_log:
                    error = str(e).replace("'", "").replace("\n", "")
                    error_log.write(f"{repo_full_name},{repo_url},'{error}'\n")
            return

        with self.writer_lock:
            try:
                cloned_log = pd.read_csv(self.cloned_log_path)
                cloned_log = pd.concat([cloned_log, pd.DataFrame([row])], ignore_index=True)
                cloned_log.to_csv(self.cloned_log_path, index=False)
            except Exception as e:
                logger.error("Error saving log for %s: %s", repo_full_name, e)

    def load_repos_to_clone(self):
        """Load repository list from CSV and exclude already cloned ones."""
        df = pd.read_csv(self.input_path, delimiter=",")
        df = df.head(self.n_repos)

        if os.path.exists(self.cloned_log_path):
            cloned_log = pd.read_csv(self.cloned_log_path)
            df = df[~df['ProjectName'].isin(cloned_log['ProjectName'])]
        else:
            pd.DataFrame(columns=['ProjectName', 'repo_url', 'ml_libs', 'count']).to_csv(
                self.cloned_log_path,
                index=False
            )
        return df

    def clone_all(self, max_workers=None):
        """Clone all repositories concurrently and log the results."""
        df = self.load_repos_to_clone()
        logger.info("To analyze: %d repositories", len(df))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self._clone_repo, row) for _, row in df.iterrows()]
            for _ in concurrent.futures.as_completed(futures):
                pass
