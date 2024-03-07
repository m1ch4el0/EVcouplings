"""
Class for executing different phases
"""

import pandas as pd
import numpy as np
import os
from evcouplings.utils.config import read_config_file, write_config_file
import multiprocessing


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
        self.complex_config = monomer_config
        self.bit_scores = bit_scores
        self.threads = threads

    def __check_threads(self, config_path: str) -> int:
        if self.threads % 2 == 0:
            config = read_config_file(config_path)
            config["global"]["cpu"] = 2
            write_config_file(config, config_path)
            return self.threads / 2
        return self.threads

    def aligning(self) -> None:
        def _run_aligning(uid: str, r_start: int, r_end: int) -> None:
            os.system(
                "evcouplings -p {0} -r {1}-{2} -b {5} --yolo --prefix {3}/{0}_{1}-{2} {4}".format(
                    uid,
                    r_start,
                    r_end,
                    self.output_dir + "align/",
                    self.monomer_config,
                    '"' + ",".join(self.bit_scores) + '"',
                )
            )
            print(
                "evcouplings -p {0} -r {1}-{2} -b {5} --yolo --prefix {3}/{0}_{1}-{2} monomer_config_all".format(
                    uid,
                    r_start,
                    r_end,
                    self.output_dir + "align/",
                    self.monomer_config,
                    '"' + ",".join(self.bit_scores) + '"',
                )
            )

        # get protein info
        PPIs = pd.read_csv(self.infile)
        proteins = pd.concat(
            PPIs["uid1", "r_start_1", "r_end_1"], PPIs["uid1", "r_start_1", "r_end_1"]
        ).drop_duplicates()
        proteins.columns = ["uid", "r_start", "r_end"]

        with multiprocessing.Pool(self.__check_threads(self.monomer_config)) as pool:
            for _, row in proteins.iterrows():
                pool.apply_async(_run_aligning, args=[row.uid, row.r_start, row.r_end])

    def couplings(self) -> None:
        def _make_config(row: pd.Series) -> dict:
            config = read_config_file(self.complex_config, preserve_order=True)
            config["global"]["prefix"] = (
                "output/couplings/" + f"{row.uid1}__{row.uid2}_{row.bit1}-{row.bit2}"
            )
            # TODO rename config with known input
            # alignment 1
            config["align_1"]["sequence_id"] = row.uid1
            config["align_1"]["domain_threshold"] = float(row.bit1)
            config["align_1"]["sequence_threshold"] = float(row.bit1)
            config["align_1"]["region"] = [int(row.r_start_1), int(row.r_end_1)]
            config["align_1"]["first_index"] = int(row.r_start_1)
            config["align_1"]["input_alignment"] = (
                "output/align" + f"{row.uid1}_{row.r_start_1}-{row.r_end_1}.a2m"
            )
            config["align_1"]["override_annotation_file"] = (
                "output/align"
                + f"{row.uid1}_{row.r_start_1}-{row.r_end_1}_annotation.csv"
            )
            # alignment 2
            config["align_2"]["sequence_id"] = row.uid2
            config["align_2"]["domain_threshold"] = float(row.bit2)
            config["align_2"]["sequence_threshold"] = float(row.bit2)
            config["align_2"]["region"] = [int(row.r_start_2), int(row.r_end_2)]
            config["align_2"]["first_index"] = int(row.r_start_2)
            config["align_2"]["input_alignment"] = (
                "output/align" + f"{row.uid2}_{row.r_start_2}-{row.r_end_2}.a2m"
            )
            config["align_2"]["override_annotation_file"] = (
                "output/align"
                + f"{row.uid2}_{row.r_start_2}-{row.r_end_2}_annotation.csv"
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

        def _run_couplings(config_filename: str) -> None:
            # run config
            os.system(f"evcouplings --yolo {config_filename}")
            print(f"finished {config_filename}")

        PPIs = pd.read_csv(self.infile)

        with multiprocessing.Pool(self.__check_threads(self.complex_config)) as pool:
            for _, line in PPIs.iterrows():
                # write config
                config = _make_config()
                config_filename = f"output/{line.prefix}.txt"
                # print(config["compare"]["plot_model_cutoffs"])
                write_config_file(config, config_filename)
                # run couplings
                pool.apply_async(_run_couplings, args=config_filename)
