from argparse import ArgumentParser
import os.path
from tempfile import mkdtemp
import webbrowser

from jinja2 import Environment, PackageLoader, select_autoescape

from camgi.contexts import IndexContext


def main():
    parser = ArgumentParser(description='investigate a must-gather for clues of autoscaler activity')
    parser.add_argument('path', help='path to the root of must-gather tree')
    parser.add_argument('--webbrowser', action='store_true', help='open a webbrowser to generated file')
    args = parser.parse_args()

    env = Environment(
        loader=PackageLoader('camgi', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('index.html')

    context = IndexContext(args.path)
    content = template.render(context.data)
    indexpath = os.path.join(mkdtemp(), 'index.html')
    indexfile = open(indexpath, 'w')
    indexfile.write(content)
    indexfile.close()

    url = f'file://{indexpath}'
    if args.webbrowser:
        webbrowser.open(url)
    print(f'{url}')


if __name__ == '__main__':
    main()
