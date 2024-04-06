"""
Class for executing different phases
"""

import pandas as pd
import numpy as np
import os
from evcouplings.utils.config import read_config_file, write_config_file
from evcouplings.utils.pipeline import execute
import multiprocessing


def run_aligning(
    monomer_config: dict,
) -> None:
    config = read_config_file(monomer_config, preserve_order=True)
    execute(**config)


def run_couplings(config_filename: str) -> None:
    # run config
    config = read_config_file(config_filename, preserve_order=True)
    execute(**config)


class EVStages:
    def __init__(
        self,
        output_dir: str,
        infile: str,
        monomer_config: str,
        complex_config: str,
        bit_scores: list,
        threads: int,
    ) -> None:
        self.infile = infile
        self.output_dir = output_dir
        self.monomer_config = monomer_config
        self.complex_config = complex_config
        self.bit_scores = bit_scores
        self.threads = threads

    def aligning(self) -> None:
        # get protein info
        PPIs = pd.read_csv(self.infile)
        # rename second PPIs for concat
        PPIs_tmp = PPIs[["uid2", "r_start_2", "r_end_2"]]
        PPIs_tmp.columns = ["uid1", "r_start_1", "r_end_1"]
        proteins = pd.concat(
            [PPIs[["uid1", "r_start_1", "r_end_1"]], PPIs_tmp]
        ).drop_duplicates()
        proteins.columns = ["uid", "r_start", "r_end"]
        # check output dir
        if not os.path.exists("/evcomplex/align"):
            os.makedirs("/evcomplex/align")

        with multiprocessing.Pool(self.threads) as pool:
            for _, row in proteins.iterrows():
                for bit in self.bit_scores:
                    # writing single config file
                    config = read_config_file(self.monomer_config, preserve_order=True)
                    config["stages"] = ["align"]
                    config["global"]["sequence_id"] = row.uid
                    config["global"]["region"] = [row.r_start, row.r_end]
                    config["global"]["prefix"] = "{3}/{0}_{1}-{2}_b{4}".format(
                        row.uid, row.r_start, row.r_end, self.output_dir + "align", bit
                    )
                    config["align"]["domain_threshold"] = bit
                    config["align"]["sequence_threshold"] = bit
                    config["align"]["reuse_alignment"] = False
                    config_file = f"{self.output_dir}align/{row.uid}_b{bit}.txt"
                    write_config_file(config_file, config)
                    # submitting alignment
                    # execute(**config)
                    pool.apply(
                        run_aligning,
                        args=[config_file],
                    )

    def couplings(self) -> None:
        def _fill_missing_information_infile(PPIs: pd.DataFrame) -> pd.DataFrame:
            use = []
            values = []
            # for each protein pair
            for _, line in PPIs.iterrows():
                line_values = []
                for alignment in [1, 2]:
                    # alignment file
                    file = f'{line[f"uid{alignment}"]}_{line[f"r_start_{alignment}"]}-{line[f"r_end_{alignment}"]}_'
                    # for each bit score
                    for bit in self.bit_scores:
                        dir = (
                            self.output_dir
                            + "align/"
                            + file
                            + f"b{bit}"
                            + "/align/"
                            + file
                            + f"b{bit}"
                            + ".a2m"
                        )
                        if os.path.isfile(dir):
                            line_values.append(bit)
                            line_values.append(dir)
                            break
                # check if any alignments are missing
                if len(line_values) == 4:
                    use.append(True)
                    values.append(line_values)
                else:
                    use.append(False)
                    print(f'Alignments {line["uid1"]}, {line["uid2"]} failed')
            PPIs = PPIs[use]
            # fill columns
            PPIs["bit1"] = list(map(lambda x: x[0], values))
            PPIs["aln1"] = list(map(lambda x: x[1], values))
            PPIs["bit2"] = list(map(lambda x: x[2], values))
            PPIs["aln2"] = list(map(lambda x: x[3], values))
            # save additional information
            PPIs.to_csv(self.infile.replace(".csv", "_used.csv"))
            return PPIs

        def _make_config(row: pd.Series) -> dict:
            config = read_config_file(self.complex_config, preserve_order=True)
            config["global"]["prefix"] = (
                self.output_dir
                + "couplings/"
                + f"{row.uid1}__{row.uid2}_{row.bit1}-{row.bit2}"
            )
            # TODO rename config with known input
            # alignment 1
            config["align_1"]["sequence_id"] = row.uid1
            config["align_1"]["domain_threshold"] = float(row.bit1)
            config["align_1"]["sequence_threshold"] = float(row.bit1)
            config["align_1"]["region"] = [int(row.r_start_1), int(row.r_end_1)]
            config["align_1"]["first_index"] = int(row.r_start_1)
            config["align_1"]["input_alignment"] = row.aln1
            config["align_1"]["override_annotation_file"] = row.aln1.replace(
                ".a2m", "_annotation.csv"
            )
            # alignment 2
            config["align_2"]["sequence_id"] = row.uid2
            config["align_2"]["domain_threshold"] = float(row.bit2)
            config["align_2"]["sequence_threshold"] = float(row.bit2)
            config["align_2"]["region"] = [int(row.r_start_2), int(row.r_end_2)]
            config["align_2"]["first_index"] = int(row.r_start_2)
            config["align_2"]["input_alignment"] = row.aln2
            config["align_2"]["override_annotation_file"] = row.aln2.replace(
                ".a2m", "_annotation.csv"
            )
            # quick and dirty alignment size calculation
            if "couplings" in config["stages"]:
                L = (
                    int(row.r_end_1)
                    - int(row.r_start_1)
                    + int(row.r_end_2)
                    - int(row.r_start_2)
                )
                q = 20
                memory_in_MB = (1 / 2 * q**2 * (L - 1) * L + q * L) / 12500
                memory_in_MB = max(500, memory_in_MB)
                config["environment"]["memory"] = int(memory_in_MB)  # maybe remove
            # config["compare"]["plot_model_cutoffs"] = [
            #     float(x) for x in config["compare"]["plot_model_cutoffs"]
            # ]
            return config

        PPIs = pd.read_csv(self.infile)

        # fill infile details
        if not (os.path.exists(PPIs["aln1"][0]) and os.path.exists(PPIs["aln2"][0])):
            PPIs = _fill_missing_information_infile(PPIs)
        # check for output path
        if not os.path.exists("/evcomplex/couplings"):
            os.makedirs("/evcomplex/couplings")

        with multiprocessing.Pool(self.threads) as pool:
            for _, line in PPIs.iterrows():
                # write config
                config = _make_config(line)
                config_filename = self.output_dir + f"couplings/{line.prefix}.txt"
                # print(config["compare"]["plot_model_cutoffs"])
                write_config_file(config_filename, config)
                # run couplings
                pool.apply(run_couplings, args=[config_filename])
