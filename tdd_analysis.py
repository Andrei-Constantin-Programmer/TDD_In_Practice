#!/usr/bin/env python

import argparse
import asyncio
from datetime import datetime
import sys
from src.infrastructure import configuration, repository_utils
from src.models.JavaFileHandler import JavaFileHandler
from src.presentation.analysis import Analysis

DEFAULT_EXPERIMENT_DATE = datetime(2024, 12, 1, 0, 0, 0)
DEFAULT_LANGUAGES = ["Java"]

def _get_parameters():
    parser = argparse.ArgumentParser(
        description="Analyse usage of TDD in repositories.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    default_experiment_date_string = DEFAULT_EXPERIMENT_DATE.strftime("%Y-%m-%d")
    parser.add_argument(
        "--date",
        type=str,
        default=default_experiment_date_string,
        help="Date of the experiment in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Single programming language to analyse.",
    )
    parser.add_argument(
        "--languages",
        type=str,
        nargs="*",
        default=["Java"],
        help="List of programming languages to analyze. NOTE: If the '--language' argument is provided, this list is ignored.",
    )
    parser.add_argument(
        "--repository",
        "--repo",
        type=str,
        default=None,
        help="Repository URL to analyse. NOTE: The '--language' argument must be provided in conjunction with this parameter.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output for debugging or detailed logs.",
    )

    args = parser.parse_args()

    try:
        args.date = datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")
    
    if args.repository and not args.language:
        raise argparse.ArgumentError(None, "--repository requires the --language argument to be provided.")

    return args

def _get_handler(language):
    match language.lower():
        case "java":
            return JavaFileHandler()
        case _:
            raise ValueError(f"No file handler found for language {language}")
        
def _get_handlers(languages):
    return [_get_handler(language) for language in languages]

def _process_single_repo(repo, language, analysis):
    repo = repository_utils.repo_from_url(repo)
    analysis.process_repo(repo, _get_handler(language))

async def _process_all_repos(language, languages, analysis):
    if (language is not None):
        handlers = [_get_handler(language)]
    elif (languages is not None):
        handlers = _get_handlers(languages)
    else:
        handlers = _get_handlers(DEFAULT_LANGUAGES)

    await analysis.perform_analysis(handlers)

async def main():
    try:
        configuration.setup_logging()
        configuration.setup_directories()

        args = _get_parameters()

        if args.verbose:
            print(f"Parameters:\n  Date: {args.date}\n  Language: {args.language}\n  Languages: {args.languages}\n  Repo: {args.repository}\n")

        print(f"Running analysis for {args.date}...")

        analysis = Analysis(args.date)

        if args.repository is not None:
            _process_single_repo(args.repository, args.language, analysis)
        else:
            await _process_all_repos(args.language, args.languages, analysis)

        print("Analysis complete.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())