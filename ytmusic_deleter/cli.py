import io
import logging
import os
import sys
from pathlib import Path
from time import strftime

import click
import ytmusic_deleter.actions as actions
import ytmusicapi
from ytmusic_deleter.auth import do_auth
from ytmusic_deleter.progress import set_static_progress
from ytmusic_deleter.version import get_version
from ytmusicapi import YTMusic


def configure_logging(log_dir, no_logfile, verbose):
    logger = logging.getLogger()

    if logger.hasHandlers():
        return

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")

    if "PYTEST_CURRENT_TEST" in os.environ:
        stream = io.StringIO()
    else:
        stream = sys.stderr
    stream_handler = logging.StreamHandler(stream)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if not no_logfile:
        logger.addHandler(
            logging.FileHandler(
                Path(log_dir) / f"ytmusic-deleter-cli_{strftime('%Y-%m-%d')}.log",
                encoding="utf-8",
            )
        )


def main():
    cli()


@click.group()
@click.version_option(f"{get_version()}, ytmusicapi version: {ytmusicapi.__version__}")
@click.option(
    "--credential-dir",
    "-c",
    default=os.getcwd(),
    help="Custom directory in which to locate/create JSON credential file, instead of current working directory",
)
@click.option(
    "--static-progress",
    "-p",
    is_flag=True,
    help="Log the progress statically instead of an animated progress bar",
)
@click.option(
    "--log-dir",
    "-l",
    default=os.getcwd(),
    help="Custom directory in which to write log files, instead of current working directory.",
)
@click.option("--no-logfile", "-n", is_flag=True, help="Only log to stdout, no file logging")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose (debug) logging")
@click.option("--oauth", "-o", is_flag=True, help="Enable OAuth authentication")
@click.option("--client-id", "-y", help="Client ID (for OAuth)")
@click.option("--client-secret", "-z", help="Client secret (for OAuth)")
@click.pass_context
def cli(
    ctx: click.Context, log_dir, credential_dir, static_progress, no_logfile, verbose, oauth, client_id, client_secret
):
    """Perform batch delete operations on your YouTube Music library."""
    configure_logging(log_dir, no_logfile, verbose)
    set_static_progress(static_progress)

    if ctx.obj is not None:
        # Allows yt_auth to be provided by pytest
        yt_auth: YTMusic = ctx.obj
    else:
        yt_auth: YTMusic = do_auth(credential_dir, oauth, client_id, client_secret)
    ctx.ensure_object(dict)
    ctx.obj["STATIC_PROGRESS"] = static_progress
    ctx.obj["YT_AUTH"] = yt_auth


@cli.command()
def whoami():
    """Print the name of the authenticated user, or sign in"""
    pass


@cli.command()
@click.option(
    "--add-to-library",
    "-a",
    is_flag=True,
    help="Add the corresponding album to your library before deleting a song from uploads.",
)
@click.option(
    "--score-cutoff",
    "-s",
    default=90,
    help="When combined with the --add-to-library flag, this optional integer argument between 0 and 100 is used when finding matches in the YTM online catalog. No matches with a score less than this number will be added to your library. Defaults to 90.",  # noqa: B950
)
@click.pass_context
def delete_uploads(ctx: click.Context, add_to_library, score_cutoff):
    """Delete all songs that you have uploaded to your YT Music library."""
    context = actions.ActionContext(ctx.obj["YT_AUTH"], static_progress=ctx.obj["STATIC_PROGRESS"])
    return actions.delete_uploads(context, add_to_library=add_to_library, score_cutoff=score_cutoff)


@cli.command()
@click.pass_context
def remove_library(ctx: click.Context):
    """Remove all songs and podcasts that you have added to your library from within YouTube Music."""
    context = actions.ActionContext(ctx.obj["YT_AUTH"], static_progress=ctx.obj["STATIC_PROGRESS"])
    return actions.remove_library(context)


@cli.command()
@click.pass_context
def unlike_all(ctx: click.Context):
    """Reset all Thumbs Up ratings back to neutral"""
    context = actions.ActionContext(ctx.obj["YT_AUTH"], static_progress=ctx.obj["STATIC_PROGRESS"])
    return actions.unlike_all(context)


