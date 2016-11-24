# Co-reference-Resolution
Co reference  resolution for NLP:

1. Create the virtual environment by running the requirements.txt

2. Run command "python -m spacy.en.download all" in bash to download the spacy dependency.

3. run shell script coreference.sh from current directory like:
        sh coreference.sh listfiles scorer/responses/
   Here, listfiles file contain the input file path
         scorer/responses/ is the location for the output, where *.response file
s will gets printed.

