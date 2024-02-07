#!/bin/bash
cd /DB/
wget https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz
gunzip uniprot_sprot.fasta.gz
wget https://marks.hms.harvard.edu/evcomplex_databases/cds_pro_2017_02.txt
wget https://marks.hms.harvard.edu/evcomplex_databases/idmapping_uniprot_embl_2017_02.txt 