import subprocess
import platform

from modules.upsidedown import flip


__author__ = flip('developers')

win_git_path = 'C:/Program Files (x86)/Git/cmd/git.exe'
major_version = 'α'


def get_git_commit_count(path_to_git='git'):
    return subprocess.check_output([path_to_git, 'rev-list', 'HEAD', '--count'])


def get_git_revision_hash(path_to_git='git'):
    return subprocess.check_output([path_to_git, 'rev-parse', 'HEAD'])


def get_git_revision_short_hash(path_to_git='git'):
    return subprocess.check_output([path_to_git, 'rev-parse', '--short', 'HEAD'])


def get_version(long_version=False):
    version_long = ''
    version_short = ''
    commit_count = ''
    try:
        version_short = get_git_revision_short_hash().decode("utf-8").strip()
        version_long = get_git_revision_hash().decode("utf-8").strip()
        commit_count = get_git_commit_count().decode("utf-8").strip()
    except WindowsError:
        version_short = get_git_revision_short_hash(win_git_path).decode("utf-8").strip()
        version_long = get_git_revision_hash(win_git_path).decode("utf-8").strip()
        commit_count = get_git_commit_count(win_git_path).decode("utf-8").strip()
    finally:
        if long_version:
            return '<' + major_version + ' r' + commit_count + '/' + 'git:' + version_long + '/' + platform.system() + '>'
        else:
            return '<' + major_version + ' r' + commit_count + '/' + 'git:' + version_short + '/' + platform.system() + '>'


def get_author():
    return __author__
