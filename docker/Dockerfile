FROM mcr.microsoft.com/devcontainers/miniconda:3

# Copy the environment.yml file to the /tmp/conda-tmp directory in the image
COPY environment.yml /tmp/conda-tmp/
# Run the command to update the Conda environment
RUN if [ -f "/tmp/conda-tmp/environment.yml" ]; then /opt/conda/bin/conda env update -n base -f /tmp/conda-tmp/environment.yml; fi \
    && rm -rf /tmp/conda-tmp
# Install anaconda
RUN conda install anaconda
# Install EVcomplex sql
RUN pip install https://github.com/m1ch4el0/EVcouplings/archive/refs/heads/inter_species_sql.zip

# tools
# plmc
RUN wget https://github.com/debbiemarkslab/plmc/archive/refs/heads/master.zip -O plmc.zip
RUN unzip plmc.zip -d plmc
RUN rm plmc.zip
WORKDIR /plmc/plmc-master
RUN make all-openmp32
WORKDIR /
# jackhmmer
RUN wget http://eddylab.org/software/hmmer/hmmer-3.4.tar.gz -O hmmer.tar.gz
RUN gunzip hmmer.tar.gz
RUN tar -xf hmmer.tar
RUN rm hmmer.tar
WORKDIR /hmmer-3.4
RUN ./configure
RUN make
RUN make check
RUN make install
