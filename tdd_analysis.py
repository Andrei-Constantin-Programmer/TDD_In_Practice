#!/usr/bin/env python

import argparse
import asyncio
from datetime import datetime
import logging
import sys
from src.infrastructure import configuration, repository_utils
from src.models.CSharpFileHandler import CSharpFileHandler
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
        "--batch_size",
        type=int,
        default = 8,
        help="Batch size for asynchronous repository retrieval using PyDriller."
    )
    parser.add_argument(
        "--force_mine",
        action="store_true",
        help="Forcefully mine the repository/repositories, even if they have already been retrieved."
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
    
    if args.batch_size < 1:
        raise argparse.ArgumentError(None, "--batch_size cannot be lower than 1.")
    elif args.batch_size > 16:
        response = input(f"Warning: --batch_size ({args.batch_size}) is greater than 16. Are you sure you want to continue? (Y/N): ").strip().lower()
        while response not in {'y', 'n', 'yes', 'no'}:
            response = input("Invalid input. Please enter 'yes'/'y' or 'no'/'n': ").strip().lower()
        if response in {'no', 'n'}:
            raise argparse.ArgumentError(None, "Operation aborted by the user.")

    return args

def _get_handler(language):
    match language.lower():
        case "java":
            return JavaFileHandler()
        case "c#" | "csharp":
            return CSharpFileHandler()
        case _:
            raise ValueError(f"No file handler found for language {language}")
        
def _get_handlers(languages):
    return [_get_handler(language) for language in languages]

async def _process_single_repo(args, analysis: Analysis):
    repo = repository_utils.repo_from_url(args.repository)
    await analysis.perform_analysis_on_repo(repo, _get_handler(args.language), args.force_mine)

async def _process_all_repos(args, analysis: Analysis):
    if (args.language is not None):
        handlers = [_get_handler(args.language)]
    elif (args.languages is not None):
        handlers = _get_handlers(args.languages)
    else:
        handlers = _get_handlers(DEFAULT_LANGUAGES)

    await analysis.perform_analysis(handlers, args.batch_size, args.force_mine)

async def main():
    try:
        configuration.setup_directories()
        configuration.setup_logging()

        args = _get_parameters()

        if args.verbose:
            logging.notify(f"Parameters:\n  Date: {args.date}\n  Language: {args.language}\n  Languages: {args.languages}\n  Repo: {args.repository}\n")

        logging.notify(f"Running analysis for {args.date}...")

        analysis = Analysis(args.date)

        if args.repository is not None:
            await _process_single_repo(args, analysis)
        else:
            await _process_all_repos(args, analysis)

        end_message = "Analysis complete."
        print(end_message)
        logging.notify(end_message)

    except Exception as e:
        logging.exception(e)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())