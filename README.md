Project: Jax_GeneWeaver Backend GeneUses
Backend development on the Gene Weaver project for Jackson Laboratories.
In this project we are creating a prototype where we move the gene set tools 
on GeneWeaver to an Asynchronous Task Service. Decoupling the tool implementations
from the GeneWeaver database. These tools are implemented with just the input
and the GeneWeaver ReST API interface as end points. 

Developers:
Anushka Ashishkumar Doshi
Daniel Hayes
Harshit Khattar
Kishan Lakshman

Running the Project:

First the repository must be cloned onto your local machine.
Then inside the repository start a virtual python environment

### Package Management
- **Poetry**: Dependency management and packaging
  - Installation: `pip install poetry`
  - Initialize: `poetry install --with dev,docs,test,build`
  - Virtual Environment: `poetry shell`

With this you should be able to run the tests in the project as well as the FastAPI interface for the project.

Completed Tools:

- MSET comparison
Ran with gene set files or gene IDs
- Boolean Algebra
For same species genes.

Appendix: (Documents, etc.)

[Software Requirements Specification](https://docs.google.com/document/d/1CuAEDM0lB_aLkWd-7UbAVl1-4FK-Bd3kylNvMyXkAls/edit?tab=t.0)

[Software Design Document (Initial Version) ](https://docs.google.com/document/d/1iV7gFUhqc2Z5BtbLYyuZjCIfEyceMhUscrIj2UMRTug/edit?tab=t.0)

[Software Testing Document - Planning Version](https://docs.google.com/document/d/1Lk9_93cKM9bXzYuGziVMOhecGJTzI2oFd0pS3NMt780/edit?usp=sharing)
