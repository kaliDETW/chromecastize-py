#!/usr/bin/python3

import argparse
import datetime
import subprocess
import sys
import os
from subprocess import check_output

SUPPORTED_EXTENSIONS = 'mkv', 'avi', 'mp4', '3gp', 'mov', 'mpg', 'mpeg', 'qt', 'wmv', 'm2ts', 'rmvb', 'rm', 'rv', \
                       'ogm', 'flv', 'asf'
SUPPORTED_VIDEO_CODECS = ('AVC')
SUPPORTED_AUDIO_CODECS = ('AAC' 'MPEG Audio' 'Vorbis' 'Ogg' 'VorbisVorbis')

DEFAULT_VCODEC = "h264"
DEFAULT_ACODEC = "libvorbis"
DEFAULT_GFORMAT = "mkv"


def _check_path():
    """
    Checks the path for ffmpeg and mediainfo. If not found, try to add one placed in the same folder as this module.
    If that did not work, exit

    :return:
    """
    if sys.platform == 'win32':
        sep = ';'
    else:
        sep = ':'

    if _which("ffmpeg") == None:
        _add_program_to_path("ffmpeg/bin/")
    if _which("mediainfo") == None:
        _add_program_to_path("mediainfo/")


def _add_program_to_path(programpath):
    """
    Tries to add a program to the path

    :param programpath:
    :return:
    """
    if sys.platform == 'win32':
        sep = ';'
    else:
        sep = ':'

    if os.path.exists(programpath):
        abs_programpath = os.path.abspath(programpath)
        os.environ['PATH'] += sep + r'' + abs_programpath + ''
    else:
        print("Tried to add " + programpath + " to the path but path could not be found.")
        sys.exit(-1)


def start_transcoding_process(path):
    """
    wrapper that checks if we are processing a file or directory, redirect as appropriate, set the ffmpeg settings
    and then execute the transcoding process if necessary.

    :param path:
    :return:
    """
    if os.path.isfile(path):  # process a file
        params = _set_ffmpeg_params(path)
        _do_ffmpeg_transcoding(path, params)
    elif os.path.isdir(path):  # process a directory
        for file in os.listdir(path):
            print("processing '%s'.." % file)
            filepath = os.path.join(path, file)
            params = _set_ffmpeg_params(filepath)
            _do_ffmpeg_transcoding(filepath, params)
    else:  # It's something else
        print("Invalid input, it is neither a file nor a directory or does not exist! Thus, exiting.")
        sys.exit(-1)


def _which(program):
    """
    checks if a program exists on the path

    :param program:
    :return:
    """

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    print("Could not find %s on path. Install %s or set the path and try again" % (program, program))
    return None


def _set_ffmpeg_params(filepath):
    """
    Checks the file meta data and sets the ffmpeg parameters accordingly

    :param filepath: absolute path to file
    :return: array of parameters
    """
    if _is_supported_file_ending(filepath):
        subs_param = _set_subs_param(filepath)
        vcodec_param = _set_vcodec_param(filepath)
        acodec_param = _set_acodec_param(filepath)
        return {"subs": subs_param, "video": vcodec_param, "audio": acodec_param}
    else:
        print("This file type is not supported. Thus, skipping '%s'." % filepath)
        return None


def _is_supported_file_ending(filepath):
    """
    checks if the file extension is supported

    :param filepath:
    :return: True or False
    """
    global SUPPORTED_EXTENSIONS

    if filepath.lower().endswith(tuple(SUPPORTED_EXTENSIONS)):
        return True
    else:
        return False


def _execute_mediainfo(param, filepath):
    try:
        s = check_output(['mediainfo', param, filepath])  # Gets the output from mediainfo
        s1 = s[:-1]  # Removes the second line from output
        name = s1.decode("utf-8")  # s1 is a bytes object but we need a string for the check
        return name
    except OSError as e:  # Some error happened
        if e.errno == os.errno.ENOENT:  # mediainfo is not installed
            print("Could not find mediainfo on path. Install mediainfo or set the path and try again")
            sys.exit(-1)
        else:  # Something else went wrong
            raise


def _set_subs_param(filepath):
    """
    Checks if an external subtitle file exists sets the ffmpeg param to add or merge, depending on if subs already
    exist in the container

    :param filepath:
    :return:
    """
    # TODO add subtitle logic
    return "copy"


