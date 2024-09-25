# A wishing gifts website
## Design
Attached in `Diagrm.pptx`.

## AliExpressScrapper package
### Description
A package to scrape products' data from AliExpress website.

### Instructions
1. Build the docker file: `docker build -t aliexpressscrapper .`.
2. Run the docker and get shell: `docker run -it aliexpressscrapper /bin/bash`.
3. Copy the file `scrapper.py` to the docker container: `docker cp scarpper.py <container_id>:/app/` from current shell (not the docker container shell).
4. Run the script from inside the container.
