# EVcomplex (dockerized)
The folder *docker* containerizes *EVcomplex*.

## Building the first image
The docker image can be built using the Dockerfile

- *docker build -t ev:\<tag> -f Dockerfile*

Afterward, the image should be specified in the *docker-compose.yml*.

## Defining the input

Further, the output directory, the input file, and optionally a config file need to be specified. Examples can be found in the following directories:

- input PPIs: *docker/config/infile_example.csv*
- config file (optional): *docker/config/custom_config_docker.yaml*

Instructions on how to specify directories are described inside the _docker-compose.yml_.

## Running application
The image can now be run using docker-compose

- docker-compose run --rm app

## Additional information
Information on how the pipeline works can be found in the main documentation.
