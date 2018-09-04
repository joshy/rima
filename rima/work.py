def key(entry):
    pid = entry["patient_id"]
    accession_nr = entry["accession_number"]
    series_nr = entry["series_number"]
    return pid + "_" + accession_nr + "_" + series_nr
