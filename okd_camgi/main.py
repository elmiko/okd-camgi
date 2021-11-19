from argparse import ArgumentParser
import logging
import os.path
import pathlib
from shutil import unpack_archive
import sys
from tempfile import mkdtemp, TemporaryDirectory
from threading import Thread
from time import sleep
import webbrowser

from bottle import route, run
from jinja2 import Environment, PackageLoader

import okd_camgi
from okd_camgi.contexts import IndexContext
from okd_camgi.interfaces import MustGather


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


def load_index_from_path(path):
    env = Environment(
        loader=PackageLoader('okd_camgi', 'templates'),
        autoescape=False
    )

    mustgather = MustGather(path)

    # render the index.html template
    index_template = env.get_template('index.html')
    index_context = IndexContext(mustgather)
    index_content = index_template.render(index_context.data)

    return index_content


def main():
    parser = ArgumentParser(prog='okd-camgi', description='investigate a must-gather for clues of autoscaler activity')
    parser.add_argument('path', help='path to the root of must-gather tree')
    parser.add_argument('--tar', action='store_true', help='open a must-gather archive in tar format')
    parser.add_argument('--webbrowser', action='store_true', help='open a webbrowser to investigation')
    parser.add_argument('--server', action='store_true', help='run in server mode')
    parser.add_argument('--host', help='server host address', default='127.0.0.1')
    parser.add_argument('--port', help='server host port', default='8080')
    parser.add_argument('--output', help='output filename')
    parser.add_argument('--version', action='version', version=f'%(prog)s {okd_camgi.version}')
    parser.add_argument('--verbose', action='store_true', help='enable verbose logging')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    path = os.path.abspath(args.path)

    if args.tar:
        extraction_path = TemporaryDirectory(prefix="okd_camgi")
        logging.info(f"Trying to unpack mg archive {path} into {extraction_path.name}")
        unpack_archive(path, extract_dir=extraction_path.name)
        extracted_mg_content_path = next(filter(lambda x: os.path.isdir(x), os.scandir(extraction_path.name)))
        extracted_mg_content_path = extracted_mg_content_path.path if extracted_mg_content_path else None

        if extracted_mg_content_path:
            logging.info(f"Found mg root in {extracted_mg_content_path}")
        else:
            logging.info(f"No extra dirs was not found in unpacked archive, using {extraction_path}")

        path = extracted_mg_content_path or extraction_path

    path = find_must_gather_root(path)
    if path is not None:
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

    bth = None
    if args.webbrowser:
        # delay opening the browser in case we are running in server mode
        def delay_browser_open():
            sleep(1)
            webbrowser.open(url)

        bth = Thread(target=delay_browser_open)
        bth.start()

    if args.server:
        @route('/')
        def handler():
            content = load_index_from_path(path)
            return content

        run(host=host, port=port, debug=True)

    if bth is not None:
        bth.join()


if __name__ == '__main__':
    main()
