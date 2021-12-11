from argparse import ArgumentParser
import logging
import os.path
import pathlib
from shutil import unpack_archive
import sys
from tempfile import mkdtemp
import webbrowser

from bottle import request, route, run, Response
from jinja2 import Environment, PackageLoader
import requests

import okd_camgi
from okd_camgi.contexts import IndexContext
from okd_camgi.interfaces import MustGather


def extract_tar(path):
    extraction_path = mkdtemp(prefix="okd_camgi")
    logging.info(f"Trying to unpack mg archive {path} into {extraction_path}")
    try:
        unpack_archive(path, extract_dir=extraction_path)
    except Exception as ex:
        logging.debug(ex)
        return None
    return extraction_path


def find_must_gather_root(path):
    # attempt to determine if the path given is a valid must-gather
    # we do this by looking for a few files which should be present.
    # the rules are as follows:
    # 1. look for a `version` file in the current path, if it exists return path
    # 2. look for the directories `namespaces` and `cluster-scoped-resources` in the current path, if they exist return path
    # 3. look to see if there is a single subdirectory in the path, if so run this function on that path and return the result
    # 4. return None
    if os.path.exists(os.path.join(path, 'version')):
        return path
    if os.path.isdir(os.path.join(path, 'namespaces')) and os.path.isdir(os.path.join(path, 'cluster-scoped-resources')):
        return path

    pathfiles = [d for d in pathlib.Path(path).iterdir() if d.is_dir()]
    if len(pathfiles) == 1:
        return find_must_gather_root(str(pathfiles[0]))

    return None


def http_error(status, message, optional=None):
    context = {
        'status_code': status,
        'message': message,
        'optional': optional,
    }
    return render_template('error.html', context)


def load_index_from_path(path):
    env = Environment(
        loader=PackageLoader('okd_camgi', 'templates'),
        autoescape=False
    )

    mustgather = MustGather(path)
    index_context = IndexContext(mustgather)
    return render_template('index.html', index_context.data)


def render_template(template, context):
    env = Environment(
        loader=PackageLoader('okd_camgi', 'templates'),
        autoescape=False
    )
    tmpl = env.get_template(template)
    return tmpl.render(context)


def run_server(args):
    @route('/')
    def handler():
        url = request.query.url
        logging.debug(f'url={url}')
        if not url:
            logging.error('No url specified in request query parameters')
            return Response(body=http_error(400, 'Error, no url supplied.', 'Add <pre>?url=http://path/to/must-gather.tar.gz'), status=400)

        try:
            req = requests.get(url)
            if req.status_code != 200:
                msg = f'Error downloading requests url {url}'
                logging.error(msg)
                logging.debug(req.content)
                return Response(body=http_error(req.status_code, msg, req.content), status=req.status_code)

            tarpath = os.path.join(mkdtemp(), url.split('/')[-1])
            with open(tarpath, "wb") as outfile:
                outfile.write(req.content)
            path = extract_tar(tarpath)
            if path is None:
                return Reponse(body=http_error(500, 'Error extracting must-gather archive'), status=500)

            path = find_must_gather_root(path)
            return load_index_from_path(path)
        except Exception as ex:
            return Response(body=http_error(500, 'Unexpected server error', str(ex)), status=500)


    run(host=args.host, port=args.port, debug=True)


def main():
    parser = ArgumentParser(prog='okd-camgi', description='investigate a must-gather for clues of autoscaler activity')
    parser.add_argument('path', help='path to the root of must-gather tree', nargs='?', default=None)
    parser.add_argument('--tar', action='store_true', help='open a must-gather archive in tar format')
    parser.add_argument('--webbrowser', action='store_true', help='open a webbrowser to investigation')
    parser.add_argument('--server', action='store_true', help='run in server mode, path will be ignored')
    parser.add_argument('--host', help='server host address', default='127.0.0.1')
    parser.add_argument('--port', help='server host port', default='8080')
    parser.add_argument('--output', help='output filename')
    parser.add_argument('--version', action='version', version=f'%(prog)s {okd_camgi.version}')
    parser.add_argument('--verbose', action='store_true', help='enable verbose logging')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if args.server:
        run_server(args)
        sys.exit(0)

    if args.path is None:
        logging.error('No path specified, and not running in server mode. Please check usage by running `okd-camgi --help`')
        sys.exit(1)
    path = os.path.abspath(args.path)

    if args.tar:
        extraction_path = extract_tar(path)
        if extraction_path is None:
            logging.error(f'Error extracting tar file {path}')
            sys.exit(1)

        path = find_must_gather_root(extraction_path)

    path = find_must_gather_root(path)
    if path is not None:
        logging.info(f'Found valid must-gather in {os.path.abspath(args.path)}')
        content = load_index_from_path(path)
    else:
        logging.error(f'"{os.path.abspath(args.path)}" does not appear to be a valid must-gather archive')
        sys.exit(1)

    if args.output or not args.server:
        indexpath = args.output if args.output else os.path.join(mkdtemp(), 'index.html')
        with open(indexpath, 'w') as indexfile:
            indexfile.write(content)

    host = args.host
    port = int(args.port)
    url = f'file://{indexpath}' if not args.server else f'http://{host}:{port}/'
    print(f'{url}')

    if args.webbrowser:
        webbrowser.open(url)


if __name__ == '__main__':
    main()
