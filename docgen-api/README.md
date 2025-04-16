# SCAFFOLD-API

A scaffold Python flask API application to be used as a template.

## Getting Started

### Development Environment
* Install the following:
    - [Python](https://www.python.org/)
    - [Docker](https://www.docker.com/)
    - [Docker-Compose](https://docs.docker.com/compose/install/)
* Install Dependencies
    - Run `make setup` in the root of the project (scaffold-api)
* Start the databases
    - Run `docker-compose up` in the root of the project (scaffold-api)

## Environment Variables

The development scripts for this application allow customization via an environment file in the root directory called `.env`. See an example of the environment variables that can be overridden in `sample.env`.

## Commands

### Development

The following commands support various development scenarios and needs.
Before running the following commands run `. venv/bin/activate` to enter into the virtual env.


> `make run`
>
> Runs the python application and runs database migrations.  
Open [http://localhost:5000/api](http://localhost:5000/api) to view it in the browser.<br/>
> The page will reload if you make edits.<br/>
> You will also see any lint errors in the console.

> `make test`
>
> Runs the application unit tests<br>

> `make lint`
>
> Lints the application code.

## Debugging in the Editor

### Visual Studio Code

Ensure the latest version of [VS Code](https://code.visualstudio.com) is installed.

The [`launch.json`](.vscode/launch.json) is already configured with a launch task (SCAFFOLD-API Launch) that allows you to launch chrome in a debugging capacity and debug through code within the editor.

## Usage
You can use the /templates api endpoint to create or register a template in the backend. The template_key and app determines the uniqueness.
You can create template create request with the html content of the template. Make sure you escape all the double quotes while sending the html content.
DocGen-API uses jinja2 for template creation and weasyprint for pdf generation. When you create html template using jinja2 format, make sure it adhers to the rules of weasyprint library for better pdf generation experience.

DocGen-API produces either html or pdf output as of now. You can use the /templates/render endpoint to create the output in the format you want. Refer the swagger doc for more detailed api usage
You can find a sample template and its output pdf in the example folder