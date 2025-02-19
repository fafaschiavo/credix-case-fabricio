# Credix Case Project

This project is a monorepo containing a frontend application built with React and Vite, and a backend API built with Django. The deployment infrastructure is managed via Terraform and deployed on AWS using services like S3, CloudFront, ECR, Fargate, and RDS (PostgreSQL).

## Setup and Running Locally

- **Environment File:** Create a `.env` file in the root of the project with the required environment variables. You can use the .env.sample file as a reference.
- **Start the Project:**
  - If you have `make` installed, run: `make start`
  - Otherwise, run: `docker compose up --build`

## Main Dependencies

### Frontend

- [React](https://reactjs.org/)
- [React Compiler](https://reactjs.org/docs/react-api.html)  
  *(This refers to the modern build tooling that optimizes and compiles React code, ensuring deprecated patterns such as `useMemo` or `useCallback` are managed properly.)*
- [Vite](https://vitejs.dev/)
- [React Router](https://reactrouter.com/)
- [Axios](https://axios-http.com/)
- [MUI](https://mui.com/)

### Backend

- [Django](https://www.djangoproject.com/)

## Deploy

- **AWS Credentials:** Ensure you export your AWS keys (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`) in your environment.
- **Prepare Infrastructure:** Run `make prepare-infra` to create the AWS infrastructure using Terraform.
- **Push Backend:** Run `make push-back` to build and push the Django image to ECR and deploy it on Fargate.
- **Push Frontend:** Run `make push-front` to build the frontend application and sync it to the S3 bucket.

## Infrastructure Overview

- **S3:** Hosts the static files of the frontend application.  
  ([AWS S3](https://aws.amazon.com/s3/))
- **CloudFront:** Serves the content via a global CDN.  
  ([AWS CloudFront](https://aws.amazon.com/cloudfront/))
- **ECR:** Stores the Docker images for the backend.  
  ([AWS ECR](https://aws.amazon.com/ecr/))
- **Fargate:** Runs the backend containers without managing servers.  
  ([AWS Fargate](https://aws.amazon.com/fargate/))
- **RDS - PostgreSQL:** Managed PostgreSQL database.  
  ([AWS RDS for PostgreSQL](https://aws.amazon.com/rds/postgresql/))

## Todo

- **Storybook:** For developing and documenting UI components.  
  ([Storybook](https://storybook.js.org/))
- **Pipelines:** Set up CI/CD pipelines for automated testing and deployment.  
  ([GitHub Actions](https://github.com/features/actions) or [GitLab CI/CD](https://www.gitlab.com/))
- **End-to-End Tests:** Use Cypress for e2e testing.  
  ([Cypress](https://www.cypress.io/))
- **Unit Tests:** Write unit tests for both frontend and backend components.  
  ([Jest](https://jestjs.io/) and [Pytest](https://docs.pytest.org/en/stable/))

## Additional Notes

The project is organized as a monorepo with two main folders: `back` for the Django API and `front` for the Vite+React application. The `terraform` folder contains all the Terraform configuration files to deploy the infrastructure on AWS.