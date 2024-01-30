FROM mcr.microsoft.com/devcontainers/miniconda:3

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
# plmc | maybe bash scirps ?
RUN wget https://github.com/debbiemarkslab/plmc/archive/refs/heads/master.zip -O plmc.zip
RUN unzip plmc.zip -d plmc
RUN rm plmc.zip
WORKDIR /plmc/plmc-master
RUN make all-openmp32
WORKDIR /
# jackhmmer | maybe bash scripts ?
RUN wget http://eddylab.org/software/hmmer/hmmer-3.4.tar.gz -O hmmer.tar.gz
RUN gunzip hmmer.tar.gz
RUN tar -xf hmmer.tar
RUN rm hmmer.tar
WORKDIR /hmmer-3.4
RUN ./configure
RUN make
RUN make check
RUN make install

# Databases TODO clean up
WORKDIR /DB/
RUN wget https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz
RUN gunzip uniprot_sprot.fasta.gz
RUN wget https://marks.hms.harvard.edu/evcomplex_databases/cds_pro_2017_02.txt
RUN wget https://marks.hms.harvard.edu/evcomplex_databases/idmapping_uniprot_embl_2017_02.txt 
# Config files
COPY ./config/complex_config.txt /config/
COPY ./config/monomer_config_all.txt /config/

# run bash script for running python file with input file
COPY ./main.py /config/
CMD [ "python", "/config/main.py" ]
