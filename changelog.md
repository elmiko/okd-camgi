# Changelog

## devel

* add machinesets to navigation tabs
* add current replicas to participating machinesets on summary

## 0.6.0

* improve directory detection and error reporting for must-gathers
* add a --tar flag to allow processing of tar files
* add a fix for ClusterAutoscaler with no defined resourceLimits

## 0.5.0

* title of index page always show the basename of the directory
* add a dockerfile and automated build for webserver deployment
* add decoded csr information to the csr data pages
* add machine config operator pods
* add a contributing doc
* convert index page to use vuejs for improved clarity and performance
* add nvidia.com/gpu allocatable/capacity to sumamry page

## 0.4.0

* add certificate signing requests to displayed resources
* clean up visual appearance of badges in nav list
* clean up memory can cpu display on summary

## 0.3.0

* add cluster alloctable memory and cpu to summary
* add cluster memory and cpu capacity to summary
* add cluster version to summary

## 0.2.1

* add error logging for failed yaml parses
* add verbose flag to enable debug output
* add current logs for all mapi container pods