def _set_vcodec_param(filepath):
    """
    Checks if the video codec is supported

    :param filepath:
    :return: ffmpeg encoding parameter for the video setting
    """
    global DEFAULT_VCODEC
    global SUPPORTED_VIDEO_CODECS

    name = _execute_mediainfo('--Inform=Video;%Format%', filepath)
    print("Video codec: {}".format(name))
    if name.lower() in SUPPORTED_VIDEO_CODECS.lower():  # Is the video codec supported?
        print("Video codec is compatible, setting video param to 'copy'")
        return "copy"
    else:
        print("Video codec is not compatible, setting transcode parameter to %s." % DEFAULT_VCODEC)
        return DEFAULT_VCODEC


def _set_acodec_param(filepath):
    """
    Checks if the audio codec is supported

    :param filepath: absolute path to file
    :return: ffmpeg encoding parameter for the audio setting
    """
    global DEFAULT_ACODEC
    global SUPPORTED_AUDIO_CODECS

    name = _execute_mediainfo('--Inform=Audio;%Format%', filepath)
    print("Audio codec: {}".format(name))
    if name in SUPPORTED_AUDIO_CODECS:  # Is the audio codec supported by the fire stick?
        print("Audio codec is compatible, setting video param to 'copy'")
        return "copy"
    else:
        print("Audio codec is not compatible, setting transcode parameter to %s." % DEFAULT_ACODEC)
        return DEFAULT_ACODEC


def _do_ffmpeg_transcoding(filepath, params):
    """
    Uses the ffmpeg encoder with the passed parameters

    :param filepath: absolute path to file
    :param params: An array containing the ffmpeg params
    :return:
    """
    if (params == None):
        print("{}: Could not recognize valid parameters, thus skipping the file. \n".format(filepath))
    if all(value == "copy" for value in params.values()):  # check if all values in the dict are 'copy'
        print("{}: File is already playable on a chromecast or fire tv stick, thus skipping it. \n".format(filepath))
    else:
        print("{}: Transcoding file. \n".format(filepath))
        # filepath = os.path.splitext(filepath)[0]  # This removes the filepath extension from the name

        bakname = filepath + ".bak"

        # outputFile = shlex.quote(str(os.path.abspath(filepath)))
        # sourceFile = shlex.quote(str(os.path.abspath(bakname)))

        outputFile = _quote(os.path.abspath(filepath))
        sourceFile = _quote(os.path.abspath(bakname))

        # New output is always matroska container because I want to add subtitle support at some point
        finalFile = outputFile + ".mkv"

        # putting together the ffmpeg command
        command = "ffmpeg -loglevel error -stats " \
                  "-i {srcFile} -map 0 " \
                  "-scodec {subs} " \
                  "-vcodec {video} " \
                  "-acodec {audio} " \
                  "{finFile}".format(srcFile=sourceFile,
                                     subs=str(params["subs"]),
                                     video=str(params["video"]),
                                     audio=str(params["audio"]),
                                     finFile=finalFile)

        # File needs to be renamed so it's not overwritten)
        os.rename(filepath, bakname)

        print("executing " + command)
        subprocess.call(command, shell=True)

        print("%s has successfully been transcoded \n" % filepath)


def _quote(s):
    """
    TODO
    this is a poor workaround for non-working shlex.quote on windows (?). Will be fixed

    :param s:
    :return:
    """
    # TODO fix this, use proper shlex.quote
    if os.name == 'nt':
        return "\"" + s.replace("'", "'\"'\"'") + "\""
    else:
        return "'" + s.replace("'", "'\"'\"'") + "'"


def main():
    """
    Command line main to start the transcoding process.

    Accepts a file or directory as input param and will skip already chromecast or fire TV stick compatible files.

    :return: transcoded video file in mkv format
    """

    # save start timestamp
    start_time = datetime.datetime.now()

    # Describe a parser for command-line options
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='filename or directory to transcode')

    # Parse all the command-line options, automatically checks for required params
    args = parser.parse_args()

    # start the transcoding process
    _check_path()
    print("Starting transcoding process..")
    start_transcoding_process(args.input)

    # finish, print time needed for execution
    print("## Total transcoding duration {duration}".format(duration=(datetime.datetime.now() - start_time)))


if __name__ == "__main__":
    main()