@cli.command()
@click.pass_context
def delete_playlists(ctx: click.Context):
    """Delete all playlists"""
    context = actions.ActionContext(ctx.obj["YT_AUTH"], static_progress=ctx.obj["STATIC_PROGRESS"])
    return actions.delete_playlists(context)


@cli.command()
@click.pass_context
def delete_history(ctx: click.Context, items_deleted: int = 0):
    """
    Delete your play history. This does not currently work with brand accounts.
    The API can only retrieve 200 history items at a time, so the process will appear to
    start over and repeat multiple times if necessary until all history is deleted.
    """
    context = actions.ActionContext(ctx.obj["YT_AUTH"], static_progress=ctx.obj["STATIC_PROGRESS"])
    return actions.delete_history(context, items_deleted=items_deleted)


@cli.command()
@click.pass_context
def delete_all(ctx: click.Context):
    """Executes delete-uploads, remove-library, delete-playlists, unlike-all, and delete-history"""
    context = actions.ActionContext(ctx.obj["YT_AUTH"], static_progress=ctx.obj["STATIC_PROGRESS"])
    return actions.delete_all(context)


@cli.command()
@click.argument("playlist_titles", nargs=-1, required=True)
@click.option("--shuffle", "-s", is_flag=True, help="Shuffle the playlist(s) instead of sorting.")
@click.option("--custom-sort", "-c", multiple=True, metavar="ATTRIBUTE", help="Enable custom sorting")
@click.option("--reverse", "-r", is_flag=True, help="Reverse the entire playlist after sorting")
@click.pass_context
def sort_playlist(ctx: click.Context, shuffle, playlist_titles, custom_sort, reverse):
    """Sort or shuffle one or more playlists alphabetically by artist and by album"""
    context = actions.ActionContext(ctx.obj["YT_AUTH"], static_progress=ctx.obj["STATIC_PROGRESS"])
    return actions.sort_playlist(context, shuffle, playlist_titles, custom_sort, reverse)


@cli.command()
@click.argument("playlist_title")
@click.option("--exact", "-e", is_flag=True, help="Only remove exact duplicates")
@click.option("--fuzzy", "-f", is_flag=True, help="Use fuzzy matching")
@click.option(
    "--score-cutoff",
    "-s",
    default=80,
    help="When combined with the --fuzzy flag, this optional integer argument between 0 and 100 is used when finding matches in the YTM online catalog. No matches with a score less than this number will be added to your library. Defaults to 90",  # noqa: B950
)
@click.pass_context
def remove_duplicates(ctx: click.Context, playlist_title, exact, fuzzy, score_cutoff):
    """Delete all duplicates in a given playlist"""
    context = actions.ActionContext(ctx.obj["YT_AUTH"], static_progress=ctx.obj["STATIC_PROGRESS"])
    return actions.remove_duplicates(context, playlist_title, exact, fuzzy, score_cutoff)


@cli.command
@click.argument("playlist_title")
@click.option("--library", "-l", is_flag=True, help="Add all library songs to a playlist")
@click.option("--uploads", "-u", is_flag=True, help="Add all uploaded songs to a playlist")
@click.pass_context
def add_all_to_playlist(ctx: click.Context, playlist_title, library, uploads):
    """Add all library songs or uploaded songs to a playlist."""
    context = actions.ActionContext(ctx.obj["YT_AUTH"], static_progress=ctx.obj["STATIC_PROGRESS"])
    return actions.add_all_to_playlist(context, playlist_title, library, uploads)


@cli.command
@click.argument("playlist_title_or_id")
@click.pass_context
def add_all_to_library(ctx: click.Context, playlist_title_or_id):
    """
    Add each individual song from a playlist to your YTMusic library.

    Supplied argument can be a playlist title from your own library,
    or a playlist ID of any playlist (e.g. PLTkvVIeIOLkXCnGpcx4QBnWliyGsMO8zC)
    """
    context = actions.ActionContext(ctx.obj["YT_AUTH"], static_progress=ctx.obj["STATIC_PROGRESS"])
    return actions.add_all_to_library(context, playlist_title_or_id)


if __name__ == "__main__":
    main()
