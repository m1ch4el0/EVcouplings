FROM mcr.microsoft.com/devcontainers/miniconda:0-3

# Set environment variable to noninteractive
ENV DEBIAN_FRONTEND noninteractive

# Copy the environment.yml file to the /tmp/conda-tmp directory in the image
COPY ./environment.yml /tmp/conda-tmp/
# Run the command to update the Conda environment
RUN if [ -f "/tmp/conda-tmp/environment.yml" ]; then /opt/conda/bin/conda env update -n base -f /tmp/conda-tmp/environment.yml; fi \
    && rm -rf /tmp/conda-tmp
# Install anaconda
RUN conda install anaconda
# Install EVcomplex sql
RUN pip install https://github.com/m1ch4el0/EVcouplings/archive/refs/heads/inter_species_sql.zip


# tools
# plmc 
WORKDIR /home/
RUN wget https://github.com/debbiemarkslab/plmc/archive/refs/heads/master.zip -O plmc.zip
RUN unzip plmc.zip -d plmc
RUN rm plmc.zip
WORKDIR /home/plmc/plmc-master
RUN make all-openmp32
WORKDIR /
# jackhmmer 
WORKDIR /home/
RUN wget http://eddylab.org/software/hmmer/hmmer-3.4.tar.gz -O hmmer.tar.gz
RUN gunzip hmmer.tar.gz
RUN tar -xf hmmer.tar
RUN rm hmmer.tar
WORKDIR /home/hmmer-3.4
RUN ./configure
RUN make
RUN make check
RUN make install

# Databases 
COPY ./scripts/download_db.sh /home/utils/
RUN chmod +rwx /home/utils/download_db.sh
RUN mkdir /home/DB
RUN bash /home/utils/download_db.sh

# Install tini
RUN apt-get update && apt-get install -y tini
# required
RUN sudo apt install libtiff5 -y

# Config files
COPY ./config/complex_config.txt /home/utils/
COPY ./config/monomer_config_all.txt /home/utils/

# copying docker backend and frontend
COPY ./scripts/main_ui.py /home/utils/
RUN chmod +rwx /home/utils/main_ui.py
COPY ./scripts/main_batch.py /home/utils/
RUN chmod +rwx /home/utils/main_batch.py
COPY ./scripts/stages.py /home/utils/
RUN chmod +rwx /home/utils/stages.py
COPY ./entrypoint.sh /home/utils/
RUN chmod +x /home/utils/entrypoint.sh
# running service entrypoint
CMD ["/home/utils/entrypoint.sh"]
 