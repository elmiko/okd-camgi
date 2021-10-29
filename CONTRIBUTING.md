# Contributing

In general this project follows the standard pattern for making contributions,
namely:

1. fork this repo
2. make a feature branch
3. commit your changes to the feature branch
4. propose feature branch as a pull request

## Code structure

The code is organized into 2 primary modules: `contexts` and `interfaces`.

The `interfaces` module contains code that translates the on-disk files into
in-memory representations. This is the place to add new interactions with data
from the must-gather.

The `contexts` module contains code that adapts a interface data into variables
that can be used within the templates. This is the place to control how data
is injected from the on-disk format to a template so that it can be rendered
in the browser.

The `okd_camgi/templates` directory contains the HTML template that is used
to render the final output.
