# Conversational Aerospace NLP Model

## Project summary

### One-sentence description of the project

This project aims to create an internal Boeing ChatGPT, a conversational AI system, the gives Boeing stakeholders the ability to effortlessly summarize and comprehend large, complex technical documents.

### Additional information about the project

The Boeing NLP model will be your personal tool to navigate pilot operating handbooks, domain-specific documents, and much more. Within just a few keystrokes, you will be able to turn that 20-50 page document into a few paragraphs.

Our goal is to successfully create an NLP model that can accurately and efficiently summarize these documents to increase productivity of Boeing employees. A user should be able to input a PDF or Word document to have it be summarized by our program. We will also implement ChatGPT internally as your personal AI co-pilot to navigate these complex documents with you. This program is your key to unlocking unlimited aerospace knowledge, increasing productivity, and expanding innovation at Boeing.

## Installation

### Prerequisites

1. Github
2. Python 3


### Add-ons

1. SpaCy: Used as our Natural Language Processor (NLP)
2. Fitz: Used to handle PDF documents
3. RE: Used to handle Regular Expressions
4. Tkinter: Used to traverse file paths
5. BERT Summarizer: Used to assist in summarizing large documents after parsed
6. Flask: Used to create web application
7. OpenAI: Used to create instance of AI Chatbot

### Installation Steps

```
pip install -r requirements.txt
```
```
python -m spacy download en_core_web_sm
```
```
python -m spacy download en_core_web_md
```
```
python -m spacy download en_core_web_lg
```

## Functionality

'cd' into `./app` and run `python app.py` (for web app) OR `python main.py` (basic command line)

See 'Startup Guide' for instructions (to be implemented)


## Known Problems

OpenAI API can only accept a set amount of tokens per request. We must split the text up into chunks using LangChain.


## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Additional Documentation

  * [Sprint 1 Report](https://github.com/WSUCptSCapstone-F23-S24/boeing-nlp-ai/blob/main/documentation/Sprint1/Sprint_Report_1.md)
  * [Sprint 1 Video](https://github.com/WSUCptSCapstone-F23-S24/boeing-nlp-ai/blob/main/documentation/Sprint1/README.md)
  * [Sprint 2 Report](https://github.com/WSUCptSCapstone-F23-S24/boeing-nlp-ai/blob/main/documentation/Sprint2/Sprint_Report_2.md)
  * [Sprint 2 Video](https://github.com/WSUCptSCapstone-F23-S24/boeing-nlp-ai/blob/main/documentation/Sprint2/README.md)
  * [Sprint 3 Report](https://github.com/WSUCptSCapstone-F23-S24/boeing-nlp-ai/blob/main/documentation/Sprint3/Sprint_Report_3.md)
  * [Sprint 3 Video](https://github.com/WSUCptSCapstone-F23-S24/boeing-nlp-ai/blob/main/documentation/Sprint3/README.md)
  * [Sprint 4 Report](https://github.com/WSUCptSCapstone-F23-S24/boeing-nlp-ai/blob/main/documentation/Sprint4/Sprint_Report_4.md)
  * [Sprint 4 Video](https://github.com/WSUCptSCapstone-F23-S24/boeing-nlp-ai/blob/main/documentation/Sprint4/README.md)
  * [Sprint 5 Report](https://github.com/WSUCptSCapstone-F23-S24/boeing-nlp-ai/blob/main/documentation/Sprint5/Sprint_Report_5.md)
  * [Sprint 5 Video](https://github.com/WSUCptSCapstone-F23-S24/boeing-nlp-ai/blob/main/documentation/Sprint5/README.md)
  * [Sprint 6 Report](https://github.com/WSUCptSCapstone-F23-S24/boeing-nlp-ai/blob/main/documentation/Sprint6/Sprint_Report_6.md)
  * [Sprint 6 Video](https://github.com/WSUCptSCapstone-F23-S24/boeing-nlp-ai/blob/main/documentation/Sprint6/README.md)

## License

If you haven't already, add a file called `LICENSE.txt` with the text of the appropriate license.
We recommend using the MIT license: <https://choosealicense.com/licenses/mit/>

## Resources

  * 2022-2023 Capstone Team Video - NLP Model: <https://vimeo.com/822183770?share=copy>
  * 2021-2022 Capstone Team Video - Automated Taxonomies: <https://vimeo.com/705006982>
  * 2021-2022 Capstone Team Project GitHub Repo: <https://github.com/WSUCptSCapstone-Fall2021Spring2022/boeing-naturallanguageprocessing>
  * 2020-2021 Capstone Team Video - Semantic Vocabulary Extraction: <https://vimeo.com/522696857>
  * 2020-2021 Capstone Team Project GitLab Repo: <https://gitlab.com/alorphan/pilot-operating-handbook-text-analysis>
