#!/usr/bin/env python

import argparse
import asyncio
import logging
import sys
from src.mining.repository_finder import RepositoryFinder

def _get_parameters():
    parser = argparse.ArgumentParser(
        description="Find repositories on GitHub.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--github_token",
        required=True,
        type=str,
        help="Personal GitHub token. For information on how to create one, visit: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token"
    )
    parser.add_argument(
        "--language",
        required=True,
        type=str,
        help="Programming language to find repositories for.",
    )
    parser.add_argument(
        "--organisation",
        "--org",
        type=str,
        default=RepositoryFinder.APACHE_ORGANISATION,
        help="Organisation to find repositories for."
    )
    parser.add_argument(
        "--pagination",
        type=int,
        default = 100,
        help="Pagination for retrieving repositories."
    )
    parser.add_argument(
        "--maximum",
        "--max",
        type=int,
        help="Maximum number of repositories to find."
    )

    args = parser.parse_args()

    if args.pagination < 1:
        raise argparse.ArgumentError(None, "--pagination cannot be lower than 1.")
    if args.maximum is not None and args.maximum < 1:
        raise argparse.ArgumentError(None, "--maximum cannot be lower than 1.")
    
    return args

async def main():
    try:
        args = _get_parameters()

        repository_finder = RepositoryFinder(args.github_token)
        repository_finder.extract_repositories(args.organisation.lower(), args.pagination, args.language.lower(), args.maximum)

        print("Repository find complete.")

    except Exception as e:
        logging.exception(e)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())