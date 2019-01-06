# Blindr
This script was created by Justus Huebotter and Sarantos Tzortzis as part of the Knowledge Engineering course at the Vrije Universiteit Amsterdam.

The requirements to run this script are Python 3.5+ with several site packages of the Anaconda distribution.
To obtain this script run in a terminal:
```
git clone https://github.com/jhuebotter/Blindr.git
```
To run the script run in a terminal:
```
python Blindr/scr/blindr.py
```

## Background Information
This script will read in a list of animals (IDs & features) from a csv or excel document and automatially assign them to a given number of groups while preserving group size and animal feature similarity, to be used in experimental setups. It shall decrease the general experimental design / preparation workload, the need of a second scientist for manual animal assignment as well as improve the quality of experimental group similarity. Thereby, we hope to contribute towards less bias in scientific research and tackle one of the various key problems towards more reproducibility. 

## Input requirements
For now, the accepted input is .csv, .xls and .xlsx. The first line of the table shall contain a description of the presented data, so a caption for the data in this column. The first three columns are used for information about the animals, one of which needs to be labeled as "ID". Every column to follow the first three will be seen as either a numerical or categorical feature to equally distribute across the experimental groups. An example for this structure is given in this repository as example_data.xlsx.
