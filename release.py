#!/usr/bin/env ../../env/bin/python

import sys
import os
import argparse
import semantic_version
import git


def main():
    parser = get_args_parser()
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    version = None
    app_name = os.path.basename(os.getcwd())
    with open(f'{app_name}/__init__.py', encoding = 'utf-8') as f:
        for line in f.readlines():
            version = semantic_version.Version(
                line
                    .replace('__version__ = ', '')
                    .replace('\n', '')
                    .replace('\'','')
            )

    release = None
    if args.major:
        release = version.next_major()
    elif args.minor:
        release = version.next_minor()
    elif args.patch:
        release = version.next_patch()

    if release:
        print(f'Bumping from {version} to {release}')
        if not args.dry_run:
            print('Writing changes to __init__.py')
            with open(f'{app_name}/__init__.py', 'w') as version_file:
                version_file.write(f'__version__ = \'{release}\'\n')

        repo = git.Repo(os.getcwd())
        git_commit_release_message(repo, release, args.dry_run)
        git_tag_repo(repo, release, args.dry_run)
        git_push_all(repo, remote=None, dry_run=args.dry_run)


def get_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry-run', action='store_true', help='DO NOT make changes')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-j', '--major', action='store_true', help='Release Major Version')
    group.add_argument('-n', '--minor', action='store_true', help='Release Minor Version')
    group.add_argument('-p', '--patch', action='store_true', help='Release Patch Version')
    return parser


def git_commit_release_message(repo, version, dry_run=False):
    print('Commit release to git')
    commit_message = f'Publish v{version}'
    if not dry_run:
        repo.git.add(all=True)
        repo.git.commit('-m', commit_message)


def git_tag_repo(repo, version, dry_run=False):
    if not dry_run:
        repo.create_tag(f'v{version}', message=f"Released v{version}")


def git_push_all(repo, remote=None, dry_run=False):
    if not remote:
        print('Available git remotes')
        index = 1
        for rem in repo.remotes:
            print(f'{index} - {rem.name}')
            index = index + 1

        remote = int(input('Select remote to push: '))

        try:
            remote = repo.remotes[remote - 1].name
        except Exception as exc:
            print('Invalid Remote, setting remote to "upstream"')
            remote = 'upstream'

    git_ssh_command = os.environ.get('GIT_SSH_COMMAND')
    if git_ssh_command:
        repo.git.update_environment(GIT_SSH_COMMAND=git_ssh_command)

    if not dry_run:
        repo.git.push(remote, '--follow-tags')


if __name__ == "__main__":
    main()
