# idn-homograph-generator

The **idn_homograph_generator** is a Python script used to generate homographs of Internationalized Domain Names (IDNs) to perform homograph attacks. A write-up covering the concept of this script can be found at my blog at [intothethickof.it](https://intothethickof.it/2023/08/15/generating-and-detecting-phishing-domains-with-idn-homograph-attacks).

The script uses a mapping of Unicode characters that are *visually-similar* to Latin letters to generate possible IDNs that can be used to impersonate traditional domains which only contain Latin letters.

Some use-cases include:
- Raising awareness on homograph attacks
- Generating phishing domains for internal phishing exercises
- Generating IDN homographs for your company/brand to register before bad actors do


## Requirements

1. The script was developed in Python 3.10.5 and requires the ``` idna ``` library which can be installed using pip:

```
pip install idna
```

2. The script takes in as input a dictionary file (.txt file) which contains a mapping of Latin letters to visually-similar Unicode characters in their Hex values. The contents  of the dictionary file should look like this:

```
a|0251|03B1|0430|203|...
b|13CF|1472|15AF|...
c|1D04|2CA5|0441|1043D|188|107...
.
.
.
x|0445|1541|157D|1E8D|3C7|...
y|0263|028F|03B3|0443|04AF|...
z|1D22|17A|17C|1E95|17E|...
```

The contents of the dictionary can be adjusted depending on what is *visually-similar* to you. The mapping will affect the output of the script and the amount of time/resources to complete the script as it will increase/decrease the number of possible IDN homographs.

## Usage

To run the script:

```
python idn_homograph_generator.py <dictionary_file> <domain> [lazy/intensive]
```

**WARNING! RUNNING THE SCRIPT IN INTENSIVE MODE WILL CONSUME SIGNIFICANT AMOUNTS OF RAM.**

By default, the program runs in **lazy** mode to generate IDN homographs, which is slower than the **intensive mode** but consumes a **significantly** lesser amount of RAM. To use the **intensive** mode, add the **intensive** switch at the end of the command. For example:

```
python idn_homograph_generator.py <dictionary_file> <domain> intensive
```

The script will output the IDN homographs by printing the results to your console and saving them to a text file named after the domain provided. For example, by running:

```
python idn_homograph_generator.py dictionary.txt github
```

The console will look like this:

The results of the script will be saved to **github.txt** and look like this:


## Disclaimer

**THIS SCRIPT IS FOR EDUCATIONAL AND INFORMATIONAL PURPOSES ONLY. THE SCRIPT WILL UTILIZE SIGNIFICANT RESOURCES WHEN RUN IN INTENSIVE MODE. THE AUTHOR DOES NOT TAKE RESPONSIBILITY FOR ANY MISUSE, LOSS, OR DAMAGE CAUSED BY THE USE OF THIS SCRIPT.**

