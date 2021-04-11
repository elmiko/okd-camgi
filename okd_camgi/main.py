from argparse import ArgumentParser
import os.path
from tempfile import mkdtemp
from threading import Thread
from time import sleep
import webbrowser

from bottle import route, run
from jinja2 import Environment, PackageLoader, select_autoescape

from okd_camgi.contexts import IndexContext
from okd_camgi.interfaces import MustGather


def load_index_from_path(path):
    env = Environment(
        loader=PackageLoader('okd_camgi', 'templates'),
        autoescape=False
    )

    mustgather = MustGather(path)

    # render the mustgather_data.js template
    # mustgather_data_template = env.get_template('mustgather_data.js')
    # mustgather_data_context = MustGatherDataContext(mustgather)
    # mustgather_data_content = mustgather_data_template.render(mustgather_data_context.data)

    # render the index.html template
    index_template = env.get_template('index.html')
    index_context = IndexContext(mustgather)
    index_content = index_template.render(index_context.data)

    return index_content


def main():
    parser = ArgumentParser(description='investigate a must-gather for clues of autoscaler activity')
    parser.add_argument('path', help='path to the root of must-gather tree')
    parser.add_argument('--webbrowser', action='store_true', help='open a webbrowser to investigation')
    parser.add_argument('--server', action='store_true', help='run in server mode')
    args = parser.parse_args()

    content = load_index_from_path(args.path)
    indexpath = os.path.join(mkdtemp(), 'index.html')
    indexfile = open(indexpath, 'w')
    indexfile.write(content)
    indexfile.close()

    host = '127.0.0.1'
    port = 8080
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
            content = load_index_from_path(args.path)
            return content

        run(host=host, port=port, debug=True)

    if bth is not None:
        bth.join()


if __name__ == '__main__':
    main()
