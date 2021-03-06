# Fccr3_DA

This is part of a larger project. The tentative full name of this project is FreeCodeCamp (fCC) Community Resources Review. Although it borrows the name from fCC as source of inspiration and origin, this project is NOT currently in direct connection with the organization (www.freecodecamp.org).

## Description

The project mission is to offer users, in principle new developers, a curated list of relevant resources to learn programming.

This project is a Proof of Concept.

This section includes the code for the data mining and the application of machine learning techniques for classifying the gathered resources (`platforms`) - online content mentioned by fCC social media users.

The main sources from where the data is being currently extracted are fCC chatrooms.

The scripts in this section are used to:
* collect the resources from the chatrooms
* extract information about its use in the chatrooms
* add information about the collected platforms visiting their main pages (a bot)
* an effort to assign `categories` by exploring machine learning techniques
* collect and organize information about the `subjects` fCC curriculum (https://beta.freecodecamp.com/en/map)
* information retrieval: assign weights for ranking based on similarity of platform-specific content with fCC subjects keywords
* generate tests
* solve some ETL issues
* save data into Firebase

This project is being managed using Kanban methodology (https://realtimeboard.com/blog/choose-between-agile-lean-scrum-kanban/#.WW5nlh9Nybk). This repository of the project shows the advances of the data mining and machine learning work. There exists another repository to shows some of the advances in the rendering of the project (in Angular).

## Installation

This repository and its content is still under construction and it is not ready for downloads.

However we can mention that:
* it is run under *UNIX-like operating system (Ubuntu 16.04)*
* Python 3.5.2, IPython 4.2.0, both in Anaconda 4.1.1

For privacy reasons the project won't include:
* local directories
* critical access information (databases, API's); some of the API's are public and the code can be replicated if you get an API for the corresponding platform; access to database is restricted: only reading is public

## Related projects

For more information about the associated advances in rendering of this project, please visit this repository: https://github.com/evaristoc/fCC_R3 (work-in-progress)
