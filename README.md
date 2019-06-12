# Blindr
This script was created by Justus Huebotter and Sarantos Tzortzis as part of the Knowledge Engineering course at the Vrije Universiteit Amsterdam.

To obtain this script run in a terminal:
```
git clone https://github.com/jhuebotter/Blindr.git
```

The requirements to run this script are Python 3.5+ with several site packages of e.g. the Anaconda distribution. To install these please run:
```
pip install -r Blindr/requirements.txt
```

To run the script run in a terminal:
```
python Blindr/src/blindr.py
```

## Background Information
This script will read in a list of animals (IDs & features) from a csv or excel document and automatially assign them to a given number of groups while preserving group size and animal feature similarity, to be used in experimental setups. Otherwise, the repeated measure option will generate an experimental setup for wich each animal is tested a given number of times. Here, on each experimental session every group is roughly equally represented and sequential group pairs occur equally often. This tool shall decrease the general experimental design / preparation workload, the need of a second scientist for manual animal assignment as well as improve the quality of experimental group similarity. Thereby, we hope to contribute towards less bias in scientific research and tackle one of the various key problems towards more reproducibility. However, this is a work-in-progress and not all desired functionality is yet implemented. Any comments and questions are most welcome.

## Input requirements
Ihe accepted input formats are .csv, .xls and .xlsx. The first line of the table shall contain a description of the presented data, so a caption for the data in the respective column (header). A columns shall contain an unique identifier (ID) for each subject. At least one other column shall contain information about the animals as either a numerical or categorical feature to be equally distributed across the experimental groups. An example for this structure is given in this repository as example_data.xlsx and example_data.csv. The output will be saved in a new folder and have the same filetype as the input.

## Future improvements
- Step-by-step wizard with explainations on the presented choices.
- More flexible repreated measures options, such as a differentiation between groups to create and available test days.
- Progress bar to show that the script is running in the background.
- Dataset summary and visualization of selected features before the script is executed.

